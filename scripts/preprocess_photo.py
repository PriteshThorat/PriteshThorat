"""Preprocess a source photo for ASCII conversion.

Pipeline: isolate the subject (OpenCV GrabCut) -> composite on white ->
grayscale -> CLAHE local-contrast boost (OpenCV) -> resize with a ~0.55
aspect-ratio correction so monospace character cells (taller than wide)
don't squash the portrait vertically.

Run locally only (not in CI) — depends on scripts/requirements-photo.txt.
Uses OpenCV GrabCut rather than rembg: rembg's dependency chain (pymatting ->
numba -> llvmlite) doesn't support Python 3.13, and GrabCut needs nothing
beyond opencv-python, which this pipeline already requires.

Usage:
    python scripts/preprocess_photo.py --input assets/photo.jpg --output assets/photo_processed.png
"""

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ASCII_COLUMNS = 80
CHAR_ASPECT_CORRECTION = 0.55
GRABCUT_MARGIN_RATIO = 0.05
GRABCUT_ITERATIONS = 5


def remove_background(input_path: Path) -> Image.Image:
    bgr = cv2.imread(str(input_path))
    if bgr is None:
        raise SystemExit(f"Could not read image: {input_path}")

    height, width = bgr.shape[:2]
    margin_x = int(width * GRABCUT_MARGIN_RATIO)
    margin_y = int(height * GRABCUT_MARGIN_RATIO)
    rect = (margin_x, margin_y, width - 2 * margin_x, height - 2 * margin_y)

    mask = np.zeros((height, width), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    cv2.grabCut(bgr, mask, rect, bgd_model, fgd_model, GRABCUT_ITERATIONS, cv2.GC_INIT_WITH_RECT)
    foreground_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    rgba = np.dstack([rgb, foreground_mask])
    return Image.fromarray(rgba, mode="RGBA")


def composite_on_white(image: Image.Image) -> Image.Image:
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, image).convert("RGB")


def apply_clahe(image: Image.Image) -> Image.Image:
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return Image.fromarray(enhanced)


def resize_for_ascii(image: Image.Image, columns: int = ASCII_COLUMNS) -> Image.Image:
    width, height = image.size
    aspect_ratio = height / width
    new_height = max(1, int(columns * aspect_ratio * CHAR_ASPECT_CORRECTION))
    return image.resize((columns, new_height))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to source photo (e.g. assets/photo.jpg)")
    parser.add_argument("--output", required=True, help="Path to write processed grayscale PNG")
    parser.add_argument(
        "--no-remove-bg",
        action="store_true",
        help="Skip background removal (useful if the source photo already has a plain background)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input photo not found: {input_path}")

    if args.no_remove_bg:
        image = Image.open(input_path).convert("RGBA")
    else:
        image = remove_background(input_path)

    image = composite_on_white(image)
    image = apply_clahe(image)
    image = resize_for_ascii(image)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    print(f"Wrote {output_path} ({image.size[0]}x{image.size[1]})")


if __name__ == "__main__":
    main()
