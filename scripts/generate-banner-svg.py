#!/usr/bin/env python3
"""Generate an animated SVG banner: handwritten signature + typing ASCII art.

Reads ascii-banner.txt and renders a terminal-style card:
  1. "Maaz Ahmad" draws itself like handwriting (stroke-draw + fill fade,
     script font, plus an underline flourish).
  2. The figlet block types out line-by-line, each line clipped by its own
     chained SMIL animation, with a block cursor that travels with the text.
  3. Cursor blinks at the end. No third-party dependencies — stdlib only.
"""
import html
import sys
from pathlib import Path

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ascii-banner.txt")
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("banner.svg")
SIGNATURE = "Maaz Ahmad"

FONT_SIZE = 13
CHAR_W = 7.8        # approx monospace advance at 13px
LINE_H = 17
PAD_X = 24
ASCII_RATE = 0.022  # seconds per char for the figlet block
STATS_RATE = 0.060  # seconds per char for the stats lines
STATS_PAUSE = 0.4   # pause before the stats lines start

SIG_BEGIN = 0.2
SIG_DUR = 2.5       # handwriting stroke duration
FLOURISH_DUR = 0.8

lines = SRC.read_text(encoding="utf-8").splitlines() or [" "]
max_len = max(len(l) for l in lines)
text_w = max_len * CHAR_W

SIG_Y = 52
ASCII_TOP = 100  # baseline of first ascii line

def is_stats(line: str) -> bool:
    s = line.strip()
    return s.startswith("followers:") or s.startswith("last updated:")

# Baselines for every row (blanks keep their spacing, get no clip).
baselines = [ASCII_TOP + i * LINE_H for i in range(len(lines))]
typed = [(i, l) for i, l in enumerate(lines) if l.strip()]

# --- Schedule: signature first, then ascii, pause, then stats ---
t = SIG_BEGIN + SIG_DUR + 0.3 + FLOURISH_DUR + 0.2  # ascii starts here
ASCII_START = t
spans = []  # (line_index, begin, dur)
for i, l in typed:
    rate = STATS_RATE if is_stats(l) else ASCII_RATE
    spans.append((i, l, t, max(len(l) * rate, 0.3)))
    t += spans[-1][3]
    # pause right before the first stats line
    if not is_stats(l):
        nxt = typed[typed.index((i, l)) + 1] if (i, l) != typed[-1] else None
        if nxt is not None and is_stats(nxt[1]):
            t += STATS_PAUSE
TOTAL = t

card_w = round(max(text_w + PAD_X * 2 + 14, 420))
card_h = round(baselines[-1] + 24)
flourish_y = SIG_Y + 14
flourish_end = SIG_BEGIN + SIG_DUR + 0.3 + FLOURISH_DUR

# --- Per-line clips, chained like L(n-1).end ---
clips = []
groups = []
prev_id = None
for n, (i, l, b, d) in enumerate(spans):
    cid = f"clipL{n}"
    begin = f"{b:.3f}s" if prev_id is None else f"{prev_id}.end"
    if n > 0 and is_stats(l) and not is_stats(spans[n - 1][1]):
        # re-anchor after the stats pause (chain breaks across the gap)
        begin = f"{b:.3f}s"
    w = round(len(l) * CHAR_W + 2, 1)
    y = round(baselines[i] - 13)
    clips.append(
        f'    <clipPath id="{cid}">\n'
        f'      <rect x="{PAD_X}" y="{y}" width="0" height="16">\n'
        f'        <animate id="L{n}" attributeName="width" from="0" to="{w}" '
        f'begin="{begin}" dur="{d:.3f}s" fill="freeze"/>\n'
        f'      </rect>\n'
        f'    </clipPath>'
    )
    esc = html.escape(l)
    fill = "#8b949e" if is_stats(l) else "#3fb950"
    groups.append(
        f'    <g clip-path="url(#{cid})">\n'
        f'      <text x="{PAD_X}" y="{baselines[i]}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="{FONT_SIZE}" fill="{fill}" xml:space="preserve">{esc}</text>\n'
        f'    </g>'
    )
    prev_id = f"L{n}"

# --- Traveling cursor: jumps to each line start, runs to its end ---
xs, ys, ks = [str(PAD_X)], [str(round(baselines[spans[0][0]] - 11))], ["0.0000"]
for i, l, b, d in spans:
    e = b + d
    x1 = round(PAD_X + len(l) * CHAR_W, 1)
    y = round(baselines[i] - 11)
    xs += [str(PAD_X), str(x1)]
    ys += [str(y), str(y)]
    ks += [f"{b / TOTAL:.4f}", f"{e / TOTAL:.4f}"]
cursor = (
    f'  <rect width="8" height="14" fill="#3fb950" opacity="0">\n'
    f'    <animate attributeName="x" values="{";".join(xs)}" keyTimes="{";".join(ks)}" '
    f'dur="{TOTAL:.3f}s" begin="0s" fill="freeze"/>\n'
    f'    <animate attributeName="y" values="{";".join(ys)}" keyTimes="{";".join(ks)}" '
    f'dur="{TOTAL:.3f}s" begin="0s" fill="freeze" calcMode="discrete"/>\n'
    f'    <animate attributeName="opacity" from="0" to="1" dur="0.1s" '
    f'begin="{ASCII_START:.3f}s" fill="freeze"/>\n'
    f'    <animate attributeName="opacity" values="1;1;0;1" keyTimes="0;0.45;0.55;1" '
    f'dur="1s" begin="{TOTAL:.3f}s" repeatCount="indefinite"/>\n'
    f'  </rect>'
)

clips_block = "\n".join(clips)
groups_block = "\n".join(groups)
svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}" role="img" aria-label="Animated ASCII banner">
  <title>Maaz Ahmad — animated ASCII banner</title>
  <rect width="{card_w}" height="{card_h}" rx="8" fill="#0d1117" stroke="#30363d"/>
  <circle cx="20" cy="16" r="4" fill="#ff5f56"/>
  <circle cx="34" cy="16" r="4" fill="#ebc22f"/>
  <circle cx="48" cy="16" r="4" fill="#27c93f"/>
  <text x="{PAD_X}" y="{SIG_Y}" font-family="'Segoe Script','Brush Script MT','Apple Chancery','Comic Sans MS',cursive" font-size="36" fill="#58a6ff" fill-opacity="0" stroke="#58a6ff" stroke-width="1" stroke-dasharray="280" stroke-dashoffset="280">{html.escape(SIGNATURE)}<animate attributeName="stroke-dashoffset" from="280" to="0" dur="{SIG_DUR:.1f}s" begin="{SIG_BEGIN:.1f}s" fill="freeze"/><animate attributeName="fill-opacity" from="0" to="1" dur="0.8s" begin="{(SIG_BEGIN + SIG_DUR - 0.3):.1f}s" fill="freeze"/></text>
  <path d="M{PAD_X},{flourish_y} C150,{flourish_y + 12} 300,{flourish_y - 14} {card_w - PAD_X},{flourish_y}" stroke="#3fb950" stroke-width="2" fill="none" stroke-dasharray="600" stroke-dashoffset="600"><animate attributeName="stroke-dashoffset" from="600" to="0" dur="{FLOURISH_DUR:.1f}s" begin="{(SIG_BEGIN + SIG_DUR + 0.3):.1f}s" fill="freeze"/></path>
{clips_block}
{groups_block}
{cursor}
</svg>
"""
DST.write_text(svg, encoding="utf-8")
print(f"Wrote {DST} ({DST.stat().st_size} bytes, signature + {len(spans)} typed lines, total {TOTAL:.1f}s)")
