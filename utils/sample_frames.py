"""Make one image of evenly spaced frames from a finished video, to check
that parts end up where the manual shows them.

Usage (from the repo root):
    python utils/sample_frames.py NAME            # outputs/videos/NAME.mp4, 6 frames
    python utils/sample_frames.py NAME --count 9 --cols 3
    python utils/sample_frames.py NAME --at 12.5  # one frame at 12.5 s, full size

Images go to outputs/checks/. The grid is sized so no detail is lost to the
model's own downscaling; when something in it is unclear, look at that moment
with --at.
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import imageio.v3 as iio
from PIL import Image

from config import OUTPUTS_DIR, VIDEOS_DIR
from utils.image_budget import fit, fit_cells, grid

CHECKS_DIR = OUTPUTS_DIR / "checks"


def video_path(name: str) -> Path:
    path = Path(name)
    if path.suffix != ".mp4":
        path = VIDEOS_DIR / f"{name}.mp4"
    if not path.exists():
        sys.exit(f"No video at {path}. Run the pipeline first.")
    return path


def read_frames(path: Path, picks: list) -> list:
    """Decode the video once, keeping only the picked frames (the last frame
    stands in for any pick past the end, since the frame count is estimated)."""
    wanted, kept, last = set(picks), {}, None
    for index, frame in enumerate(iio.imiter(path)):
        last = frame
        if index in wanted:
            kept[index] = Image.fromarray(frame)
    return [kept[i] if i in kept else Image.fromarray(last) for i in picks]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("video", help="Manual name (outputs/videos/NAME.mp4) or a path to an .mp4.")
    parser.add_argument("--count", type=int, default=6, help="How many frames to sample.")
    parser.add_argument("--cols", type=int, default=2, help="Frames per row.")
    parser.add_argument("--at", type=float, help="Save the single frame at this many seconds instead.")
    args = parser.parse_args()

    path = video_path(args.video)
    CHECKS_DIR.mkdir(parents=True, exist_ok=True)
    meta = iio.immeta(path)
    fps = meta.get("fps", 24)
    total = max(1, round(meta["duration"] * fps))

    if args.at is not None:
        picks = [min(total - 1, max(0, round(args.at * fps)))]
    else:
        count = max(1, min(args.count, total))
        picks = [round(i * (total - 1) / max(1, count - 1)) for i in range(count)]
    frames = read_frames(path, picks)

    if args.at is not None:
        out = CHECKS_DIR / f"{path.stem}_{args.at:g}s.png"
        fit(frames[0]).save(out)
        print(f"{out}  (frame {picks[0] + 1} of about {total})")
        return

    w, h = fit_cells(len(frames), args.cols, frames[0].width / frames[0].height)
    cells = [frame.resize((w, h), Image.LANCZOS) for frame in frames]
    sheet = grid(cells, args.cols, labels=[f"{i / fps:.1f}s" for i in picks])
    out = CHECKS_DIR / f"{path.stem}_frames.png"
    sheet.save(out)
    print(f"{out}  {sheet.width}x{sheet.height}, {len(frames)} of about {total} frames ({meta['duration']:.1f} s)")


if __name__ == "__main__":
    main()
