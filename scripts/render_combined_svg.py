"""Assemble tagline + heatmap + ascii portrait + info card into ONE combined SVG.

Why: GitHub strips <script> from READMEs, so 4 separate <img>-embedded SVGs
each run their own independent animation clock — there is no way to
synchronize them against each other. Merging everything into a single SVG
document gives them one shared timeline, so a single scan-bar can sweep
top-to-bottom across the whole thing and each section's reveal animation can
be timed to trigger exactly when the scan line reaches it.

Reads data/contributions.json and data/ascii_art.json (both already produced
by fetch_contributions.py / ascii_convert.py) plus the same hardcoded
info-card/tagline content used by the standalone generators, and writes
svg/readme-hero.svg.
"""

import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "svg" / "readme-hero.svg"

WIDTH = 860

BG = "#0d1117"
ACCENT = "#39d353"
TEXT = "#c9d1d9"
DIM = "#7d8590"
PANEL_BORDER = "#30363d"

SECTION_GAP = 16

SCAN_SPEED_PX_PER_S = 150  # governs both the loop duration and reveal pacing

# ---------------------------------------------------------------------------
# Tagline
# ---------------------------------------------------------------------------
TAGLINE_HEIGHT = 40
TAGLINE_FONT_SIZE = 18
TAGLINE_CHAR_WIDTH_RATIO = 0.6
TAGLINE_LEFT_PADDING = 20
TAGLINE_CHAR_DUR = 0.045
TAGLINE_TEXT = "$ Full Stack Developer · MERN Stack Enthusiast · Backend Lover"


def render_tagline(y_offset: float, time_offset: float):
    char_width = TAGLINE_FONT_SIZE * TAGLINE_CHAR_WIDTH_RATIO
    full_width = len(TAGLINE_TEXT) * char_width
    type_duration = len(TAGLINE_TEXT) * TAGLINE_CHAR_DUR

    baseline_y = y_offset + TAGLINE_HEIGHT // 2 + TAGLINE_FONT_SIZE // 3
    clip_y = baseline_y - TAGLINE_FONT_SIZE
    clip_height = TAGLINE_FONT_SIZE + 6

    cursor_x = TAGLINE_LEFT_PADDING + full_width + 2
    cursor_y = baseline_y - TAGLINE_FONT_SIZE + 2
    cursor_width = TAGLINE_FONT_SIZE * 0.5
    cursor_height = TAGLINE_FONT_SIZE

    begin = time_offset

    parts = [
        '<clipPath id="typeClip">',
        f'<rect x="{TAGLINE_LEFT_PADDING}" y="{clip_y:.1f}" height="{clip_height}" width="0">',
        f'<animate id="typeAnim" attributeName="width" from="0" to="{full_width:.1f}" '
        f'begin="{begin:.3f}s" dur="{type_duration:.3f}s" fill="freeze" calcMode="linear"/>',
        '</rect></clipPath>',
        f'<text clip-path="url(#typeClip)" x="{TAGLINE_LEFT_PADDING}" y="{baseline_y:.1f}" '
        f'font-family="Consolas, \'Courier New\', monospace" font-size="{TAGLINE_FONT_SIZE}" '
        f'fill="{ACCENT}" xml:space="preserve">{escape(TAGLINE_TEXT)}</text>',
        f'<rect x="{cursor_x:.1f}" y="{cursor_y:.1f}" width="{cursor_width:.1f}" '
        f'height="{cursor_height}" fill="{ACCENT}" opacity="0">',
        f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" '
        f'dur="0.01s" fill="freeze"/>',
        '<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.5;0.5;1;1" '
        'dur="1s" begin="typeAnim.end" repeatCount="indefinite"/>',
        '</rect>',
    ]
    return parts, TAGLINE_HEIGHT


# ---------------------------------------------------------------------------
# Contribution heatmap
# ---------------------------------------------------------------------------
CELL = 11
GAP = 3
HEATMAP_LEFT_MARGIN = 30
HEATMAP_TOP_MARGIN = 45
HEATMAP_BOTTOM_MARGIN = 25
HEATMAP_RIGHT_MARGIN = 10

LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def render_heatmap(y_offset: float, time_offset: float, data: dict):
    weeks = data["weeks"]
    total = data["total_contributions"]
    username = data["username"]

    height = HEATMAP_TOP_MARGIN + 7 * (CELL + GAP) + HEATMAP_BOTTOM_MARGIN

    parts = [
        f'<text x="20" y="{y_offset + 20:.1f}" font-family="Consolas, \'Courier New\', monospace" '
        f'font-size="13" fill="{ACCENT}">{username}@github ~ $ ./contributions.sh</text>'
    ]

    for dow, label in WEEKDAY_LABELS.items():
        y = y_offset + HEATMAP_TOP_MARGIN + dow * (CELL + GAP) + CELL - 2
        parts.append(
            f'<text x="4" y="{y:.1f}" font-family="Consolas, monospace" '
            f'font-size="9" fill="{DIM}">{label}</text>'
        )

    last_month = None
    for week_index, week in enumerate(weeks):
        for day in week:
            if day and day["date"]:
                month = day["date"][:7]
                if month != last_month:
                    x = HEATMAP_LEFT_MARGIN + week_index * (CELL + GAP)
                    month_label = day["date"][5:7]
                    parts.append(
                        f'<text x="{x}" y="{y_offset + HEATMAP_TOP_MARGIN - 8:.1f}" '
                        f'font-family="Consolas, monospace" font-size="9" '
                        f'fill="{DIM}">{month_label}</text>'
                    )
                    last_month = month
                break

    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            if day is None:
                continue
            level = day["level"]
            color = LEVEL_COLORS.get(level, LEVEL_COLORS[0])
            x = HEATMAP_LEFT_MARGIN + week_index * (CELL + GAP)
            y = y_offset + HEATMAP_TOP_MARGIN + day_index * (CELL + GAP)
            begin = time_offset + 0.015 * (week_index + day_index)
            title = f'{day["date"]}: {day["count"]} contribution(s)'
            parts.append(
                f'<rect x="{x}" y="{y - 14:.1f}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<title>{title}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.3f}s" dur="0.35s" fill="freeze"/>'
                f'<animate attributeName="y" from="{y - 14:.1f}" to="{y:.1f}" '
                f'begin="{begin:.3f}s" dur="0.35s" calcMode="spline" '
                f'keySplines="0.2 0.8 0.2 1" fill="freeze"/>'
                f'</rect>'
            )

    footer_y = y_offset + height - 8
    parts.append(
        f'<text x="20" y="{footer_y:.1f}" font-family="Consolas, monospace" '
        f'font-size="11" fill="{DIM}">{total} contributions in the last year</text>'
    )

    legend_cell = 9
    legend_gap = 3
    legend_label_gap = 6
    legend_swatches = len(LEVEL_COLORS)
    legend_width = (
        len("Less") * 6 + legend_label_gap
        + legend_swatches * (legend_cell + legend_gap)
        + len("More") * 6 + legend_label_gap
    )
    legend_x = WIDTH - HEATMAP_RIGHT_MARGIN - legend_width
    legend_y = y_offset + height - 8 - legend_cell

    parts.append(
        f'<text x="{legend_x}" y="{footer_y:.1f}" font-family="Consolas, monospace" '
        f'font-size="10" fill="{DIM}">Less</text>'
    )
    swatch_start_x = legend_x + len("Less") * 6 + legend_label_gap
    for level in range(legend_swatches):
        sx = swatch_start_x + level * (legend_cell + legend_gap)
        parts.append(
            f'<rect x="{sx}" y="{legend_y:.1f}" width="{legend_cell}" height="{legend_cell}" '
            f'rx="2" fill="{LEVEL_COLORS[level]}"/>'
        )
    more_x = swatch_start_x + legend_swatches * (legend_cell + legend_gap) + legend_label_gap - 6
    parts.append(
        f'<text x="{more_x}" y="{footer_y:.1f}" font-family="Consolas, monospace" '
        f'font-size="10" fill="{DIM}">More</text>'
    )

    return parts, height


# ---------------------------------------------------------------------------
# Info card (right column)
# ---------------------------------------------------------------------------
INFO_WIDTH = 490
INFO_LINE_HEIGHT = 26
INFO_TOP_PADDING = 40
INFO_BOTTOM_PADDING = 24

INFO_LINES = [
    ("label", "pritesh@github", None),
    ("kv", "Role", "Full Stack Developer (MERN)"),
    ("kv", "Currently", "Twitter-clone platform (React + Node.js)"),
    ("kv", "Learning", "Next.js & backend architecture"),
    ("kv", "Stack", "JS · TS · React · Redux · Next.js"),
    ("kv", "", "Node.js · Express.js · MongoDB · Git"),
    ("kv", "Portfolio", "priteshthorat.vercel.app"),
    ("kv", "Fun fact", "loves building robust backend systems"),
]


def info_card_natural_height() -> float:
    return INFO_TOP_PADDING + len(INFO_LINES) * INFO_LINE_HEIGHT + INFO_BOTTOM_PADDING


