"""Describe a manual with Gemini: read its page images in one request and
write manuals/<name>/page_states.json and diagram_analysis.json, the same
files a hand-written describe.py produces.

Usage (from the repo root, GEMINI_API_KEY in .env):
    python v2/agents/gemini_describer.py NAME            # manuals/NAME/pages/
    python v2/agents/gemini_describer.py path/to.pdf [--name NAME]
    python v2/agents/gemini_describer.py NAME --force    # ask Gemini again

Gemini's answer is kept as manuals/<name>/gemini_description.json and reused
on later runs, so re-running the pipeline costs no requests. GEMINI_MODELS in
.env lists the models to try, comma-separated; the free tier is often
overloaded (503), so each overloaded model hands over to the next.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Literal, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel, Field

from config import MANUALS_DIR
from manual_description import action, diagram, fastener, page, part, tool, write_description
from utils.image_budget import fit
from utils.pdf_to_images import add_manual

DEFAULT_MODELS = "gemini-3.8-flash,gemini-3.7-flash,gemini-flash-latest"
RAW_FILE = "gemini_description.json"
# Pauses between rounds through the models while all are overloaded (503).
OVERLOAD_RETRY_SECONDS = (15, 45)
SKILL_FILE = PROJECT_ROOT / ".claude" / "skills" / "describe-manual" / "SKILL.md"


class Feature(BaseModel):
    type: Literal["hole", "slot", "connector", "groove", "notch"]
    count: int
    location: str


class Part(BaseModel):
    label: str = Field(description="Number or code printed next to the part, or empty")
    name: str = Field(description="Full name using the role words, e.g. 'left side frame', 'front rail'")
    description: str
    shape_family: Literal["beam", "panel", "frame", "bracket", "cylinder", "block"]
    material: Literal["wood", "metal", "plastic", "fabric", "glass", "other"]
    quantity: int = Field(description="Copies drawn on this page (1 for a close-up standing for all)")
    features: List[Feature]
    position: Literal["left", "right", "center", "top", "bottom"]
    size_mm: List[float] = Field(description="[width, depth, height] in mm as the part sits in the finished piece; "
                                             "estimate from the drawings when no size is printed; [] if unsure")
    tilt_deg: float = Field(description="Degrees the fitted part leans back (a reclined back); 0 if upright or flat")
    profile_path: List[List[float]] = Field(description="Outline of a curved or bent part as [u, v] mm points "
                                                        "(side view: y front to back, z up); [] for straight parts")
    profile_plane: Literal["side", "front", "top"] = Field(description="View the outline is traced in")
    profile_closed: bool = Field(description="True when the outline is a filled shape (an upholstered body's side), "
                                             "false when it is a strip (a bentwood frame)")
    profile_thickness: float = Field(description="Strip thickness in mm for an open outline; 0 when closed or no outline")


class Fastener(BaseModel):
    label: str = Field(description="Part number or letter printed next to it, or empty")
    name: str
    shape_family: Literal["dowel", "bolt", "screw", "nut", "washer", "cam", "plug", "bracket", "other"]
    quantity: int


class Action(BaseModel):
    type: Literal["attach", "insert", "tighten", "place", "slide"]
    moving_part: str = Field(description="Name of the part that moves; empty when only a fastener goes in")
    target_part: str = Field(description="Name of the part it goes onto or into")
    fastener: str = Field(description="Label (or name) of a fastener listed on this page, or empty")
    tool: str = Field(description="Name of a tool listed on this page, or empty")
    direction: Literal["down", "up", "inward", "outward", "clockwise", "left", "right", "unknown"]
    evidence: str = Field(description="What the picture shows, naming every part in full; include 'Repeat xN' if printed")


class Diagram(BaseModel):
    type: Literal["final_product", "warning", "part_inventory", "exploded_view", "assembly_view"]
    description: str = Field(description="For a parts-list part with a printed size: 'Name (A x B mm) xN'")
    region: List[float] = Field(description="x0, y0, x1, y1 as fractions of the page")
    labels: List[str]
    has_parts: bool
    has_fasteners: bool
    has_tools: bool
    has_arrows: bool
    action: Literal["attach", "insert", "tighten", "place", "slide", "warning", "none"]


class Page(BaseModel):
    number: int
    type: Literal["cover", "warning", "parts_list", "assembly_step", "unknown"]
    parts: List[Part]
    fasteners: List[Fastener]
    tools: List[str]
    actions: List[Action]
    final_structure: str
    uncertainties: List[str]
    diagrams: List[Diagram]


class Manual(BaseModel):
    product: str
    pages: List[Page]


def describe_rules() -> str:
    """The naming, quantity and size rules from the describe-manual skill,
    so Gemini follows the same rules as a hand-written description."""
    text = SKILL_FILE.read_text(encoding="utf-8")
    return text[text.index("## Naming parts"):]


PROMPT = """You are reading every page of a furniture assembly manual, in order, to describe it for a program that animates the assembly. Return one entry per page.

For each page list the parts, fasteners and tools drawn on it, the assembly actions its pictures show (one per distinct join), what the piece looks like after the page, and anything unclear. Wooden parts often have no printed label: name them by what they are. Use the same name for the same part on every page. Every fastener and tool an action names must be listed on that page. Diagram regions are fractions of the page (0-1).

The program places parts by the role words in their names and builds the video from these rules (they mention helper functions; the fields of your answer correspond to them):

