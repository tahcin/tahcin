"""SHEET 08: end of job. The bookend to the banner page.

The printhead comes back for one last pass, a line of thanks is written
under it, and a perforated stub at the foot carries the addresses worth
keeping.
"""
import random

from lib import dotmatrix as dm
from lib.fonts import text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, shadow, strike
from sheets.hero import carriage_for

H = 500
PITCH = 14


def build(date_str):
    rng = random.Random(97)
    sdefs, sbody = sheet(H, seed=97, uid="e", hole_offset=14)
    head = furniture(8, "END OF JOB")

    word = "END OF JOB"
    width = dm.text_width(word, PITCH)
    x0 = (1000 - width) / 2
    top, t0, dur = 112, .4, 1.3
    pins = []
    for col, rows in dm.columns(word):
        if not rows:
            continue
        cx = x0 + col * PITCH + PITCH / 2
        dots = "".join(
            f'<circle cx="{cx + rng.uniform(-.5, .5):.1f}" cy="{top + r * PITCH + PITCH / 2 + rng.uniform(-.5, .5):.1f}" '
            f'r="{PITCH * rng.uniform(.42, .45):.1f}"/>'
            for r in rows
        )
        pins.append(f'<g class="k" {delay(t0 + (cx - x0) / width * dur)}>{dots}</g>')
    banner = f'<g fill="{INK}">{"".join(pins)}</g>'
    head_svg, head_css = carriage_for(x0, width, top, PITCH, t0, dur, "he")

    t = t0 + dur + .3
    thanks = (
        f'<g class="ink" {delay(t)}>'
        f'{text("Voice", "thanks for reading the whole printout.", 500, 296, 40, anchor="middle", fill=BLUE)}</g>'
    )
    line = f"PRINTED {date_str.upper()}.  REPRINTED EVERY MORNING."
    end_x = 500 + dm.text_width(line, 1.9) / 2
    printed, t_line = strike(line, end_x, 322, t + .4, 160, pitch=1.9, anchor="end")
    printed += (f'<g class="k" {delay(t_line)}><rect class="blink" x="{end_x + 6:.1f}" y="321" '
                f'width="8" height="14" fill="{INK}"/></g>')

    # the stub
    py = 380
    perf = (
        f'<path d="M{X0 - 30} {py}H{X1 + 30}" stroke="{PENCIL}" stroke-width="1.4" stroke-dasharray="2 5"/>'
        + text("Voice", "tear here", X1, py - 10, 19, fill=PENCIL, anchor="end")
    )
    keep, _ = strike("KEEP THIS STUB", X0, py + 26, t + 1, 120, pitch=2.2)
    addresses = [("CODE", "GITHUB.COM/TAHCIN"), ("RESUME", "TAHCIN.GRADESTONE.IN"), ("NOTES", "GRADESTONE.IN")]
    slot = (X1 - X0) / 3
    adr = "".join(
        text("Mono", k, X0 + i * slot, py + 72, 9, tracking=1.6, fill=PENCIL)
        + text("Mono", v, X0 + i * slot, py + 92, 12.5, tracking=.6, fill=INK)
        for i, (k, v) in enumerate(addresses)
    )

    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{banner}{head_svg}{thanks}{printed}{perf}{keep}{adr}'
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, BASE_CSS + head_css + ".head{opacity:0}",
        title="End of job",
        desc="End of job. Handwritten: thanks for reading the whole printout. Reprinted every "
             "morning. A tear-off stub lists github.com/tahcin, tahcin.gradestone.in and gradestone.in.",
    )