def render_info_card(x_offset: float, y_offset: float, time_offset: float, panel_height: float):
    parts = [
        f'<rect x="{x_offset + 1}" y="{y_offset + 1:.1f}" width="{INFO_WIDTH - 2}" '
        f'height="{panel_height - 2:.1f}" rx="10" fill="{BG}" stroke="{PANEL_BORDER}" '
        f'stroke-width="1" filter="url(#panelShadow)"/>',
        f'<text x="{x_offset + 20}" y="{y_offset + 24:.1f}" font-family="Consolas, monospace" '
        f'font-size="12" fill="{DIM}">$ neofetch</text>',
    ]

    for i, (kind, key, value) in enumerate(INFO_LINES):
        y = y_offset + INFO_TOP_PADDING + i * INFO_LINE_HEIGHT
        begin = time_offset + 0.15 * i

        if kind == "label":
            parts.append(
                f'<text x="{x_offset + 20}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
                f'font-size="15" font-weight="bold" fill="{ACCENT}" opacity="0">{escape(key)}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" '
                f'dur="0.3s" fill="freeze"/></text>'
            )
            rule_y = y + 10
            parts.append(
                f'<line x1="{x_offset + 20}" y1="{rule_y:.1f}" x2="{x_offset + INFO_WIDTH - 20}" '
                f'y2="{rule_y:.1f}" stroke="{PANEL_BORDER}" stroke-width="1" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin + 0.05:.3f}s" '
                f'dur="0.3s" fill="freeze"/></line>'
            )
            continue

        if key:
            text = (
                f'<tspan fill="{ACCENT}">▸ {escape(key)}:</tspan> '
                f'<tspan fill="{TEXT}">{escape(value)}</tspan>'
            )
        else:
            text = f'<tspan fill="{TEXT}">  {escape(value)}</tspan>'

        parts.append(
            f'<text x="{x_offset + 20}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="13" opacity="0">{text}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" '
            f'dur="0.3s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 6" to="0 0" begin="{begin:.3f}s" dur="0.3s" fill="freeze"/>'
            f'</text>'
        )

    return parts, panel_height


# ---------------------------------------------------------------------------
# ASCII portrait (left column)
# ---------------------------------------------------------------------------
PORTRAIT_WIDTH = 370
PORTRAIT_CHAR_WIDTH = 4.2
PORTRAIT_CHAR_ASPECT_CORRECTION = 0.55  # must match preprocess_photo.py
PORTRAIT_TOP_PADDING = 20
PORTRAIT_SIDE_PADDING = 8
PORTRAIT_ROW_STAGGER = 0.03
PORTRAIT_ROW_DURATION = 0.18
HANDLE_TEXT = "@PriteshThorat"


def ascii_portrait_natural_height(rows: list) -> float:
    cols = len(rows[0])
    font_size = max(3, min(PORTRAIT_CHAR_WIDTH, (PORTRAIT_WIDTH - 2 * PORTRAIT_SIDE_PADDING) / (cols * 0.6)))
    row_height = (font_size * 0.6) / PORTRAIT_CHAR_ASPECT_CORRECTION
    return round(PORTRAIT_TOP_PADDING * 2 + len(rows) * row_height)


