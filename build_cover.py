#!/usr/bin/env python3
"""Generate cover.svg: cinematic hacker-style profile header for github.com/sdkaluwitharana.

Pure SVG + SMIL animation (no scripts, no web fonts), so GitHub renders it inside a README <img>.
Requires: pip install pyfiglet
"""
import random
from html import escape

import os
from datetime import date, datetime, timedelta, timezone

import pyfiglet

from tw_kit import typewriter, ymd_text

random.seed(20020212)

W, H = 1200, 424
MONO = "'JetBrains Mono','Fira Code','Cascadia Code','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
CYAN, MAG, GRN, DIM, BG = "#5ee8ff", "#ff6bff", "#5dff8a", "#6b7a8c", "#06090f"

# ───────────── matrix rain ─────────────
GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEF<>/{}[]=+*#$%&;:"
COL_W, CH_H = 22, 18
cols = []
for i in range(W // COL_W + 1):
    x = i * COL_W + 8
    n = random.randint(12, 22)
    dur = round(random.uniform(4.5, 11.0), 2)
    begin = round(-random.uniform(0, dur), 2)
    spans = []
    for j in range(n):
        t = j / (n - 1)
        fill = "#eafff4" if j == n - 1 else GRN
        spans.append(f'<tspan x="{x}" dy="{CH_H if j else 0}" fill="{fill}" opacity="{0.08 + 0.85 * t:.2f}">'
                     f'{escape(random.choice(GLYPHS))}</tspan>')
    cols.append(f'<text font-size="{random.choice([13, 14, 15])}" y="{-n * CH_H}">{"".join(spans)}'
                f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {H + n * CH_H}" '
                f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></text>')
matrix = "\n".join(cols)

# ───────────── figlet name ─────────────
FIG_SIZE, FIG_LH = 14.6, 17.2
FIG_CW = FIG_SIZE * 0.6

def figlet(txt, y0):
    lines = [l.rstrip() for l in pyfiglet.figlet_format(txt, font="slant", width=300).split("\n")]
    while lines and not lines[-1].strip():
        lines.pop()
    w = max(map(len, lines))
    px = w * FIG_CW
    x0 = (W - px) / 2
    svg = "\n".join(f'<text x="{x0:.1f}" y="{y0 + k * FIG_LH:.1f}" xml:space="preserve" textLength="{px:.1f}" '
                    f'lengthAdjust="spacingAndGlyphs">{escape(l.ljust(w))}</text>' for k, l in enumerate(lines))
    return svg, y0 + len(lines) * FIG_LH

y = 92
fig1, y = figlet("Sachith Dilshan", y)
fig2, y = figlet("Kaluwitharana", y + 6)
sub_y = y + 18
sub2_y = sub_y + 24
rule_y = sub2_y + 28

# ───────────── typewriter ─────────────
# GITHUB_JOINED is set by the workflow from the GitHub API (created_at). Fallback = estimate for local previews.
JOINED = date.fromisoformat(os.environ.get("GITHUB_JOINED", "2019-07-01")[:10])
TODAY = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
LX = 60
PROMPT = "sdkaluwitharana@github:~$ "
LINES = [
    f"Joined {ymd_text(JOINED, TODAY, cap_days=True)} ago",
    "Input  →  Process  →  Output",
    "Build  →  Deploy  →  Scale",
    "Create  →  Read  →  Update  →  Delete",
    "Planning → Analysis → Requirements → Design → Development → Testing → Deployment → Maintenance",
]
TW_SIZE = 15
prompt_y = rule_y + 44
prompt_w = len(PROMPT) * TW_SIZE * 0.6
typed = typewriter(LINES, LX + prompt_w, prompt_y, TW_SIZE, CYAN, 27.5, "tw")

# ───────────── assemble ─────────────
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="14">
<title>Sachith Dilshan Kaluwitharana · CEO · Developer · Designer · Editor · Admin · Software Engineer · Writer · Creator · Thinker · Builder · Computer Science Undergraduate</title>
<defs>
  <radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#0d1a22"/><stop offset="0.65" stop-color="{BG}"/><stop offset="1" stop-color="#000"/></radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="0.1"/><stop offset="0.3" stop-color="{BG}" stop-opacity="0.6"/>
    <stop offset="0.8" stop-color="{BG}" stop-opacity="0.7"/><stop offset="1" stop-color="{BG}" stop-opacity="0.5"/>
  </linearGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity="0.18"/></pattern>
  <filter id="glow" x="-10%" y="-40%" width="120%" height="180%">
    <feGaussianBlur stdDeviation="2.2" result="b"/><feComponentTransfer in="b" result="b2"><feFuncA type="linear" slope="0.45"/></feComponentTransfer>
    <feMerge><feMergeNode in="b2"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow2" x="-10%" y="-40%" width="120%" height="180%">
    <feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <g opacity="0.8">
{matrix}
  </g>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
  <rect width="{W}" height="{H}" fill="url(#scan)"/>

  <!-- terminal window chrome -->
  <rect width="{W}" height="34" fill="#0b1118" opacity="0.92"/>
  <circle cx="24" cy="17" r="6" fill="#ff5f57"/><circle cx="44" cy="17" r="6" fill="#febc2e"/><circle cx="64" cy="17" r="6" fill="#28c840"/>
  <text x="{W/2}" y="22" text-anchor="middle" fill="{DIM}" font-size="13">sdkaluwitharana — zsh — 120×32</text>
  <line x1="0" y1="34" x2="{W}" y2="34" stroke="#1b2a36"/>

  <g fill="{CYAN}" font-size="{FIG_SIZE}" font-weight="600" filter="url(#glow)">
{fig1}
{fig2}
  </g>

  <text x="{W/2}" y="{sub_y}" text-anchor="middle" fill="{MAG}" font-size="15" font-weight="700" letter-spacing="1" filter="url(#glow2)">CEO · Developer · Designer · Editor · Admin · Software Engineer · Writer</text>
  <text x="{W/2}" y="{sub2_y}" text-anchor="middle" fill="{MAG}" font-size="15" font-weight="700" letter-spacing="1" filter="url(#glow2)">Creator · Thinker · Builder · Computer Science Undergraduate</text>
  <line x1="{LX}" y1="{rule_y}" x2="{W-LX}" y2="{rule_y}" stroke="{DIM}" stroke-opacity="0.6" stroke-dasharray="2 2"/>

  <text x="{LX}" y="{prompt_y}" fill="{GRN}" font-weight="700" font-size="{TW_SIZE}" xml:space="preserve" textLength="{prompt_w:.1f}" lengthAdjust="spacingAndGlyphs">{escape(PROMPT)}</text>
  <g font-size="{TW_SIZE}" font-weight="700">
{typed}
  </g>
</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="#1b2a36"/>
</svg>
"""
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.svg"), "w", encoding="utf-8") as f:
    f.write(svg)
print(f"cover.svg: {len(svg)/1024:.1f} KB, prompt_y={prompt_y}, H={H}")
