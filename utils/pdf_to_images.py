"""Add a manual: copy its PDF into manuals/<name>/manual.pdf and render each
page to manuals/<name>/pages/page_<n>.png, ready to be read and described.

Usage (from the repo root):
    python utils/pdf_to_images.py path/to/manual.pdf [name]

name defaults to the PDF's file name, e.g. "New Table Manual.pdf" -> new_table_manual.
"""
import re
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import fitz

from config import MANUALS_DIR, MAX_UPLOAD_MB, MAX_UPLOAD_PAGES


def manual_name(pdf_path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "_", pdf_path.stem.lower()).strip("_") or "manual"


def pdf_to_images(pdf_path: Path, output_dir: Path, zoom: int = 2):
    if not pdf_path.exists():
        raise FileNotFoundError(f"Manual PDF not found: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    for old_file in output_dir.glob("page_*.png"):
        old_file.unlink()

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_index in range(len(doc)):
        pix = doc[page_index].get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        image_path = output_dir / f"page_{page_index + 1}.png"
        pix.save(image_path)
        image_paths.append(image_path)

    doc.close()
    return image_paths


def upload_problem(data: bytes) -> str:
    """Why an uploaded file can't be used ("" when it's fine): it must be a
    PDF of at most MAX_UPLOAD_PAGES pages and MAX_UPLOAD_MB megabytes."""
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        return f"The file is over {MAX_UPLOAD_MB} MB, the limit."
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            pages = doc.page_count
    except Exception:
        return "That file isn't a readable PDF."
    if pages > MAX_UPLOAD_PAGES:
        return f"The manual has {pages} pages; the limit is {MAX_UPLOAD_PAGES}."
    return ""


def add_manual(pdf_path: Path, name: str = "") -> Path:
    """Set up manuals/<name>/ for a PDF and render its pages. Returns the folder."""
    manual_dir = MANUALS_DIR / (name or manual_name(pdf_path))
    manual_dir.mkdir(parents=True, exist_ok=True)

    stored = manual_dir / "manual.pdf"
    if pdf_path.resolve() != stored.resolve():
        shutil.copyfile(pdf_path, stored)

    pdf_to_images(stored, manual_dir / "pages")
    return manual_dir


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    manual_dir = add_manual(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "")
    pages = sorted((manual_dir / "pages").glob("page_*.png"))

    print(f"Manual folder: {manual_dir}")
    print(f"Rendered {len(pages)} pages to {manual_dir / 'pages'}")
    print(f"Next: describe the pages in {manual_dir / 'describe.py'} "
          f"(in Claude Code: /describe-manual {manual_dir.name})")


if __name__ == "__main__":
    main()
