"""One image of every manual's finished piece, to review a change across all
of them at a glance (outputs/checks/review_sheet.png).

For each manual it runs the pipeline up to the Blender script, then renders
only the last frame (V3_LAST_FRAME_ONLY) at reduced size, and keeps it in
outputs/checks/review/<name>.png. Much faster than rendering every video.

Usage (from the repo root):
    python utils/review_sheet.py [NAME ...]        # all described manuals by default
    python utils/review_sheet.py --sheet-only      # rebuild the sheet from the kept frames

Runs manuals one at a time; output paths are fixed, so don't start another
pipeline run while it works.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from PIL import Image

from config import BLENDER_V3_SCRIPT, FRAMES_V3_DIR, MANUALS_DIR, OUTPUTS_DIR, is_described
from utils.image_budget import fit_cells, grid

load_dotenv(PROJECT_ROOT / ".env")
BLENDER_EXE = os.environ.get("BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
REVIEW_DIR = OUTPUTS_DIR / "checks" / "review"
SHEET = OUTPUTS_DIR / "checks" / "review_sheet.png"
# Half size is plenty for a sheet cell and renders about four times faster.
RESOLUTION_PERCENT = "50"


def described_manuals():
    return sorted(p.name for p in MANUALS_DIR.iterdir() if p.is_dir() and is_described(p))


def render_last_frame(name: str) -> bool:
    run = subprocess.run([sys.executable, "v2/run_mvp_pipeline.py", name, "--no-render", "--quiet"],
                         cwd=PROJECT_ROOT, capture_output=True, text=True)
    if run.returncode:
        print(f"{name}: pipeline failed (see outputs/logs/pipeline.log)")
        return False
    for old in FRAMES_V3_DIR.glob("frame_*.png"):
        old.unlink()
    env = {**os.environ, "V3_LAST_FRAME_ONLY": "1", "V3_RESOLUTION_PERCENT": RESOLUTION_PERCENT}
    # The resolution and frame range are written into the script, so build it again with them.
    subprocess.run([sys.executable, "v2/rendering/blender_builder_v3.py"], cwd=PROJECT_ROOT, env=env,
                   capture_output=True, text=True, check=True)
    blender = subprocess.run([BLENDER_EXE, "--background", "--python-exit-code", "1", "--python", str(BLENDER_V3_SCRIPT)],
                             cwd=PROJECT_ROOT, env=env, capture_output=True, text=True)
    frames = sorted(FRAMES_V3_DIR.glob("frame_*.png"))
    if blender.returncode or not frames:
        print(f"{name}: Blender failed\n{blender.stdout[-800:]}{blender.stderr[-800:]}")
        return False
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(frames[-1], REVIEW_DIR / f"{name}.png")
    print(f"{name}: rendered")
    return True


def build_sheet(names: list) -> None:
    kept = [(n, REVIEW_DIR / f"{n}.png") for n in names if (REVIEW_DIR / f"{n}.png").exists()]
    if not kept:
        sys.exit("No review frames yet; run without --sheet-only first.")
    images = [Image.open(p).convert("RGB") for _, p in kept]
    cols = 4 if len(images) > 6 else 2
    w, h = fit_cells(len(images), cols, images[0].width / images[0].height)
    sheet = grid([im.resize((w, h), Image.LANCZOS) for im in images], cols, labels=[n for n, _ in kept])
    sheet.save(SHEET)
    print(f"{SHEET}  {sheet.width}x{sheet.height}, {len(images)} manuals")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("names", nargs="*")
    parser.add_argument("--sheet-only", action="store_true", help="rebuild the sheet from kept frames")
    args = parser.parse_args()
    names = args.names or described_manuals()
    failed = [] if args.sheet_only else [n for n in names if not render_last_frame(n)]
    build_sheet(described_manuals() if not args.names else names)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
