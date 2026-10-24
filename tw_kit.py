"""Shared helpers: SMIL typewriter that cycles through lines, and an exact y/m/d "since" calculator."""
import calendar
from datetime import date
from html import escape


def since(start: date, today: date):
    y, m, d = today.year - start.year, today.month - start.month, today.day - start.day
    if d < 0:
        m -= 1
        py, pm = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
        d += calendar.monthrange(py, pm)[1]
    if m < 0:
        y, m = y - 1, m + 12
    return y, m, d


def plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


def ymd_text(start: date, today: date, cap_days=False):
    y, m, d = since(start, today)
    return f"{plural(y, 'year')}, {plural(m, 'month')}, {plural(d, 'Day' if cap_days else 'day')}"


def typewriter(lines, x, y, size, color, cycle, uid, center_w=None, cursor_color=None, weight=700, filt=""):
    """Type each line, hold, erase, next. If center_w is given, each line is centred in that width."""
    cw = size * 0.6
    seg = cycle / len(lines)
    out, ck, cv = [], [], []
    for i, line in enumerate(lines):
        w = len(line) * cw
        x0 = (center_w - w) / 2 if center_w else x
        type_t = min(seg * 0.42, max(0.9, 0.045 * len(line)))
        erase_t = 0.45
        hold_t = seg - type_t - erase_t - 0.2
        t0 = i * seg
        pts = [(0.0, 0), (t0, 0), (t0 + type_t, w), (t0 + type_t + hold_t, w), (t0 + type_t + hold_t + erase_t, 0), (cycle, 0)]
        dd = []
        for t, v in pts:
            if dd and abs(dd[-1][0] - t) < 1e-6:
                dd[-1] = (t, v)
            else:
                dd.append((t, v))
        kt = ";".join(f"{t / cycle:.4f}" for t, _ in dd)
        vals = ";".join(f"{v:.1f}" for _, v in dd)
        out.append(
            f'<clipPath id="{uid}{i}"><rect x="{x0:.1f}" y="{y - size - 2}" height="{size + 10}" width="0">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/>'
            f'</rect></clipPath>'
            f'<text x="{x0:.1f}" y="{y}" clip-path="url(#{uid}{i})" fill="{color}" font-size="{size}" font-weight="{weight}" '
            f'{filt} xml:space="preserve" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs">{escape(line)}</text>')
        for t, v in pts[1:5]:
            ck.append(t / cycle)
            cv.append(x0 + v + (3 if v else 0))
    if ck[0] > 0:
        ck.insert(0, 0.0)
        cv.insert(0, cv[0])
    ck.append(1.0)
    cv.append(cv[1])
    cur = (f'<rect y="{y - size + 1}" width="{size * 0.6:.1f}" height="{size + 3}" fill="{cursor_color or color}">'
           f'<animate attributeName="x" values="{";".join(f"{v:.1f}" for v in cv)}" '
           f'keyTimes="{";".join(f"{k:.4f}" for k in ck)}" dur="{cycle}s" repeatCount="indefinite"/>'
           f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    return "\n".join(out) + "\n" + cur


def typewriter_quotes(quotes, width, y0, size, color, uid, line_h=26, wrap=96, cps=34, hold=3.2,
                      cursor_color=None, filt=""):
    """Cycle quotes; long ones wrap onto several centred lines that are typed one after another.

    Each quote: type (len/cps seconds), hold (hold + 0.02s per char), erase all lines together.
    The block of lines is vertically centred around y0.
    """
    import textwrap as _tw
    cw = size * 0.6
    plans, t = [], 0.0
    for q in quotes:
        lines = _tw.wrap(q, wrap)
        typing = [len(l) / cps for l in lines]
        hold_t = hold + 0.02 * len(q)
        seg = sum(typing) + hold_t + 0.5 + 0.3
        plans.append((lines, typing, hold_t, t, seg))
        t += seg
    cycle = t
    out, ck, cv_x, cv_y = [], [], [], []

    def kt(pts):
        dd = []
        for tt, v in pts:
            if dd and abs(dd[-1][0] - tt) < 1e-6:
                dd[-1] = (tt, v)
            else:
                dd.append((tt, v))
        return ";".join(f"{a / cycle:.5f}" for a, _ in dd), ";".join(f"{v:.1f}" for _, v in dd)

    for qi, (lines, typing, hold_t, t0, seg) in enumerate(plans):
        n = len(lines)
        top = y0 - (n - 1) * line_h / 2
        end_type = t0 + sum(typing)
        erase_s, erase_e = end_type + hold_t, end_type + hold_t + 0.5
        ts = t0
        for li, line in enumerate(lines):
            w = len(line) * cw
            x0 = (width - w) / 2
            y = top + li * line_h
            te = ts + typing[li]
            k, v = kt([(0, 0), (ts, 0), (te, w), (erase_s, w), (erase_e, 0), (cycle, 0)])
            out.append(
                f'<clipPath id="{uid}{qi}_{li}"><rect x="{x0:.1f}" y="{y - size - 2:.1f}" height="{size + 10}" width="0">'
                f'<animate attributeName="width" values="{v}" keyTimes="{k}" dur="{cycle:.2f}s" repeatCount="indefinite"/>'
                f'</rect></clipPath>'
                f'<text x="{x0:.1f}" y="{y:.1f}" clip-path="url(#{uid}{qi}_{li})" fill="{color}" font-size="{size}" '
                f'font-weight="700" {filt} xml:space="preserve" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs">'
                f'{escape(line)}</text>')
            # cursor path: jump to line start, travel to line end
            ck += [ts / cycle, te / cycle]
            cv_x += [x0, x0 + w + 3]
            cv_y += [y, y]
            ts = te
        # hold at end of last line, then park at its start during erase
        ck += [erase_s / cycle, erase_e / cycle]
        cv_x += [cv_x[-1], (width - len(lines[-1]) * cw) / 2]
        cv_y += [cv_y[-1], cv_y[-1]]
    ck = [0.0] + ck + [1.0]
    cv_x = [cv_x[0]] + cv_x + [cv_x[0]]
    cv_y = [cv_y[0]] + cv_y + [cv_y[0]]
    # discrete y jumps, linear x
    cur = (f'<rect width="{size * 0.6:.1f}" height="{size + 3}" fill="{cursor_color or color}">'
           f'<animate attributeName="x" values="{";".join(f"{v:.1f}" for v in cv_x)}" '
           f'keyTimes="{";".join(f"{k:.5f}" for k in ck)}" dur="{cycle:.2f}s" repeatCount="indefinite"/>'
           f'<animate attributeName="y" values="{";".join(f"{v - size + 1:.1f}" for v in cv_y)}" '
           f'keyTimes="{";".join(f"{k:.5f}" for k in ck)}" dur="{cycle:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'
           f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    return "\n".join(out) + "\n" + cur, cycle
