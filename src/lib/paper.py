"""Continuous-form paper: the substrate every asset is printed on.

A sheet is fanfold computer paper: tractor-feed margins with sprocket holes
(punched through, so GitHub's own background shows through them), a
perforated tear line inside each margin, faint guide bars, and torn
perforated edges top and bottom. Every sheet is generated from a seed, so
no two tears are identical but every build is reproducible.
"""
import random
from xml.sax.saxutils import escape

W = 1000          # every asset shares this coordinate width
MARGIN = 46       # tractor-feed strip width
HOLE_PITCH = 40   # sprocket hole spacing
HOLE_R = 7.5

PAPER = "#F2EDE1"
PAPER_SHADE = "#E6DFCF"
BAR = "#E5EBDD"   # the faint green bar of greenbar paper
INK = "#18181B"
RED = "#D8362A"   # rubber stamp
BLUE = "#2A3FD0"  # ballpoint
PENCIL = "#8C877B"


def torn_edge(y, rng, x0=0, x1=W, amp=3.2, step=7, down=True):
    """A torn perforation as a polyline from x0 to x1 around y."""
    pts = []
    x = x0
    while x < x1:
        jitter = rng.uniform(-amp, amp)
        pts.append((x, y + jitter))
        x += rng.uniform(step * 0.5, step * 1.4)
    pts.append((x1, y + rng.uniform(-amp, amp)))
    return pts


def sheet_path(h, seed, top="torn", bottom="torn"):
    """Outline of a sheet (with torn or straight top/bottom) as a path d."""
    rng = random.Random(seed)
    top_pts = torn_edge(6, rng) if top == "torn" else [(0, 0), (W, 0)]
    bot_pts = torn_edge(h - 6, rng) if bottom == "torn" else [(0, h), (W, h)]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in top_pts)
    d += " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(bot_pts))
    return d + "Z"


def holes_path(h, offset=20):
    """Sprocket holes for both margins, as one path (used as a cut-out)."""
    parts = []
    y = offset
    while y < h - 8:
        for cx in (MARGIN / 2, W - MARGIN / 2):
            r = HOLE_R
            parts.append(
                f"M{cx - r:.1f} {y:.1f}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0z"
            )
        y += HOLE_PITCH
    return "".join(parts)


def sheet(h, seed, top="torn", bottom="torn", bars=True, uid="s", hole_offset=20, extra_holes=""):
    """Return (defs, body) SVG fragments for a full-width sheet of height h.

    extra_holes: path data punched through the sheet as well (see timecard).
    The mask is exposed as #{uid}-mask so objects laid on the sheet can share it.
    """
    outline = sheet_path(h, seed, top, bottom)
    holes = holes_path(h, hole_offset) + extra_holes
    defs = f"""
<clipPath id="{uid}-clip"><path d="{outline}"/></clipPath>
<mask id="{uid}-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{h}">
  <path d="{outline}" fill="#fff"/><path d="{holes}" fill="#000"/>
</mask>
<filter id="{uid}-grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="{seed % 97}" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 .35  0 0 0 0 .32  0 0 0 0 .26  0 0 0 -1.1 .62"/>
  <feComposite in2="SourceGraphic" operator="in"/>
</filter>"""
    bar_rects = ""
    if bars:
        # greenbar: alternating bands, each two dot-matrix lines tall
        y = 0
        band = 48
        i = 0
        while y < h:
            if i % 2 == 0:
                bar_rects += f'<rect x="{MARGIN + 14}" y="{y}" width="{W - 2 * MARGIN - 28}" height="{band}"/>'
            y += band
            i += 1
        bar_rects = f'<g fill="{BAR}" opacity=".55">{bar_rects}</g>'
    perf = (
        f'<path d="M{MARGIN} 0V{h}M{W - MARGIN} 0V{h}" stroke="{PAPER_SHADE}" '
        f'stroke-width="1.4" stroke-dasharray="3 4"/>'
    )
    body = f"""
<g mask="url(#{uid}-mask)">
  <rect width="{W}" height="{h}" fill="{PAPER}"/>
  {bar_rects}
  <rect width="{W}" height="{h}" fill="{PAPER}" filter="url(#{uid}-grain)" opacity=".5"/>
  {perf}
</g>"""
    return defs, body


def svg_doc(h, inner, css="", title="", desc=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" '
        f'width="{W}" height="{h}" role="img" aria-labelledby="t d">'
        f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
        f"<style>{css}</style>{inner}</svg>"
    )
