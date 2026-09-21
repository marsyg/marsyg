#!/usr/bin/env python3
"""Generate an animated (typing-effect) SVG from ascii-banner.txt.

Reads ascii-banner.txt, renders it as terminal-style text on a dark card,
reveals it left-to-right with a SMIL clip animation, then blinks a cursor.
No third-party dependencies — stdlib only.
"""
import html
import sys
from pathlib import Path

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ascii-banner.txt")
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("banner.svg")

FONT_SIZE = 13
CHAR_W = 7.8      # approx monospace advance at 13px
LINE_H = 17
PAD_X = 24
PAD_TOP = 28
PAD_BOTTOM = 24

lines = SRC.read_text(encoding="utf-8").splitlines() or [" "]
max_len = max(len(l) for l in lines)
text_w = max_len * CHAR_W
total_chars = sum(len(l) for l in lines)
# ~28 chars/sec, clamped so the loop stays pleasant
type_dur = min(max(total_chars / 28, 3), 14)

card_w = round(text_w + PAD_X * 2 + 14)  # +14 room for cursor
card_h = round(PAD_TOP + len(lines) * LINE_H + PAD_BOTTOM)

def dim(line: str) -> bool:
    s = line.strip()
    return s.startswith("followers:") or s.startswith("last updated:")

tspans = []
for i, line in enumerate(lines):
    esc = html.escape(line) or " "
    fill = "#8b949e" if dim(line) else "#3fb950"
    dy = 0 if i == 0 else LINE_H
    tspans.append(
        f'<tspan x="{PAD_X}" dy="{dy}" fill="{fill}">{esc}</tspan>'
    )
text_body = "\n      ".join(tspans)

cursor_x = round(PAD_X + text_w + 4)
cursor_y = round(PAD_TOP + (len(lines) - 1) * LINE_H - 11)

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}" role="img" aria-label="Animated ASCII banner">
  <title>Maaz Ahmad — animated ASCII banner</title>
  <rect width="{card_w}" height="{card_h}" rx="8" fill="#0d1117" stroke="#30363d"/>
  <circle cx="20" cy="16" r="4" fill="#ff5f56"/>
  <circle cx="34" cy="16" r="4" fill="#ebc22f"/>
  <circle cx="48" cy="16" r="4" fill="#27c93f"/>
  <clipPath id="reveal">
    <rect x="{PAD_X}" y="12" width="0" height="{card_h}">
      <animate attributeName="width" from="0" to="{round(text_w + 2)}" dur="{type_dur:.1f}s" fill="freeze"/>
    </rect>
  </clipPath>
  <g clip-path="url(#reveal)">
    <text x="{PAD_X}" y="{PAD_TOP}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT_SIZE}" xml:space="preserve">{text_body}
    </text>
  </g>
  <rect x="{cursor_x}" y="{cursor_y}" width="8" height="14" fill="#3fb950" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.45;0.55;1" dur="1s" begin="{type_dur:.1f}s" repeatCount="indefinite"/>
  </rect>
</svg>
"""
DST.write_text(svg, encoding="utf-8")
print(f"Wrote {DST} ({DST.stat().st_size} bytes, {len(lines)} lines, typing {type_dur:.1f}s)")