def render_ascii_portrait(x_offset: float, y_offset: float, time_offset: float, rows: list, panel_height: float):
    cols = len(rows[0])
    font_size = max(3, min(PORTRAIT_CHAR_WIDTH, (PORTRAIT_WIDTH - 2 * PORTRAIT_SIDE_PADDING) / (cols * 0.6)))
    row_full_width = cols * font_size * 0.6
    char_width = font_size * 0.6
    row_height = char_width / PORTRAIT_CHAR_ASPECT_CORRECTION

    parts = [
        f'<rect x="{x_offset + 1}" y="{y_offset + 1:.1f}" width="{PORTRAIT_WIDTH - 2}" '
        f'height="{panel_height - 2:.1f}" rx="10" fill="{BG}" stroke="{PANEL_BORDER}" '
        f'stroke-width="1" filter="url(#panelShadow)"/>',
    ]

    for row_index, row_text in enumerate(rows):
        y = y_offset + PORTRAIT_TOP_PADDING + row_index * row_height
        clip_id = f"clipRow{row_index}"
        begin = time_offset + row_index * PORTRAIT_ROW_STAGGER

        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{x_offset + PORTRAIT_SIDE_PADDING}" y="{y - row_height + 2:.1f}" '
            f'height="{row_height:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{row_full_width:.1f}" '
            f'begin="{begin:.3f}s" dur="{PORTRAIT_ROW_DURATION}s" fill="freeze"/>'
            f'</rect></clipPath>'
        )
        parts.append(
            f'<text clip-path="url(#{clip_id})" x="{x_offset + PORTRAIT_SIDE_PADDING}" y="{y:.1f}" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="{font_size:.1f}" '
            f'fill="{ACCENT}" xml:space="preserve">{escape(row_text)}</text>'
        )

    rows_end = time_offset + (len(rows) - 1) * PORTRAIT_ROW_STAGGER + PORTRAIT_ROW_DURATION

    art_right_edge = x_offset + PORTRAIT_SIDE_PADDING + row_full_width
    divider_x = art_right_edge + 14
    if divider_x + 30 < x_offset + PORTRAIT_WIDTH - PORTRAIT_SIDE_PADDING:
        handle_begin = rows_end + 0.15

        parts.append(
            f'<line x1="{divider_x:.1f}" y1="{y_offset + PORTRAIT_TOP_PADDING - 8:.1f}" '
            f'x2="{divider_x:.1f}" y2="{y_offset + panel_height - 12:.1f}" stroke="{PANEL_BORDER}" '
            f'stroke-width="1" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{handle_begin:.3f}s" '
            f'dur="0.3s" fill="freeze"/></line>'
        )

        text_cx = (divider_x + 14 + x_offset + PORTRAIT_WIDTH - PORTRAIT_SIDE_PADDING) / 2
        text_cy = y_offset + panel_height / 2
        parts.append(
            f'<text x="{text_cx:.1f}" y="{text_cy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" transform="rotate(-90 {text_cx:.1f} {text_cy:.1f})" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="15" '
            f'letter-spacing="3" fill="{ACCENT}" opacity="0">{escape(HANDLE_TEXT)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{handle_begin:.3f}s" '
            f'dur="0.4s" fill="freeze"/>'
            f'</text>'
        )

    return parts, panel_height


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def main():
    contributions = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    ascii_data = json.loads((ROOT / "data" / "ascii_art.json").read_text(encoding="utf-8"))
    rows = ascii_data["rows"]
    if not rows:
        raise SystemExit("data/ascii_art.json has no rows to render.")

    # Pass 1: figure out each section's height up front (pure geometry, no timing yet).
    heatmap_height = HEATMAP_TOP_MARGIN + 7 * (CELL + GAP) + HEATMAP_BOTTOM_MARGIN
    info_height = info_card_natural_height()
    portrait_height = ascii_portrait_natural_height(rows)
    # Portrait and info card share one bordered row, so both panels are drawn
    # at this same height even though their content is shorter — keeps the
    # two boxes' borders aligned instead of one looking visually shorter.
    bottom_row_height = max(portrait_height, info_height)

    tagline_y = 0
    heatmap_y = tagline_y + TAGLINE_HEIGHT + SECTION_GAP
    bottom_row_y = heatmap_y + heatmap_height + SECTION_GAP
    total_height = bottom_row_y + bottom_row_height

    scan_loop_duration = total_height / SCAN_SPEED_PX_PER_S

    def time_offset_for(y):
        return y / SCAN_SPEED_PX_PER_S

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{total_height}" '
        f'viewBox="0 0 {WIDTH} {total_height}">',
        '<defs>',
        '<filter id="panelShadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.45"/>'
        '</filter>',
        '<linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0"/>'
        f'<stop offset="50%" stop-color="{ACCENT}" stop-opacity="0.55"/>'
        f'<stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>'
        '</linearGradient>',
        '</defs>',
    ]

    tagline_parts, _ = render_tagline(tagline_y, time_offset_for(tagline_y))
    parts.extend(tagline_parts)

    heatmap_parts, _ = render_heatmap(heatmap_y, time_offset_for(heatmap_y), contributions)
    parts.extend(heatmap_parts)

    portrait_parts, _ = render_ascii_portrait(
        0, bottom_row_y, time_offset_for(bottom_row_y), rows, bottom_row_height
    )
    parts.extend(portrait_parts)

    info_parts, _ = render_info_card(
        PORTRAIT_WIDTH, bottom_row_y, time_offset_for(bottom_row_y), bottom_row_height
    )
    parts.extend(info_parts)

    scan_height = 32
    parts.append(
        f'<g style="mix-blend-mode:screen">'
        f'<rect x="0" width="{WIDTH}" height="{scan_height}" fill="url(#scanGrad)">'
        f'<animate attributeName="y" from="{-scan_height}" to="{total_height}" '
        f'begin="0s" dur="{scan_loop_duration:.3f}s" repeatCount="indefinite" calcMode="linear"/>'
        f'</rect></g>'
    )

    parts.append("</svg>")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({WIDTH}x{total_height}, scan loop {scan_loop_duration:.2f}s)")


if __name__ == "__main__":
    main()
