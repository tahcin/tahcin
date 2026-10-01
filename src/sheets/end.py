"""SHEET 08: end of job. The bookend to the banner page.

The printhead comes back for one last pass, the job summary is struck, a
STILL BUILDING stamp lands, and a perforated stub at the foot carries the
addresses worth keeping.
"""
import random

from lib import dotmatrix as dm
from lib.fonts import text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PAPER_SHADE, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, shadow, strike
from sheets.hero import carriage_for

H = 560
PITCH = 14


def build(date_str, sheets_total):
    rng = random.Random(97)
    sdefs, sbody = sheet(H, seed=97, uid="e", hole_offset=14)
    head = furniture(8, "END OF JOB", "THANK YOU")

    word = "END OF JOB"
    width = dm.text_width(word, PITCH)
    x0 = (1000 - width) / 2
    top, t0, dur = 106, .4, 1.3
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

    summary = [
        ("SHEETS PRINTED", f"{sheets_total:02d}"),
        ("CASE FILES", "03"),
        ("JOBS LOGGED", "07 + PRIVATE"),
        ("PRINTED ON", date_str.upper()),
        ("NEXT RUN", "TOMORROW, 06:17 UTC"),
    ]
    t, y, sm = t0 + dur + .1, 246, ""
    for k, v in summary:
        g, t = strike(f"{k:<16}{v}", X0, y, t, 150, pitch=2.3)
        sm += g
        y += 26

    voice = (
        f'<g class="ink" {delay(t + .2)}>{text("Voice", "thanks for reading", 548, 268, 40, fill=BLUE)}'
        f'{text("Voice", "the whole printout.", 576, 310, 40, fill=BLUE)}</g>'
    )

    stamp = f"""
<g transform="translate(772 368) rotate(-5)" style="mix-blend-mode:multiply">
 <g class="slam" style="animation-delay:{t + .9:.2f}s;--r0:24deg" filter="url(#wear)" fill="none" stroke="{RED}">
  <rect x="-128" y="-30" width="256" height="60" rx="5" stroke-width="4"/>
  {text("Wide", "STILL BUILDING", 0, 9, 25, tracking=2, anchor="middle", fill=RED, stroke="none")}
 </g>
</g>"""

    # the stub: a perforation across the sheet, then the addresses
    py = 420
    perf = (
        f'<path d="M{X0 - 30} {py}H{X1 + 30}" stroke="{PENCIL}" stroke-width="1.4" stroke-dasharray="2 5"/>'
        f'<path class="pen" {delay(t + 1.5)} pathLength="1" stroke="{BLUE}" stroke-width="2" '
        f'd="M{X0} {py - 10} C{X0 + 40} {py - 16},{X0 + 90} {py - 15},{X0 + 120} {py - 8}"/>'
        + text("Voice", "tear here", X0 + 14, py - 18, 20, fill=BLUE)
    )
    stub_l, _ = strike("KEEP THIS STUB", X0, py + 30, t + 1, 120, pitch=2.6)
    addresses = [
        ("CODE", "GITHUB.COM/TAHCIN"),
        ("RESUME", "TAHCIN.GRADESTONE.IN"),
        ("NOTES", "GRADESTONE.IN"),
    ]
    adr = "".join(
        text("Mono", f"{k:<7}{v}", X0 + (i * 280), py + 82, 12, tracking=.6, fill=INK)
        for i, (k, v) in enumerate(addresses)
    )
    stub_no = text("Mono", "No. 0001", X1, py + 44, 11, tracking=1.2, fill=RED, anchor="end")
    stub_box = f'<rect x="{X0}" y="{py + 56}" width="{X1 - X0}" height="40" fill="none" stroke="{PAPER_SHADE}" stroke-width="1.2"/>'

    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{banner}{head_svg}{sm}{voice}{stamp}{perf}{stub_l}{stub_no}{stub_box}{adr}'
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, BASE_CSS + head_css + ".head{opacity:0}",
        title="End of job",
        desc="End of job. Sheets printed, case files and jobs logged. Stamped STILL BUILDING. "
             "Handwritten: thanks for reading the whole printout. A tear-off stub lists "
             "github.com/tahcin, tahcin.gradestone.in and gradestone.in.",
    )
