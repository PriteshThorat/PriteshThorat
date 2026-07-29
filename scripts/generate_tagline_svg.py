"""Generate an animated typewriter-effect tagline SVG.

Self-contained SMIL animation: the tagline types out character-by-character
via a clip-path width reveal, then a cursor block blinks indefinitely once
typing finishes (chained via begin="typeAnim.end").
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "svg" / "typing-tagline.svg"

WIDTH = 860
HEIGHT = 40
FONT_SIZE = 18
CHAR_WIDTH_RATIO = 0.6
LEFT_PADDING = 20
START_DELAY = 0.3
CHAR_DUR = 0.045

TEXT_COLOR = "#39d353"
CURSOR_COLOR = "#39d353"

TAGLINE = "$ Full Stack Developer · MERN Stack Enthusiast · Backend Lover"


def main():
    char_width = FONT_SIZE * CHAR_WIDTH_RATIO
    full_width = len(TAGLINE) * char_width
    type_duration = len(TAGLINE) * CHAR_DUR

    baseline_y = HEIGHT // 2 + FONT_SIZE // 3
    clip_y = baseline_y - FONT_SIZE
    clip_height = FONT_SIZE + 6

    cursor_x = LEFT_PADDING + full_width + 2
    cursor_y = baseline_y - FONT_SIZE + 2
    cursor_width = FONT_SIZE * 0.5
    cursor_height = FONT_SIZE

    scan_height = 14

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs>
  <linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{TEXT_COLOR}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{TEXT_COLOR}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{TEXT_COLOR}" stop-opacity="0"/>
  </linearGradient>
</defs>
<clipPath id="typeClip">
  <rect x="{LEFT_PADDING}" y="{clip_y}" height="{clip_height}" width="0">
    <animate id="typeAnim" attributeName="width" from="0" to="{full_width:.1f}" begin="{START_DELAY}s" dur="{type_duration:.3f}s" fill="freeze" calcMode="linear"/>
  </rect>
</clipPath>
<text clip-path="url(#typeClip)" x="{LEFT_PADDING}" y="{baseline_y}" font-family="Consolas, 'Courier New', monospace" font-size="{FONT_SIZE}" fill="{TEXT_COLOR}" xml:space="preserve">{escape(TAGLINE)}</text>
<rect x="{cursor_x:.1f}" y="{cursor_y}" width="{cursor_width:.1f}" height="{cursor_height}" fill="{CURSOR_COLOR}" opacity="0">
  <animate attributeName="opacity" from="0" to="1" begin="{START_DELAY}s" dur="0.01s" fill="freeze"/>
  <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.5;0.5;1;1" dur="1s" begin="typeAnim.end" repeatCount="indefinite"/>
</rect>
<g style="mix-blend-mode:screen">
  <rect x="0" width="{WIDTH}" height="{scan_height}" fill="url(#scanGrad)">
    <animate attributeName="y" from="{-scan_height}" to="{HEIGHT}" begin="0s" dur="1.8s" repeatCount="indefinite" calcMode="linear"/>
  </rect>
</g>
</svg>
'''

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
