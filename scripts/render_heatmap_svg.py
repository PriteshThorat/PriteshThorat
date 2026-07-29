"""Render data/contributions.json into an animated svg/contrib-heatmap.svg.

Self-contained dark terminal panel (not dependent on GitHub's light/dark theme
switching), with a diagonal slide-down reveal animation on each cell.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "svg" / "contrib-heatmap.svg"

CELL = 11
GAP = 3
LEFT_MARGIN = 30
TOP_MARGIN = 55
RIGHT_MARGIN = 10
BOTTOM_MARGIN = 25

LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}

PANEL_BORDER = "#30363d"
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    weeks = data["weeks"]
    total = data["total_contributions"]
    username = data["username"]

    width = LEFT_MARGIN + len(weeks) * (CELL + GAP) + RIGHT_MARGIN
    width = max(width, 860)
    height = TOP_MARGIN + 7 * (CELL + GAP) + BOTTOM_MARGIN

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    parts.append(
        '<defs>'
        '<filter id="panelShadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.45"/>'
        '</filter>'
        '<linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#39d353" stop-opacity="0"/>'
        '<stop offset="50%" stop-color="#39d353" stop-opacity="0.55"/>'
        '<stop offset="100%" stop-color="#39d353" stop-opacity="0"/>'
        '</linearGradient>'
        f'<clipPath id="panelClip"><rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10"/></clipPath>'
        '</defs>'
    )
    parts.append(
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" '
        f'fill="#0d1117" stroke="{PANEL_BORDER}" stroke-width="1" filter="url(#panelShadow)"/>'
    )
    parts.append(
        f'<text x="20" y="24" font-family="Consolas, \'Courier New\', monospace" '
        f'font-size="13" fill="#39d353">{username}@github ~ $ ./contributions.sh</text>'
    )

    for dow, label in WEEKDAY_LABELS.items():
        y = TOP_MARGIN + dow * (CELL + GAP) + CELL - 2
        parts.append(
            f'<text x="4" y="{y}" font-family="Consolas, monospace" '
            f'font-size="9" fill="#7d8590">{label}</text>'
        )

    last_month = None
    for week_index, week in enumerate(weeks):
        for day in week:
            if day and day["date"]:
                month = day["date"][:7]
                if month != last_month:
                    x = LEFT_MARGIN + week_index * (CELL + GAP)
                    month_label = day["date"][5:7]
                    parts.append(
                        f'<text x="{x}" y="{TOP_MARGIN - 8}" font-family="Consolas, monospace" '
                        f'font-size="9" fill="#7d8590">{month_label}</text>'
                    )
                    last_month = month
                break

    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            if day is None:
                continue
            level = day["level"]
            color = LEVEL_COLORS.get(level, LEVEL_COLORS[0])
            x = LEFT_MARGIN + week_index * (CELL + GAP)
            y = TOP_MARGIN + day_index * (CELL + GAP)
            delay = 0.015 * (week_index + day_index)
            title = f'{day["date"]}: {day["count"]} contribution(s)'
            parts.append(
                f'<rect x="{x}" y="{y - 14}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<title>{title}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
                f'<animate attributeName="y" from="{y - 14}" to="{y}" '
                f'begin="{delay:.3f}s" dur="0.35s" calcMode="spline" '
                f'keySplines="0.2 0.8 0.2 1" fill="freeze"/>'
                f'</rect>'
            )

    footer_y = height - 8
    parts.append(
        f'<text x="20" y="{footer_y}" font-family="Consolas, monospace" '
        f'font-size="11" fill="#7d8590">{total} contributions in the last year</text>'
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
    legend_x = width - RIGHT_MARGIN - legend_width
    legend_y = height - 8 - legend_cell

    parts.append(
        f'<text x="{legend_x}" y="{footer_y}" font-family="Consolas, monospace" '
        f'font-size="10" fill="#7d8590">Less</text>'
    )
    swatch_start_x = legend_x + len("Less") * 6 + legend_label_gap
    for level in range(legend_swatches):
        sx = swatch_start_x + level * (legend_cell + legend_gap)
        parts.append(
            f'<rect x="{sx}" y="{legend_y}" width="{legend_cell}" height="{legend_cell}" '
            f'rx="2" fill="{LEVEL_COLORS[level]}"/>'
        )
    more_x = swatch_start_x + legend_swatches * (legend_cell + legend_gap) + legend_label_gap - 6
    parts.append(
        f'<text x="{more_x}" y="{footer_y}" font-family="Consolas, monospace" '
        f'font-size="10" fill="#7d8590">More</text>'
    )

    scan_loop_duration = 1.8
    scan_height = 28
    parts.append(
        f'<g clip-path="url(#panelClip)" style="mix-blend-mode:screen">'
        f'<rect x="1" width="{width - 2}" height="{scan_height}" fill="url(#scanGrad)">'
        f'<animate attributeName="y" from="{1 - scan_height}" to="{height - 1}" '
        f'begin="0s" dur="{scan_loop_duration}s" repeatCount="indefinite" calcMode="linear"/>'
        f'</rect></g>'
    )

    parts.append("</svg>")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({width}x{height})")


if __name__ == "__main__":
    main()
