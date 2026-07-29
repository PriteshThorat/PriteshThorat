"""Convert a preprocessed grayscale image into ASCII-art rows.

Reads assets/photo_processed.png (from preprocess_photo.py) and writes
data/ascii_art.json as a list of equal-length row strings, light-to-dark
luminance mapped onto a character ramp.
"""

import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "assets" / "photo_processed.png"
DEFAULT_OUTPUT = ROOT / "data" / "ascii_art.json"

# Light -> dark ramp.
RAMP = " .:-=+*#%@"


def image_to_ascii_rows(image: Image.Image):
    pixels = image.load()
    width, height = image.size
    rows = []
    for y in range(height):
        row_chars = []
        for x in range(width):
            luminance = pixels[x, y]
            index = min(len(RAMP) - 1, int((luminance / 255) * (len(RAMP) - 1)))
            # Invert: dark pixel (low luminance) -> dense character.
            row_chars.append(RAMP[len(RAMP) - 1 - index])
        rows.append("".join(row_chars))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(
            f"Processed photo not found: {input_path}. "
            "Run scripts/preprocess_photo.py first."
        )

    image = Image.open(input_path).convert("L")
    rows = image_to_ascii_rows(image)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")
    print(f"Wrote {output_path} ({len(rows)} rows x {len(rows[0]) if rows else 0} cols)")


if __name__ == "__main__":
    main()
