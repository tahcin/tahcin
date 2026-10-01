"""Shared marks every sheet makes: struck lines, rules, page furniture."""
from lib import dotmatrix as dm
from lib.motion import delay
from lib.paper import INK, W

X0 = 80          # left edge of the printable area
X1 = W - 80      # right edge
SMALL = 2.6      # pin pitch of small dot-matrix text


_USED = {}


def _glyph_id(ch, pitch):
    gid = f"g{ord(ch):x}-{str(pitch).replace('.', '_')}"
    if gid not in _USED:
        _USED[gid] = dm.path_d(ch, 0, 0, pitch, pitch * .78)
    return gid


def glyph_defs():
    """<path> defs for every dot-matrix glyph struck since the last call."""
    out = "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in _USED.items())
    _USED.clear()
    return out


def strike(text, x, y, t0, speed=120, pitch=SMALL, fill=INK, anchor="start"):
    """A dot-matrix line struck char by char. Returns (svg, t_end).

    Each glyph is defined once (see glyph_defs) and placed with <use>.
    """
    if anchor == "end":
        x -= dm.text_width(text, pitch)
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        gid = _glyph_id(ch, pitch)
        out.append(
            f'<use class="k" {delay(t0 + i / speed)} href="#{gid}" '
            f'x="{x + i * 6 * pitch:.1f}" y="{y}"/>'
        )
    return f'<g fill="{fill}">{"".join(out)}</g>', t0 + len(text) / speed


def rule(y, t0=0.0, x0=X0, x1=X1, gap=7, r=1.3, speed=260):
    n = int((x1 - x0) / gap) + 1
    dots = "".join(
        f'<circle class="k" {delay(t0 + i / speed)} cx="{x0 + i * gap + 2:.0f}" cy="{y}" r="{r}"/>'
        for i in range(n)
    )
    return f'<g fill="{INK}" opacity=".7">{dots}</g>'


def furniture(sheet_no, left, right, t0=0.0):
    """The header every sheet carries: job line, sheet number, dotted rule."""
    a, _ = strike(f"SHEET {sheet_no:02d}   {left}", X0, 40, t0)
    b, _ = strike(right, X1, 40, t0 + .2, anchor="end")
    return a + b + rule(72, t0)


FILTERS = """
<filter id="wear" x="-10%" y="-20%" width="120%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency=".55" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.3 1.32" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in"/>
</filter>
<filter id="lift" x="-5%" y="-5%" width="110%" height="115%">
  <feGaussianBlur stdDeviation="6"/>
</filter>"""


def shadow(sheet_defs):
    """A soft cast shadow under the sheet so it lifts off GitHub's light theme."""
    start = sheet_defs.index('<path d="') + 9
    outline = sheet_defs[start:sheet_defs.index('"', start)]
    return (
        f'<path d="{outline}" transform="translate(0 5)" fill="#000" '
        f'opacity=".16" filter="url(#lift)"/>'
    )
