"""Pick the finished videos the website shows. For each one this builds
showcase/<name>/ (committed, so the deployed site has it):
    video.mp4     a copy of outputs/videos/<name>.mp4
    pages/NN.jpg  the manual's pages, small enough for the web
    poster.jpg    the finished piece, for the product's card
    data.json     the steps (time in the video, caption, manual pages, parts)
                  and the parts list, so the site can turn the manual's pages
                  and tick off parts as the video plays. Only what the manual
                  and video show: no ids or pipeline internals, since the
                  site is public and the pipeline is not
showcase/showcase.json lists them in page order.

Usage (from the repo root):
    python utils/showcase.py list
    python utils/showcase.py add NAME [NAME ...] [--title "IKEA MELLTORP table"]
    python utils/showcase.py remove NAME
    python utils/showcase.py up NAME        # move one place earlier on the page

`add` re-runs the pipeline up to the Blender script (--no-render, a few
seconds, no Blender) to get the video's step timings, and warns when they
don't match the video's length, i.e. the video was rendered with older code
and the steps would be out of sync; re-render it and add it again. The title
defaults to the manual's product title (manuals/NAME/product.json).
Re-adding a name rebuilds it and keeps its place.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import fitz
from PIL import Image

from config import (
    MANUALS_DIR,
    MOTION_PLAN_JSON,
    RENDER_TIMELINE_JSON,
    SHOWCASE_DIR,
    SHOWCASE_JSON,
    UNIVERSAL_GRAPH_JSON,
    VIDEOS_DIR,
    product_title,
)

PAGE_WIDTH = 900
PAGE_QUALITY = 70
POSTER_WIDTH = 640
# Allowed difference between the video's length and the timeline's.
SYNC_TOLERANCE_SECONDS = 0.2


def load() -> list:
    """The showcase entries in page order: [{"name", "title"}, ...]."""
    try:
        return json.loads(SHOWCASE_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def save(entries: list):
    SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)
    SHOWCASE_JSON.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_pages(manual_dir: Path, out_dir: Path) -> list:
    """The manual's pages as JPEGs PAGE_WIDTH wide, from manual.pdf or else
    the rendered pages/; returns their file names in page order."""
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)

    images = []
    pdf = manual_dir / "manual.pdf"
    if pdf.exists():
        with fitz.open(pdf) as doc:
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(PAGE_WIDTH / page.rect.width, PAGE_WIDTH / page.rect.width))
                images.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    else:
        pngs = sorted((manual_dir / "pages").glob("page_*.png"), key=lambda p: int(p.stem.split("_")[1]))
        for png in pngs:
            image = Image.open(png).convert("RGB")
            images.append(image.resize((PAGE_WIDTH, round(image.height * PAGE_WIDTH / image.width))))

    names = []
    for i, image in enumerate(images, 1):
        names.append(f"{i:02d}.jpg")
        image.save(out_dir / names[-1], quality=PAGE_QUALITY, optimize=True)
    return names


def video_seconds(video: Path) -> float:
    from moviepy import VideoFileClip

    with VideoFileClip(str(video)) as clip:
        return clip.duration


def base_name(name: str) -> str:
    """A part's name without its instance number: "side rail 1/2" -> "side rail"."""
    return re.sub(r"\s+\d+/\d+$", "", name).strip()


def public_data(title: str, duration: float, pages: list, steps: list, nodes: list, edges: list) -> dict:
    """What the website gets: only what the manual and the video show (titles,
    captions, page numbers, part names and counts), nothing about how the
    pipeline works inside. steps carry the ids of the joints made in them;
    nodes are {"id", "name", "kind": "part"|"fastener", "quantity"} and
    edges {"id", "from", "to"}."""
    parts, index_of, count = [], {}, {}
    for node in nodes:
        name = base_name(node["name"])
        key = (node["kind"], name.lower())
        if key not in index_of:
            index_of[key] = len(parts)
            parts.append({"name": name, "hardware": node["kind"] == "fastener", "quantity": 0})
        part = parts[index_of[key]]
        part["quantity"] += node.get("quantity", 1) if node["kind"] == "fastener" else 1
    part_of = {n["id"]: index_of[(n["kind"], base_name(n["name"]).lower())] for n in nodes}
    joints = {e["id"]: (e["from"], e["to"]) for e in edges}

    return {
        "title": title,
        "duration": duration,
        "pages": pages,
        "parts": parts,
        "steps": [
            {
                "start": step["start"],
                "end": step["end"],
                "label": step["label"],
                "caption": step["caption"],
                "pages": step["pages"],
                "parts": sorted({
                    part_of[node] for joint in step["connections"] if joint in joints
                    for node in joints[joint] if node in part_of
                }),
            }
            for step in steps
        ],
    }


