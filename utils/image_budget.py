"""Image sizes that keep full detail when Claude reads an image.

Claude scales any image down to at most MAX_EDGE pixels on the long side and
about MAX_PIXELS in total before reading it. Pixels beyond that cost upload
time but add no detail, so the sheet tools fit images to this budget and
never upscale.
"""
from PIL import Image

MAX_EDGE = 1568
MAX_PIXELS = 1_150_000


def fit(image: Image.Image, max_edge: int = MAX_EDGE, max_pixels: int = MAX_PIXELS) -> Image.Image:
    w, h = image.size
    scale = min(1.0, max_edge / max(w, h), (max_pixels / (w * h)) ** 0.5)
    if scale >= 1.0:
        return image
    return image.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)


def fit_cells(count: int, cols: int, cell_aspect: float, gap: int = 12) -> tuple:
    """Largest (w, h) cell, at aspect w/h, whose grid of count cells fits the budget."""
    rows = -(-count // cols)
    h = MAX_EDGE
    while h > 8:
        w = round(h * cell_aspect)
        sheet_w, sheet_h = cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap
        if max(sheet_w, sheet_h) <= MAX_EDGE and sheet_w * sheet_h <= MAX_PIXELS:
            return w, h
        h -= 4
    return round(h * cell_aspect), h


def grid(images: list, cols: int, gap: int = 12, labels: list = None) -> Image.Image:
    """Lay images out left-to-right in rows, on white, with optional labels.
    Size the images with fit_cells first so the sheet is not scaled again."""
    from PIL import ImageDraw, ImageFont

    font = ImageFont.load_default(size=16)

    cell_w = max(im.width for im in images)
    cell_h = max(im.height for im in images)
    rows = -(-len(images) // cols)
    sheet = Image.new("RGB", (cols * cell_w + (cols - 1) * gap, rows * cell_h + (rows - 1) * gap), "white")
    draw = ImageDraw.Draw(sheet)
    for i, im in enumerate(images):
        x, y = (i % cols) * (cell_w + gap), (i // cols) * (cell_h + gap)
        sheet.paste(im, (x, y))
        if labels:
            text = labels[i]
            box = draw.textbbox((x + 4, y + 4), text, font=font)
            draw.rectangle((box[0] - 3, box[1] - 2, box[2] + 3, box[3] + 2), fill="black")
            draw.text((x + 4, y + 4), text, fill="white", font=font)
    return sheet
