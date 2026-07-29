"""Render data/ascii_art.json into an animated svg/ascii-portrait.svg.

Animation: SMIL clip-path typing reveal, row-by-row, left-to-right,
top-to-bottom, then freeze (no looping).
"""

import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "ascii_art.json"
OUTPUT_PATH = ROOT / "svg" / "ascii-portrait.svg"

WIDTH = 370
CHAR_WIDTH = 4.2
ROW_HEIGHT = 7
TOP_PADDING = 20
SIDE_PADDING = 8
ROW_STAGGER = 0.03
ROW_DURATION = 0.18

TEXT_COLOR = "#39d353"
BG = "#0d1117"
PANEL_BORDER = "#30363d"


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    rows = data["rows"]
    if not rows:
        raise SystemExit("data/ascii_art.json has no rows to render.")

    cols = len(rows[0])
    font_size = max(3, min(CHAR_WIDTH, (WIDTH - 2 * SIDE_PADDING) / (cols * 0.6)))
    row_full_width = cols * font_size * 0.6

    height = TOP_PADDING * 2 + len(rows) * ROW_HEIGHT

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}">',
        '<defs><filter id="panelShadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.45"/>'
        '</filter></defs>',
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10" '
        f'fill="{BG}" stroke="{PANEL_BORDER}" stroke-width="1" filter="url(#panelShadow)"/>',
    ]

    for row_index, row_text in enumerate(rows):
        y = TOP_PADDING + row_index * ROW_HEIGHT
        clip_id = f"clipRow{row_index}"
        begin = row_index * ROW_STAGGER

        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{SIDE_PADDING}" y="{y - ROW_HEIGHT + 2}" height="{ROW_HEIGHT}" width="0">'
            f'<animate attributeName="width" from="0" to="{row_full_width:.1f}" '
            f'begin="{begin:.3f}s" dur="{ROW_DURATION}s" fill="freeze"/>'
            f'</rect>'
            f'</clipPath>'
        )
        parts.append(
            f'<text clip-path="url(#{clip_id})" x="{SIDE_PADDING}" y="{y}" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="{font_size:.1f}" '
            f'fill="{TEXT_COLOR}" xml:space="preserve">{escape(row_text)}</text>'
        )

    parts.append("</svg>")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({WIDTH}x{height})")


if __name__ == "__main__":
    main()