def build_data(title: str, pages: list, video: Path) -> tuple:
    """The site's data.json for the pipeline run just made, and whether the
    video matches its step timings."""
    timeline = read_json(RENDER_TIMELINE_JSON)
    plan = {s["step_uid"]: s for s in read_json(MOTION_PLAN_JSON)["steps"]}
    graph = read_json(UNIVERSAL_GRAPH_JSON)
    fps = timeline["fps"]

    def seconds(frame):
        return round((frame - 1) / fps, 2)

    # Each caption is one step of the video (consecutive steps doing the same
    # thing are merged into one caption); the motion steps inside it give
    # its manual pages and joints.
    steps = []
    for caption in timeline["captions"]:
        inside = [
            plan[s["step_uid"]] for s in timeline["steps"]
            if s["step_uid"] in plan
            and s["start_frame"] < caption["end_frame"] and s["end_frame"] > caption["start_frame"]
        ]
        steps.append({
            "start": seconds(caption["start_frame"]),
            "end": seconds(caption["end_frame"]),
            "label": caption["label"],
            "caption": caption["text"],
            "pages": sorted({s["source_page"] for s in inside if s.get("source_page")}),
            "connections": sorted({c for s in inside for c in s.get("connection_refs", [])}),
        })

    nodes = [
        {"id": p["part_uid"], "name": p["canonical_name"], "kind": "part"}
        for p in graph["parts"]
    ] + [
        {"id": f["fastener_uid"], "name": f["name"], "kind": "fastener", "quantity": f.get("quantity_total", 1)}
        for f in graph["fasteners"]
    ]
    edges = [
        {"id": c["connection_uid"], "from": c["from_node_ref"], "to": c["to_node_ref"]}
        for c in graph["connections"]
    ]

    duration = round(video_seconds(video), 2)
    in_sync = abs(duration - timeline["frame_end"] / fps) <= SYNC_TOLERANCE_SECONDS
    return public_data(title, duration, pages, steps, nodes, edges), in_sync


def write_poster(video: Path, out: Path):
    """The finished piece (the video's last second) as the card image."""
    from moviepy import VideoFileClip

    with VideoFileClip(str(video)) as clip:
        frame = Image.fromarray(clip.get_frame(max(clip.duration - 0.5, 0)))
    frame.thumbnail((POSTER_WIDTH, POSTER_WIDTH))
    frame.save(out, quality=PAGE_QUALITY, optimize=True)


def add(name: str, title: str = ""):
    manual_dir = MANUALS_DIR / name
    video = VIDEOS_DIR / f"{name}.mp4"
    if not video.exists():
        sys.exit(f"No video at {video}. Run: python v2/run_mvp_pipeline.py {name}")

    run = subprocess.run(
        [sys.executable, "v2/run_mvp_pipeline.py", name, "--no-render", "--quiet"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if run.returncode != 0:
        sys.exit(f"The pipeline failed for {name}:\n{run.stdout[-2000:]}{run.stderr[-2000:]}")

    out = SHOWCASE_DIR / name
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, out / "video.mp4")
    pages = write_pages(manual_dir, out / "pages")
    data, in_sync = build_data(title or product_title(manual_dir), pages, out / "video.mp4")
    (out / "data.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    write_poster(out / "video.mp4", out / "poster.jpg")

    entry = {"name": name, "title": data["title"]}
    entries = load()
    names = [e["name"] for e in entries]
    if name in names:
        entries[names.index(name)] = entry
    else:
        entries.append(entry)
    save(entries)

    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) / 1e6
    print(f"Added {name}: {data['title']}, {len(data['steps'])} steps, {len(pages)} pages, {size:.1f} MB")
    if not in_sync:
        print(f"  WARNING: the video ({data['duration']} s) doesn't match the current step timings; "
              f"re-render it and add it again, or the steps will be out of sync on the site.")


def remove(name: str):
    entries = load()
    kept = [e for e in entries if e["name"] != name]
    if len(kept) == len(entries):
        sys.exit(f"{name} is not in the showcase.")
    shutil.rmtree(SHOWCASE_DIR / name, ignore_errors=True)
    save(kept)
    print(f"Removed {name}.")


def up(name: str):
    entries = load()
    names = [e["name"] for e in entries]
    if name not in names:
        sys.exit(f"{name} is not in the showcase.")
    i = names.index(name)
    if i > 0:
        entries[i - 1], entries[i] = entries[i], entries[i - 1]
        save(entries)
    show()


def show():
    entries = load()
    if not entries:
        print("The showcase is empty. Add a video with: python utils/showcase.py add NAME")
    for i, e in enumerate(entries, 1):
        print(f"{i}. {e['name']}: {e['title']}")


def main():
    parser = argparse.ArgumentParser(description="Pick the videos the website shows.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    add_cmd = sub.add_parser("add")
    add_cmd.add_argument("names", nargs="+")
    add_cmd.add_argument("--title", default="")
    for command in ("remove", "up"):
        sub.add_parser(command).add_argument("name")
    args = parser.parse_args()

    if args.command == "list":
        show()
    elif args.command == "add":
        if args.title and len(args.names) > 1:
            sys.exit("--title goes with a single NAME.")
        for name in args.names:
            add(name, args.title)
    elif args.command == "remove":
        remove(args.name)
    else:
        up(args.name)


if __name__ == "__main__":
    main()
