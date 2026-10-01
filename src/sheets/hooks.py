"""SHEET 02: research notes. "Luck has hooks."

The phrase comes from the supervisor of Tahcin's luck & serendipity research
at IIM Bangalore. The right half animates it: chance events fall like loose
printer pins; most fall straight through, and a few land in ballpoint hooks
and turn red. The loop is generated from a seed, and its rest state (no
motion) shows the hooks holding what they caught.
"""
import random

from lib.fonts import measure, text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, rule, shadow, strike

H = 704
FIELD = (548, 104, 918, 418)        # x0, y0, x1, y1 of the luck field
HOOKS = [(606, 268), (684, 370), (762, 214), (836, 318), (906, 250)]   # cup bottom points
CYCLE = 7.2


def hook_path(hx, hy):
    return (
        f"M{hx} {FIELD[1]}V{hy - 10}"
        f"C{hx} {hy + 9},{hx - 26} {hy + 9},{hx - 26} {hy - 10}V{hy - 18}"
        f"M{hx - 26} {hy - 18}l8 9"
    )


def falling_pins(rng):
    css, out = [], []
    y_top = FIELD[1] - 10
    pins = [("catch", hx - 13, hy - 7) for hx, hy in HOOKS]
    while len(pins) < 40:
        x = rng.uniform(FIELD[0] + 10, FIELD[2] - 10)
        if all(abs(x - (hx - 13)) > 20 for hx, _ in HOOKS):
            pins.append(("miss", x, FIELD[3] + 12))
    for i, (kind, x, y_end) in enumerate(pins):
        drop = y_end - y_top
        fall = (0.9 + drop / 520) / CYCLE * 100          # % of the cycle spent falling
        start = rng.uniform(0, 100 - fall - 14) if kind == "catch" else 0
        f0, f1 = start, start + fall
        name = f"p{i}"
        g = "animation-timing-function:cubic-bezier(.6,0,.95,.6)"
        if kind == "catch":
            css.append(
                f"@keyframes {name}{{0%,{f0:.1f}%{{opacity:0;fill:{INK};transform:translateY(-{drop:.0f}px);{g}}}"
                f"{f0 + .6:.1f}%{{opacity:1}}"
                f"{f1:.1f}%{{fill:{INK};transform:none}}{f1 + 1.2:.1f}%{{fill:{RED}}}"
                f"94%{{opacity:1;fill:{RED}}}100%{{opacity:0;fill:{RED};transform:none}}}}"
            )
            out.append(
                f'<circle cx="{x:.1f}" cy="{y_end:.1f}" r="6.5" fill="{RED}" '
                f'style="animation:{name} {CYCLE}s linear infinite"/>'
            )
        else:
            css.append(
                f"@keyframes {name}{{0%{{opacity:0;transform:none;{g}}}2%{{opacity:1}}"
                f"{f1:.1f}%{{opacity:1;transform:translateY({drop:.0f}px)}}"
                f"{f1 + .1:.1f}%,100%{{opacity:0;transform:translateY({drop:.0f}px)}}}}"
            )
            out.append(
                f'<circle cx="{x:.1f}" cy="{y_top:.1f}" r="{rng.uniform(4.2, 6):.1f}" fill="{INK}" '
                f'opacity="0" style="animation:{name} {CYCLE}s linear '
                f'-{rng.uniform(0, CYCLE):.2f}s infinite"/>'
            )
    return "".join(out), "".join(css)


