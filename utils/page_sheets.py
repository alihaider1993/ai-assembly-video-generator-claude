"""Make the images Claude reads to describe a manual, sized so no detail is
lost to the model's own downscaling (see image_budget.py).

Usage (from the repo root), with manuals/<name>/pages/ already rendered:
    python utils/page_sheets.py NAME                 # contact sheet + two-page sheets
    python utils/page_sheets.py NAME --page 3        # one page, as large as is useful
    python utils/page_sheets.py NAME --page 3 --split 2          # top/bottom halves, ~2x detail
    python utils/page_sheets.py NAME --page 3 --box 0 0.5 1 1    # a region (fractions of the page)

Images go to manuals/<name>/sheets/. Read the two-page sheets for the steps,
and a single page, split or box wherever there is small print: part-list
sizes, labels, "Repeat xN" notes, quantities.
"""
import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image

from config import MANUALS_DIR
from utils.image_budget import fit, fit_cells, grid

# A page counts as blank when almost none of it is ink. Blank pages still
# appear on the contact sheet, so nothing is hidden from the overview.
INK_LEVEL = 200
BLANK_INK_FRACTION = 0.001
SPLIT_OVERLAP = 0.05


def page_paths(manual_dir: Path) -> list:
    pages = list((manual_dir / "pages").glob("page_*.png"))
    if not pages:
        sys.exit(f"No pages in {manual_dir / 'pages'}. Run utils/pdf_to_images.py first.")
    return sorted(pages, key=page_number)


def page_number(path: Path) -> int:
    return int(re.search(r"(\d+)", path.stem).group(1))


def is_blank(image: Image.Image) -> bool:
    gray = image.convert("L")
    ink = sum(gray.histogram()[:INK_LEVEL])
    return ink / (gray.width * gray.height) < BLANK_INK_FRACTION


def shrink_into(images: list, cols: int) -> list:
    """Copies of images, each fitted (keeping its aspect) into one grid cell."""
    aspect = max(im.width / im.height for im in images)
    w, h = fit_cells(len(images), cols, aspect)
    cells = []
    for im in images:
        cell = im.copy()
        cell.thumbnail((w, h), Image.LANCZOS)
        cells.append(cell)
    return cells


def contact_sheet(images: list, numbers: list) -> Image.Image:
    cols = max(1, round(len(images) ** 0.5 * 1.2))
    return grid(shrink_into(images, cols), cols, labels=[f"p{n}" for n in numbers])


def two_page_sheet(images: list, numbers: list) -> Image.Image:
    return grid(shrink_into(images, len(images)), len(images), labels=[f"page {n}" for n in numbers])


def overview(manual_dir: Path, out_dir: Path) -> None:
    paths = page_paths(manual_dir)
    images = [Image.open(p).convert("RGB") for p in paths]
    numbers = [page_number(p) for p in paths]

    contact_sheet(images, numbers).save(out_dir / "contact.png")
    written = [out_dir / "contact.png"]

    content = [(n, im) for n, im in zip(numbers, images) if not is_blank(im)]
    blank = sorted(set(numbers) - {n for n, _ in content})
    for i in range(0, len(content), 2):
        pair = content[i:i + 2]
        name = "pages_" + "_".join(f"{n:02d}" for n, _ in pair) + ".png"
        two_page_sheet([im for _, im in pair], [n for n, _ in pair]).save(out_dir / name)
        written.append(out_dir / name)

    print(f"{len(paths)} pages, {images[0].width}x{images[0].height}px each")
    if blank:
        print(f"Blank pages (no sheet, still on the contact sheet): {', '.join(map(str, blank))}")
    for path in written:
        with Image.open(path) as im:
            print(f"  {path}  {im.width}x{im.height}")
    print("For small print, use --page N (--split 2 or --box) at full detail.")


def single_page(manual_dir: Path, out_dir: Path, number: int, split: int, box: list) -> None:
    path = manual_dir / "pages" / f"page_{number}.png"
    if not path.exists():
        sys.exit(f"No page {number}: {path} does not exist.")
    page = Image.open(path).convert("RGB")
    W, H = page.size

    if box:
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            sys.exit("--box takes x0 y0 x1 y1 as fractions of the page, with x0 < x1 and y0 < y1.")
        crops = {f"page_{number}_box.png": (x0, y0, x1, y1)}
    elif split > 1:
        crops = {}
        band = 1 / split
        for i in range(split):
            top, bottom = max(0.0, i * band - SPLIT_OVERLAP), min(1.0, (i + 1) * band + SPLIT_OVERLAP)
            crops[f"page_{number}_part{i + 1}of{split}.png"] = (0.0, top, 1.0, bottom)
    else:
        crops = {f"page_{number}.png": (0.0, 0.0, 1.0, 1.0)}

    for name, (x0, y0, x1, y1) in crops.items():
        region = page.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
        image = fit(region)
        image.save(out_dir / name)
        detail = image.width / region.width
        print(f"  {out_dir / name}  {image.width}x{image.height}  ({detail:.0%} of the rendered page's detail)")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("manual", help="Manual name under manuals/.")
    parser.add_argument("--page", type=int, help="Make images of this one page instead of the overview.")
    parser.add_argument("--split", type=int, default=1, help="With --page: cut it into this many bands, top to bottom.")
    parser.add_argument("--box", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"),
                        help="With --page: crop this region, as fractions of the page width and height.")
    args = parser.parse_args()

    manual_dir = MANUALS_DIR / args.manual
    out_dir = manual_dir / "sheets"
    out_dir.mkdir(exist_ok=True)

    if args.page is None:
        overview(manual_dir, out_dir)
    else:
        single_page(manual_dir, out_dir, args.page, args.split, args.box)


if __name__ == "__main__":
    main()
