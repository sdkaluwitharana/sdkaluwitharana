#!/usr/bin/env python3
"""Generate self-hosted README sections:
  assets/stack/<slug>.svg      one logo tile per technology (big logo + name)
  assets/projects/<slug>.svg   browser-window project cards
  assets/footer.svg            matrix footer with a typewriter that cycles quotes

Content rule: only personal / professional info. Never any server or hosting details.
"""
import json
import os
import random
import re
import textwrap
from html import escape

from stack_data import STACK
from tw_kit import typewriter, typewriter_quotes

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = json.load(open(os.path.join(HERE, "stack-icons.json")))
MONO = "'JetBrains Mono','Fira Code','Cascadia Code','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Inter,Arial,sans-serif"
CYAN, MAG, GRN, DIM, TXT, BG = "#5ee8ff", "#ff6bff", "#5dff8a", "#6b7a8c", "#d6e2ef", "#06090f"

WIN = "".join(f'<rect x="{x}" y="{y}" width="11" height="11" rx="1.2"/>' for x in (0.5, 12.5) for y in (0.5, 12.5))
LOCK = ('<path d="M6 10V7a6 6 0 0 1 12 0v3h1a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V11a1 1 0 0 1 1-1h1zm2 0h8V7'
        'a4 4 0 0 0-8 0v3zm4 4a2 2 0 0 0-1 3.73V20h2v-2.27A2 2 0 0 0 12 14z"/>')


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("+", "p").replace("#", "sharp")).strip("-")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(h):
    r, g, b = (c / 255 for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mix(h, t, k):
    a, b = rgb(h), rgb(t)
    return "#%02x%02x%02x" % tuple(int(x * k + y * (1 - k)) for x, y in zip(a, b))


# ═════════════════════════ stack tiles ═════════════════════════
TILE_W, TILE_H, BOX = 100, 112, 68


def tile(key, label, mono, color):
    bx = (TILE_W - BOX) / 2
    if mono:  # monogram tile (brand has no published logo)
        size = {1: 34, 2: 28, 3: 22, 4: 17}.get(len(mono), 14)
        inner = (f'<text x="{TILE_W / 2}" y="{4 + BOX / 2 + size * 0.36:.1f}" text-anchor="middle" fill="{color}" '
                 f'font-family="{MONO}" font-size="{size}" font-weight="800">{escape(mono)}</text>')
        fill = mix(color, "#141b26", 0.14)
    else:
        if key == "!win":
            c, path = "#4cc2ff", WIN
        elif key == "!lock":
            c, path = "#ffd75e", LOCK
        else:
            ic = ICONS[key]
            c, path = color or "#" + ic["c"], f'<path d="{ic["p"]}"/>'
        L = lum(c)
        if 0.07 < L < 0.62 and not color:      # skillicons look: brand tile, white logo
            fill, logo = c, "#ffffff"
        else:                                    # dark tile, coloured (or light) logo
            fill, logo = "#1d2433", (TXT if L <= 0.07 else c)
        inner = (f'<g transform="translate({TILE_W / 2 - 20} {4 + BOX / 2 - 20}) scale({40 / 24:.4f})" fill="{logo}">'
                 f'{path}</g>')
    lines = textwrap.wrap(label, 15)[:2]
    lab = "".join(f'<text x="{TILE_W / 2}" y="{BOX + 24 + k * 14}" text-anchor="middle" fill="{TXT}" '
                  f'font-size="11.5" font-family="{SANS}" font-weight="600">{escape(l)}</text>'
                  for k, l in enumerate(lines))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{TILE_W}" height="{TILE_H}" viewBox="0 0 {TILE_W} {TILE_H}">
<title>{escape(label)}</title>
<rect x="{bx}" y="4" width="{BOX}" height="{BOX}" rx="16" fill="{fill}"/>
<rect x="{bx + 0.5}" y="4.5" width="{BOX - 1}" height="{BOX - 1}" rx="15.5" fill="none" stroke="#ffffff" stroke-opacity="0.07"/>
{inner}
{lab}
</svg>"""


def build_stack():
    out = os.path.join(HERE, "assets", "stack")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    seen, n = set(), 0
    for _, items in STACK:
        for key, label, _, mono, color in items:
            s = slug(label)
            assert s not in seen, f"duplicate tile {label}"
            seen.add(s)
            open(os.path.join(out, f"{s}.svg"), "w", encoding="utf-8").write(tile(key, label, mono, color))
            n += 1
    print(f"assets/stack/*.svg x{n}")


# ═════════════════════════ project cards (browser window + site logo) ═════════════════════════
import base64
PROJECTS = [
    # (slug, title, domain, url, logo file, path, description)
    ("sdkaluwitharana-lk", "sdkaluwitharana.lk", "sdkaluwitharana.lk", "https://sdkaluwitharana.lk",
     "sdkaluwitharana-lk.png", "~/projects/sdkaluwitharana",
     "Sachith Dilshan Kaluwitharana's web. My personal portfolio, work and writing in one place."),
    ("rap-lms", "RAP LMS", "accountingking.lk", "https://accountingking.lk",
     "rap-lms.png", "~/projects/rap-lms",
     "Learning platform for a leading A/L Accounting tuition master. Courses, class enrolments, exams and payments."),
    ("econ-trust-lms", "Econ Trust LMS", "lms.econtrust.lk", "https://lms.econtrust.lk",
     "econ-trust-lms.png", "~/projects/econtrust",
     "Learning management platform for A/L students, with custom learning flows and a tailored student experience."),
    ("nd-lms", "ND LMS", "namaldilanka.lk", "https://namaldilanka.lk",
     "nd-lms.png", "~/projects/nd-lms",
     "Online class platform for A/L students: course delivery, enrolments and protected learning content."),
    ("bswithdp-lms", "BSwithDP LMS", "deshanpathinayakebs.lk", "https://deshanpathinayakebs.lk",
     "bswithdp-lms.png", "~/projects/bswithdp",
     "Business Studies learning platform for A/L students, built on a fully customised LMS."),
]


def card(i, slug_, title, domain, logo, path, desc):
    W, H = 380, 410
    bar = W - 112
    b64 = base64.b64encode(open(os.path.join(HERE, "assets", "logos", logo), "rb").read()).decode()
    lines = textwrap.wrap(desc, 44)[:3]
    d = "".join(f'<text x="{W / 2}" y="{256 + k * 20}" text-anchor="middle" fill="#9fb0c7" font-size="13.5">'
                f'{escape(l)}</text>' for k, l in enumerate(lines))
    tsize = min(25, 320 / (len(title) * 0.58))
    by = 256 + 3 * 20 + 22  # fixed so every card lines up
    # Logo panel: square for square logos, wider (and white) for wide wordmark logos.
    from PIL import Image
    lw, lh = Image.open(os.path.join(HERE, "assets", "logos", logo)).size
    ar = lw / lh
    ih = 76
    iw = min(150, round(ih * ar)) if ar > 1.15 else 76
    if ar > 1.15:
        ih = round(iw / ar)
    pad = 4
    px, py = W / 2 - iw / 2, 104 + (76 - ih) / 2
    panel = (f'<rect x="{px - pad:.1f}" y="{py - pad:.1f}" width="{iw + 2 * pad}" height="{ih + 2 * pad}" rx="14" fill="#ffffff"/>'
             if ar > 1.15 else
             f'<rect x="{W / 2 - 42}" y="100" width="84" height="84" rx="21" fill="#0e1a30" stroke="#2a4466"/>')
    clip_rx = 10 if ar > 1.15 else 18
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">
<title>{escape(title)} · {escape(domain)}</title>
<defs><clipPath id="r"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<clipPath id="lg"><rect x="{px:.1f}" y="{py:.1f}" width="{iw}" height="{ih}" rx="{clip_rx}"/></clipPath>
<filter id="g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g clip-path="url(#r)">
  <rect width="{W}" height="{H}" fill="#152039"/>
  <rect width="{W}" height="52" fill="#0a1222"/>
  <line x1="0" y1="52" x2="{W}" y2="52" stroke="#24395a"/>
  <circle cx="27" cy="26" r="6.5" fill="#f2665a"/><circle cx="48" cy="26" r="6.5" fill="#f7bd3c"/><circle cx="69" cy="26" r="6.5" fill="#5cc85a"/>
  <rect x="88" y="13" width="{bar}" height="26" rx="6" fill="#111c31"/>
  <text x="{88 + bar / 2}" y="30.5" text-anchor="middle" fill="#7f93ad" font-family="{MONO}" font-size="12.5">{escape(domain)}/</text>
  <text x="22" y="80" fill="#6b7f99" font-family="{MONO}" font-size="12"><tspan fill="{GRN}">0{i + 1}</tspan> · {escape(path)}</text>
  <text x="{W - 22}" y="80" text-anchor="end" fill="#6b7f99" font-family="{MONO}" font-size="12">online</text>
  <circle cx="{W - 22 - 6 * 7.2 - 9}" cy="76" r="4" fill="{GRN}" filter="url(#g)"><animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/></circle>
  {panel}
  <image clip-path="url(#lg)" x="{px:.1f}" y="{py:.1f}" width="{iw}" height="{ih}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{b64}" xlink:href="data:image/png;base64,{b64}"/>
  <text x="{W / 2}" y="226" text-anchor="middle" fill="#f3f6fb" font-size="{tsize:.1f}" font-weight="800">{escape(title)}</text>
  {d}
  <rect x="{W / 2 - 86}" y="{by}" width="172" height="44" rx="22" fill="#5ee8ff" fill-opacity="0.04" stroke="#5ee8ff" stroke-width="1.6"/>
  <text x="{W / 2 - 10}" y="{by + 28}" text-anchor="middle" fill="#6fe3ff" font-size="16" font-weight="700">Visit Website</text>
  <path d="M{W / 2 + 53} {by + 27.5}l8-8m-6.5 0h6.5v6.5" fill="none" stroke="#6fe3ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="23.5" fill="none" stroke="#24395a" stroke-width="1.5"/>
</svg>"""


def build_projects():
    out = os.path.join(HERE, "assets", "projects")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    for i, (slug_, title, domain, url, logo, path, desc) in enumerate(PROJECTS):
        open(os.path.join(out, f"{slug_}.svg"), "w", encoding="utf-8").write(card(i, slug_, title, domain, logo, path, desc))
    print(f"assets/projects/*.svg x{len(PROJECTS)}")


# ═════════════════════════ footer ═════════════════════════
QUOTES = [
    "Thanks for visiting. Let's build something great together.",
    "Keep me in mind, then you can know about me.",
    "History repeats itself.",
    "Doubt everything. Find your own light.",
    "Hatred is never appeased by hatred in this world. By non-hatred alone is hatred appeased. This is a law eternal.",
    "Your purpose in life is to find your purpose and give your whole heart and soul to it.",
    "Every morning we are born again. What we do today is what matters most.",
    "There is no path to happiness: happiness is the path.",
    "If you truly loved yourself, you could never hurt another.",
    "If you do not change direction, you may end up where you are heading.",
    "You will not be punished for your anger; you will be punished by your anger.",
    "Peace comes from within. Do not seek it without.",
    "No one saves us but ourselves. No one can and no one may. We ourselves must walk the path.",
    "Live as if you were to die tomorrow. Learn as if you were to live forever.",
    "Be yourself; everyone else is already taken.",
    "I'm selfish, impatient and a little insecure. I make mistakes, I am out of control and at times hard to "
    "handle. But if you can't handle me at my worst, then you sure as hell don't deserve me at my best.",
    "You only live once, but if you do it right, once is enough.",
    "Don't walk in front of me… I may not follow. Don't walk behind me… I may not lead. "
    "Walk beside me… just be my friend.",
    "If you tell the truth, you don't have to remember anything.",
    "I've learned that people will forget what you said, people will forget what you did, "
    "but people will never forget how you made them feel.",
    "A friend is someone who knows all about you and still loves you.",
    "Always forgive your enemies; nothing annoys them so much.",
    "Be the change that you wish to see in the world.",
]


def matrix(w, h, seed=42, opacity=0.6):
    rnd = random.Random(seed)
    glyphs = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEF<>/{}[]=+*#$%&;:"
    out = []
    for _ in range(int(w / 22) + 1):
        x, n, dur = rnd.uniform(0, w), rnd.randint(8, 16), round(rnd.uniform(4, 10), 2)
        spans = "".join(
            f'<tspan x="{x:.0f}" dy="{18 if j else 0}" fill="{"#eafff4" if j == n - 1 else GRN}" '
            f'opacity="{0.08 + 0.85 * j / (n - 1):.2f}">{escape(rnd.choice(glyphs))}</tspan>' for j in range(n))
        out.append(f'<text font-size="14" y="{-n * 18}">{spans}<animateTransform attributeName="transform" '
                   f'type="translate" from="0 0" to="0 {h + n * 18}" dur="{dur}s" begin="{-rnd.uniform(0, dur):.2f}s" '
                   f'repeatCount="indefinite"/></text>')
    return f'<g opacity="{opacity}">{"".join(out)}</g>'


def build_footer():
    W, H = 1200, 220
    prompt = "sdkaluwitharana@github:~$ "
    typed, cycle = typewriter_quotes(QUOTES, W, 82, 16, CYAN, "q", filt='filter="url(#glow)"')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">
<title>Thanks for visiting. Let's build something great together.</title>
<defs>
  <filter id="glow" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="1.3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity="0.16"/></pattern>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0.35"/><stop offset="1" stop-color="{BG}" stop-opacity="0.85"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  {matrix(W, H)}
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
  {typed}
  <text x="{W / 2}" y="168" text-anchor="middle" font-size="14" xml:space="preserve"><tspan fill="{GRN}">{escape(prompt)}</tspan><tspan fill="{DIM}">exit 0</tspan></text>
  <text x="{W / 2}" y="196" text-anchor="middle" fill="{MAG}" font-size="12" letter-spacing="3">BUILD · DEPLOY · SCALE</text>
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#1b2a36"/>
</svg>"""
    open(os.path.join(HERE, "assets", "footer.svg"), "w", encoding="utf-8").write(svg)
    print(f"assets/footer.svg · {len(QUOTES)} quotes · cycle {cycle:.0f}s")


if __name__ == "__main__":
    build_stack()
    build_projects()
    build_footer()