def build():
    rng = random.Random(23)
    sdefs, sbody = sheet(H, seed=29, uid="k", hole_offset=12)
    head = furniture(2, "RESEARCH NOTES", "IIMB, WITH PRAGYA & AMRIT")

    # the phrase, pressed in three heavy blows
    words = ["LUCK", "HAS", "HOOKS."]
    pressed = "".join(
        f'<g class="press" {delay(.5 + i * .32)}>{text("Slab", w, X0 - 4, 206 + i * 126, 148, fill=INK)}</g>'
        for i, w in enumerate(words)
    )
    attrib = text("Mono", "A PHRASE FROM OUR SUPERVISOR,", X0, 494, 11.5, tracking=.6, fill=INK, opacity=".75")
    attrib += text("Mono", "PROF. SURESH BHAGAVATULA", X0, 512, 11.5, tracking=.6, fill=INK, opacity=".75")

    # the field: a rail, hooks on pencil lines, falling pins
    rail = rule(FIELD[1], .2, FIELD[0] - 30, FIELD[2] + 2, gap=6, r=1.6)
    hooks = "".join(
        f'<path class="pen" {delay(1.6 + i * .2)} pathLength="1" d="{hook_path(hx, hy)}" '
        f'stroke="{BLUE}" stroke-width="3"/>'
        for i, (hx, hy) in enumerate(HOOKS)
    )
    pins, pin_css = falling_pins(rng)
    field = (
        f'<clipPath id="fc"><rect x="{FIELD[0] - 30}" y="{FIELD[1] - 2}" '
        f'width="{FIELD[2] - FIELD[0] + 50}" height="{FIELD[3] - FIELD[1] + 4}"/></clipPath>'
        f'{rail}<g clip-path="url(#fc)">{pins}</g>{hooks}'
    )
    ly = FIELD[3] + 22
    legend = (
        text("Mono", "FIG. 1  CHANCE, FALLING", FIELD[0] - 30, ly, 10.5, tracking=.8, fill=PENCIL)
        + text("Mono", "CAUGHT", FIELD[2] + 2, ly, 10.5, tracking=.8, fill=RED, anchor="end")
        + f'<circle cx="{FIELD[2] - 58}" cy="{ly - 4}" r="4.5" fill="{RED}"/>'
    )

    # the ballpoint answer, under the figure, arrow pointing on to the next sheet
    vx = 640
    voice = (
        f'<g fill="{BLUE}"><g class="ink" {delay(3.0)}>{text("Voice", "so I keep", vx, 492, 46)}</g>'
        f'<g class="ink" {delay(3.25)}>{text("Voice", "building hooks.", vx + 26, 536, 46)}</g></g>'
    )
    end_x = vx + 26 + measure("Voice", "building hooks.", 46) + 12
    arrow = (
        f'<path class="pen" {delay(3.8)} pathLength="1" stroke="{BLUE}" stroke-width="2.6" '
        f'd="M{end_x - 4:.0f} 512 C{end_x + 18:.0f} 524,{end_x + 14:.0f} 552,{end_x - 2:.0f} 568 '
        f'M{end_x - 2:.0f} 568 l-2 -12 M{end_x - 2:.0f} 568 l11 -5"/>'
    )

    # the definition, struck by the printer
    definition = [
        "SERENDIPITY, N.",
        "A CHANCE EVENT THAT BECOMES VALUABLE ONLY BECAUSE",
        "SOMEONE NOTICED IT, CONNECTED IT TO WHAT THEY KNEW,",
        "AND ACTED ON IT.   (OUR SYNTHESIS OF 17 READINGS)",
    ]
    t, y, deftxt = 2.4, 592, ""
    for line in definition:
        g, t = strike(line, X0, y, t, 170, pitch=2.3)
        deftxt += g
        y += 24

    css = (
        BASE_CSS + pin_css
    )
    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{pressed}{attrib}{field}{legend}'
        f'{rule(578, 2.3, X0, X1)}{deftxt}{voice}{arrow}'
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, css,
        title="Luck has hooks",
        desc="Research notes from a luck and serendipity project at IIM Bangalore. "
             "Headline: LUCK HAS HOOKS. An animated figure shows chance events falling; "
             "a few are caught by hooks. Definition of serendipity: a chance event that "
             "becomes valuable only because someone noticed it, connected it to what they "
             "knew, and acted on it. Handwritten: so I keep building hooks.",
    )
