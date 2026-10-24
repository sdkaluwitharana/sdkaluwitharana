#!/usr/bin/env python3
"""Generate hacker-style social badges (badges/*.svg) that match cover.svg.

LinkedIn / WhatsApp icon paths come from simple-icons (CC0); the globe and envelope are drawn here.
"""
import json
import os
from html import escape

MONO = "'JetBrains Mono','Fira Code','Cascadia Code','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
CYAN, GRN, TXT, BG, BORDER = "#5ee8ff", "#5dff8a", "#d6e2ef", "#0b1118", "#1f6f7d"

icons = {k.lower(): v["p"] for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stack-icons.json"))).items()}
icons.update(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons.json"))))

def si(path):  # simple-icons 24x24 path
    return f'<path d="{path}"/>'

GLOBE = ('<g fill="none" stroke-width="2"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.2" ry="10"/>'
         '<path d="M2 12h20M4 6.5h16M4 17.5h16"/></g>')
MAIL = ('<g fill="none" stroke-width="2" stroke-linejoin="round"><rect x="2" y="4.5" width="20" height="15" rx="2"/>'
        '<path d="M2.8 6l9.2 7 9.2-7"/></g>')

BADGES = [
    ("linkedin", "LinkedIn", si(icons["linkedin"]), True),
    ("whatsapp", "WhatsApp Channel", si(icons["whatsapp"]), True),
    ("website", "Website", GLOBE, False),
    ("email", "Email", MAIL, False),
    ("wikipedia", "Wikipedia", si(icons["wikipedia"]), True),
    ("x", "X", si(icons["x"]), True),
    ("blog", "Blog", si(icons["blogger"]), True),
]

FS = 14
CW = FS * 0.6
H = 40
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "badges")
os.makedirs(OUT, exist_ok=True)
for slug, label, icon, filled in BADGES:
    text = label.upper()
    tw = len(text) * CW + len(text) * 1.6          # letter-spacing 1.6
    w = int(14 + 20 + 10 + 10 + tw + 16)           # pad, icon, gap, prompt, text, pad
    paint = f'fill="{CYAN}"' if filled else f'stroke="{CYAN}"'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" font-family="{MONO}">
<title>{escape(label)}</title>
<defs><filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="1.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect x="0.5" y="0.5" width="{w-1}" height="{H-1}" rx="7" fill="{BG}" stroke="{BORDER}"/>
<rect x="0.5" y="0.5" width="3" height="{H-1}" rx="1.5" fill="{GRN}" opacity="0.85"/>
<g transform="translate(14 10) scale(0.8333)" {paint} filter="url(#g)">{icon}</g>
<text x="44" y="25.5" fill="{GRN}" font-size="{FS}" font-weight="700">&gt;</text>
<text x="56" y="25.5" fill="{TXT}" font-size="{FS}" font-weight="700" letter-spacing="1.6" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>
</svg>
"""
    open(os.path.join(OUT, f"{slug}.svg"), "w", encoding="utf-8").write(svg)
    print(f"badges/{slug}.svg  {w}x{H}")
