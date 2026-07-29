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
# Must match CHAR_ASPECT_CORRECTION in preprocess_photo.py — that script sizes
# the ascii grid's row count assuming rows are drawn at char_width / this
# ratio tall. If the two drift apart the portrait renders stretched/squashed
# relative to the source photo.
CHAR_ASPECT_CORRECTION = 0.55
TOP_PADDING = 20
SIDE_PADDING = 8
ROW_STAGGER = 0.03
ROW_DURATION = 0.18

TEXT_COLOR = "#39d353"
BG = "#0d1117"
PANEL_BORDER = "#30363d"
DIM = "#7d8590"

HANDLE_TEXT = "@PriteshThorat"


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    rows = data["rows"]
    if not rows:
        raise SystemExit("data/ascii_art.json has no rows to render.")

    cols = len(rows[0])
    font_size = max(3, min(CHAR_WIDTH, (WIDTH - 2 * SIDE_PADDING) / (cols * 0.6)))
    row_full_width = cols * font_size * 0.6
    char_width = font_size * 0.6
    row_height = char_width / CHAR_ASPECT_CORRECTION

    height = round(TOP_PADDING * 2 + len(rows) * row_height)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}">',
        '<defs>'
        '<filter id="panelShadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.45"/>'
        '</filter>'
        '<linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#39d353" stop-opacity="0"/>'
        '<stop offset="50%" stop-color="#39d353" stop-opacity="0.55"/>'
        '<stop offset="100%" stop-color="#39d353" stop-opacity="0"/>'
        '</linearGradient>'
        f'<clipPath id="panelClip"><rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10"/></clipPath>'
        '</defs>',
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10" '
        f'fill="{BG}" stroke="{PANEL_BORDER}" stroke-width="1" filter="url(#panelShadow)"/>',
    ]

    for row_index, row_text in enumerate(rows):
        y = TOP_PADDING + row_index * row_height
        clip_id = f"clipRow{row_index}"
        begin = row_index * ROW_STAGGER

        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{SIDE_PADDING}" y="{y - row_height + 2:.1f}" height="{row_height:.1f}" width="0">'
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

    rows_end = (len(rows) - 1) * ROW_STAGGER + ROW_DURATION

    art_right_edge = SIDE_PADDING + row_full_width
    divider_x = art_right_edge + 14
    if divider_x + 30 < WIDTH - SIDE_PADDING:
        handle_begin = rows_end + 0.15

        parts.append(
            f'<line x1="{divider_x:.1f}" y1="{TOP_PADDING - 8}" x2="{divider_x:.1f}" '
            f'y2="{height - 12}" stroke="{PANEL_BORDER}" stroke-width="1" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{handle_begin:.3f}s" '
            f'dur="0.3s" fill="freeze"/></line>'
        )

        text_cx = (divider_x + 14 + WIDTH - SIDE_PADDING) / 2
        text_cy = height / 2
        parts.append(
            f'<text x="{text_cx:.1f}" y="{text_cy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" transform="rotate(-90 {text_cx:.1f} {text_cy:.1f})" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="15" '
            f'letter-spacing="3" fill="{TEXT_COLOR}" opacity="0">{escape(HANDLE_TEXT)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{handle_begin:.3f}s" '
            f'dur="0.4s" fill="freeze"/>'
            f'</text>'
        )

    scan_height = 22
    scan_loop_duration = 1.8
    parts.append(
        f'<g clip-path="url(#panelClip)" style="mix-blend-mode:screen">'
        f'<rect x="1" width="{WIDTH - 2}" height="{scan_height}" fill="url(#scanGrad)">'
        f'<animate attributeName="y" from="{1 - scan_height}" to="{height - 1}" '
        f'begin="0s" dur="{scan_loop_duration}s" repeatCount="indefinite" calcMode="linear"/>'
        f'</rect></g>'
    )

    parts.append("</svg>")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({WIDTH}x{height})")


if __name__ == "__main__":
    main()