"""


def page_images(manual_dir: Path) -> List[Image.Image]:
    pages = sorted((manual_dir / "pages").glob("page_*.png"), key=lambda p: int(re.search(r"\d+", p.stem).group()))
    if not pages:
        sys.exit(f"No pages in {manual_dir / 'pages'}. Run utils/pdf_to_images.py first.")
    return [fit(Image.open(p).convert("RGB")) for p in pages]


def ask_gemini(images: List[Image.Image]) -> dict:
    from google import genai
    from google.genai import errors, types

    load_dotenv(PROJECT_ROOT / ".env")
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set. Add it to .env (free key: aistudio.google.com).")
    models = [m.strip() for m in os.environ.get("GEMINI_MODELS", DEFAULT_MODELS).split(",") if m.strip()]

    contents = []
    for n, image in enumerate(images, start=1):
        contents += [f"Page {n}:", image]
    # The client closes its connection once garbage-collected, so keep it
    # referenced for the whole request.
    client = genai.Client(api_key=key)
    config = types.GenerateContentConfig(
        system_instruction=PROMPT + describe_rules(),
        response_mime_type="application/json",
        response_schema=Manual,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    response = None
    limited = set()
    for pause in (*OVERLOAD_RETRY_SECONDS, None):
        for model in [m for m in models if m not in limited]:
            try:
                response = client.models.generate_content(model=model, contents=contents, config=config)
                break
            except errors.APIError as e:
                # Overload and free-tier quotas are per model: try the next.
                if e.code in (429, 503):
                    print(f"{model} is {'over its free-tier limit' if e.code == 429 else 'overloaded'}")
                    if e.code == 429:
                        limited.add(model)
                    continue
                sys.exit(f"Gemini request failed ({e.code}, {model}): {e.message}")
        if response is not None:
            break
        if pause is None or len(limited) == len(models):
            sys.exit("Every Gemini model is overloaded or over its free-tier limit. Try again later.")
        print(f"Retrying in {pause} s")
        time.sleep(pause)

    if response.parsed is None:
        sys.exit(f"Gemini returned no usable description (finish reason: {response.candidates[0].finish_reason}).")
    usage = response.usage_metadata
    print(f"{model}: {usage.prompt_token_count} input + {usage.candidates_token_count} output tokens")
    return response.parsed.model_dump()


def outline(part_answer: dict) -> Optional[dict]:
    """The traced outline of a part, in describe.py's profile form."""
    path = [list(p)[:2] for p in part_answer.get("profile_path") or [] if len(p) >= 2]
    if len(path) < 2:
        return None
    profile = {"path": path, "plane": part_answer.get("profile_plane") or "side"}
    if part_answer.get("profile_closed"):
        profile["closed"] = True
    else:
        profile["thickness"] = part_answer.get("profile_thickness") or 30
    return profile


def to_description(manual: dict) -> tuple:
    """Gemini's answer as the pages and diagrams write_description takes."""
    pages, diagrams = [], {}
    for p in manual["pages"]:
        pages.append(page(
            p["number"], p["type"],
            parts=[part(x["label"], x["name"], x["description"], x["shape_family"], x["material"], x["quantity"],
                        [(f["type"], f["count"], f["location"]) for f in x["features"]], x["position"],
                        size=x.get("size_mm") if len(x.get("size_mm") or []) == 3 else None,
                        tilt=x.get("tilt_deg") or 0.0, profile=outline(x))
                   for x in p["parts"]],
            fasteners=[fastener(f["label"], f["name"], f["shape_family"], f["quantity"]) for f in p["fasteners"]],
            tools=[tool(t) for t in p["tools"]],
            actions=[action(a["type"], a["moving_part"], a["target_part"], a["fastener"], a["tool"],
                            a["direction"], a["evidence"]) for a in p["actions"]],
            final=p["final_structure"], unc=p["uncertainties"],
        ))
        diagrams[p["number"]] = (p["type"], [
            diagram(d["type"], d["description"], tuple((list(d["region"]) + [0, 0, 1, 1])[:4]), d["labels"],
                    parts=d["has_parts"], fast=d["has_fasteners"], tools=d["has_tools"],
                    arrows=d["has_arrows"], action_=d["action"])
            for d in p["diagrams"]
        ], [])
    return pages, diagrams


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("manual", help="Manual name under manuals/, or a path to a PDF.")
    parser.add_argument("--name", default="", help="With a PDF: the manual's folder name.")
    parser.add_argument("--force", action="store_true", help=f"Ask Gemini again even if {RAW_FILE} exists.")
    args = parser.parse_args()

    source = Path(args.manual)
    manual_dir = add_manual(source, args.name) if source.suffix.lower() == ".pdf" else MANUALS_DIR / args.manual
    raw_path = manual_dir / RAW_FILE

    if raw_path.exists() and not args.force:
        print(f"Using the saved answer in {raw_path} (--force to ask again)")
        manual = json.loads(raw_path.read_text(encoding="utf-8"))
    else:
        manual = ask_gemini(page_images(manual_dir))
        raw_path.write_text(json.dumps(manual, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    pages, diagrams = to_description(manual)
    write_description(manual_dir, pages, diagrams)
    print(f"Described {manual['product']!r}: next, python v2/run_mvp_pipeline.py {manual_dir.name}")


if __name__ == "__main__":
    main()
