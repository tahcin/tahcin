"""SHEET 01: the job banner page.

Old line printers opened every job with a banner page: the user's name in
giant letters made of pins, then a block of job fields. This is that page.
The printhead crosses twice, striking TAHCIN then SARWAR column by column,
then a hand annotates it in ballpoint.
"""
import random

from lib import dotmatrix as dm
from lib.fonts import measure, text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, furniture, glyph_defs, shadow, strike

H = 668
PITCH = 24
NAME_TOP = (100, 296)
PASSES = [(0.45, 1.25), (1.85, 1.25)]   # (start, duration) of each head pass


def banner_line(word, top, t0, dur, rng):
    """Giant pins, one <g> per column, timed to the carriage position."""
    width = dm.text_width(word, PITCH)
    out = []
    for col, rows in dm.columns(word):
        if not rows:
            continue
        cx = X0 + col * PITCH + PITCH / 2
        dots = "".join(
            f'<circle cx="{cx + rng.uniform(-.7, .7):.1f}" '
            f'cy="{top + r * PITCH + PITCH / 2 + rng.uniform(-.7, .7):.1f}" '
            f'r="{PITCH * rng.uniform(.425, .455):.1f}" fill-opacity="{rng.uniform(.9, 1):.2f}"/>'
            for r in rows
        )
        out.append(f'<g class="k" {delay(t0 + (cx - X0) / width * dur)}>{dots}</g>')
    return "".join(out)


def carriage_for(x0, width, top, pitch, t0, dur, uid):
    """The printhead for one pass over a banner line: (svg, keyframes css).

    It is only visible while it travels; at rest it is hidden (.head).
    """
    h = 7 * pitch + 22
    w = max(18, pitch * 1.25)
    svg = f"""
<g class="head" style="animation:{uid} {dur + .14:.2f}s linear {t0 - .06:.2f}s both">
  <rect x="{-w / 2:.1f}" y="{top - 11}" width="{w:.1f}" height="{h}" rx="3" fill="#2A2A30"/>
  <rect x="{-w / 2 + 4:.1f}" y="{top - 7}" width="{w - 8:.1f}" height="{h - 8}" rx="2" fill="#3A3A42"/>
  <path d="M-3 {top - 5}V{top + h - 17}" stroke="{RED}" stroke-width="2" opacity=".55"/>
  <rect x="{-w / 2:.1f}" y="{top + h / 2 - h * .13:.1f}" width="{w:.1f}" height="{h * .26:.1f}" fill="#1E1E22"/>
</g>"""
    css = (
        f"@keyframes {uid}{{0%{{opacity:0;transform:translateX({x0}px)}}1%{{opacity:1}}"
        f"92%{{opacity:1;transform:translateX({x0 + width + 6}px)}}"
        f"100%{{opacity:0;transform:translateX({x0 + width + 60}px)}}}}"
    )
    return svg, css


def build(date_str):
    rng = random.Random(7)
    sdefs, sbody = sheet(H, seed=11, uid="h", hole_offset=26)

    head = furniture(1, "PRINTOUT FOR GITHUB.COM/TAHCIN")

    passes, keyframes = "", ""
    for i, (word, top) in enumerate(zip(("TAHCIN", "SARWAR"), NAME_TOP)):
        t0, dur = PASSES[i]
        width = dm.text_width(word, PITCH)
        passes += banner_line(word, top, t0, dur, rng)
        svg, css = carriage_for(X0, width, top, PITCH, t0, dur, f"hp{i}")
        passes += svg
        keyframes += css

    # job fields, struck after the banner
    fields = [
        ("USER", "T. SARWAR"),
        ("SCHOOL", "IIM BANGALORE / BBA"),
        ("DATE", date_str.upper()),
    ]
    t, fy, field_svg = 3.2, 524, ""
    for k, v in fields:
        g, t = strike(f"{k:<8}{v}", X0, fy, t, 140)
        field_svg += g
        fy += 28
    cursor_x = X0 + len(f"{'DATE':<8}{date_str}") * 6 * 2.6 + 4
    cursor = (
        f'<g class="k" {delay(t)}><rect class="blink" x="{cursor_x:.1f}" y="{fy - 28}" '
        f'width="11" height="18" fill="{INK}"/></g>'
    )

    # ballpoint annotation
    vx, vy = 548, 548
    v1, v2 = "builds things,", "studies luck."
    w2 = measure("Voice", v2, 58)
    ux = vx + 40
    voice = (
        f'<g fill="{BLUE}">'
        f'<g class="ink" {delay(4.0)}>{text("Voice", v1, vx, vy, 58)}</g>'
        f'<g class="ink" {delay(4.35)}>{text("Voice", v2, ux, vy + 58, 58)}</g></g>'
        f'<path class="pen" {delay(4.8)} pathLength="1" stroke="{BLUE}" stroke-width="3.2" '
        f'd="M{ux + w2 * .52:.0f} {vy + 72} C{ux + w2 * .7:.0f} {vy + 68},'
        f'{ux + w2 * .92:.0f} {vy + 70},{ux + w2 + 6:.0f} {vy + 66}"/>'
    )

    css = BASE_CSS + keyframes + ".head{opacity:0}"
    inner = (
        f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}{passes}</g>{field_svg}{cursor}{voice}'
    )
    return svg_doc(
        H, inner, css,
        title="TAHCIN SARWAR",
        desc="A dot-matrix banner page printing the name Tahcin Sarwar, with job fields: "
             "IIM Bangalore, BBA. Annotated in ballpoint: builds things, studies luck.",
    )
