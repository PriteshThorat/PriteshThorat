"""Generate a static neofetch-style info card SVG from the profile's bio content.

No photo dependency — content is sourced from the existing README bio/tech
stack rather than invented. Animation: staggered per-line fade-in.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "svg" / "info-card.svg"

WIDTH = 490
LINE_HEIGHT = 26
TOP_PADDING = 60
BOTTOM_PADDING = 24

LINES = [
    ("label", "pritesh@github", None),
    ("rule", None, None),
    ("kv", "Role", "Full Stack Developer (MERN)"),
    ("kv", "Currently", "Twitter-clone platform (React + Node.js)"),
    ("kv", "Learning", "Next.js & backend architecture"),
    ("kv", "Stack", "JS · TS · React · Redux · Next.js"),
    ("kv", "", "Node.js · Express.js · MongoDB · Git"),
    ("kv", "Portfolio", "priteshthorat.vercel.app"),
    ("kv", "Fun fact", "loves building robust backend systems"),
]

ACCENT = "#39d353"
DIM = "#7d8590"
TEXT = "#c9d1d9"
BG = "#0d1117"
PANEL_BORDER = "#30363d"


def render_line(index: int, kind: str, key: str, value: str) -> str:
    y = TOP_PADDING + index * LINE_HEIGHT
    delay = 0.2 * index

    if kind == "label":
        content = (
            f'<text x="20" y="{y}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="15" font-weight="bold" fill="{ACCENT}" opacity="0">{escape(key)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
            f'dur="0.3s" fill="freeze"/></text>'
        )
        rule_y = y + 10
        content += (
            f'<line x1="20" y1="{rule_y}" x2="{WIDTH - 20}" y2="{rule_y}" '
            f'stroke="{PANEL_BORDER}" stroke-width="1" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay + 0.05:.2f}s" '
            f'dur="0.3s" fill="freeze"/></line>'
        )
        return content

    if kind == "rule":
        return ""

    if key:
        text = (
            f'<tspan fill="{ACCENT}">▸ {escape(key)}:</tspan> '
            f'<tspan fill="{TEXT}">{escape(value)}</tspan>'
        )
    else:
        text = f'<tspan fill="{TEXT}">{"  " }{escape(value)}</tspan>'

    return (
        f'<text x="20" y="{y}" font-family="Consolas, \'Courier New\', monospace" '
        f'font-size="13" opacity="0">{text}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
        f'dur="0.3s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 6" to="0 0" begin="{delay:.2f}s" dur="0.3s" fill="freeze"/>'
        f'</text>'
    )


def main():
    height = TOP_PADDING + len(LINES) * LINE_HEIGHT + BOTTOM_PADDING

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
        f'<text x="20" y="28" font-family="Consolas, monospace" font-size="12" '
        f'fill="{DIM}">$ neofetch</text>',
    ]

    for i, (kind, key, value) in enumerate(LINES):
        parts.append(render_line(i, kind, key, value))

    scan_loop_duration = 1.8
    scan_height = 28
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
