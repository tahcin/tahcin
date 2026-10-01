"""SHEET 03: case file, Parchi.

Same grammar as the other case files: one figure in pins, a short story,
a ballpoint aside, the title set big. The figure is the problem Parchi
answers: of every 1,000 farmers, government extension staff reach about
68 (6.8%, ICRISAT, cited in Parchi's README). Everyone else is advised by
the dealer who sells them the pesticide, on a chit.

The red headline is Parchi's own verdict string (`danger` in its
src/lib/i18n.ts), cycling through all eleven of its languages.
"""
import json
import os
import random

from lib.fonts import FACES, glyphs, measure, register, text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, rule, shadow, strike

H = 722
GRID = (80, 150, 40, 25, 11)      # x0, y0, columns, rows, pitch: 1,000 farmers
REACHED = 68                       # 6.8% reached by extension staff
LANG_STEP = 1.8

SCRIPT_FONT = {
    "hi": "Baloo2", "mr": "Baloo2", "en": "Baloo2", "gu": "BalooBhai2", "or": "BalooBhaina2",
    "ml": "BalooChettan2", "bn": "BalooDa2", "pa": "BalooPaaji2", "kn": "BalooTamma2",
    "te": "BalooTammudu2", "ta": "BalooThambi2",
}
for _f in set(SCRIPT_FONT.values()):
    if _f not in FACES:
        register(_f, f"{_f}[wght].ttf", {"wght": 600})

LANGS = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "parchi_langs.json"),
                       encoding="utf-8"))


def verdict(x, base, max_w):
    """The verdict in red, re-set in each of Parchi's languages, with its name under it."""
    n = len(LANGS)
    cycle = n * LANG_STEP
    css, groups = [], []
    for i, lang in enumerate(LANGS):
        font = SCRIPT_FONT[lang["code"]]
        size = 44
        w = measure(font, lang["danger"], size)
        if w > max_w:
            size *= max_w / w
        ds, _ = glyphs(font, lang["danger"], x, base, size, prec=0)
        a, b = i / n * 100, (i + 1) / n * 100
        css.append(
            f"@keyframes lg{i}{{0%,{a:.2f}%{{opacity:0;transform:translateY(5px)}}"
            f"{a + 1.2:.2f}%{{opacity:1;transform:none}}{b - .8:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}"
        )
        rest = "" if lang["code"] == "en" else ' opacity="0"'      # English when motion is off
        label = f"{lang['english'].upper()}  {i + 1:02d}/{n}"
        groups.append(
            f'<g{rest} style="animation:lg{i} {cycle}s cubic-bezier(.2,.8,.3,1) infinite">'
            f'<path d="{"".join(ds)}" fill="{RED}"/>'
            f'{text("Mono", label, x, base + 26, 9.5, tracking=1.6, fill=RED)}</g>'
        )
    return "".join(groups), "".join(css)


def build():
    sdefs, sbody = sheet(H, seed=41, uid="p", hole_offset=30)
    head = furniture(3, "CASE FILE: PARCHI")

    # the figure: 1,000 farmers, struck row by row; the reached ones in ballpoint
    gx, gy, cols, rows, p = GRID
    rng = random.Random(1162)
    reached = set(rng.sample(range(cols * rows), REACHED))
    ink_rows, blue = [], []
    for r in range(rows):
        dots = []
        for c in range(cols):
            k = r * cols + c
            cx, cy = gx + c * p + p / 2, gy + r * p + p / 2
            if k in reached:
                blue.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.7"/>')
            else:
                dots.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.1"/>')
        ink_rows.append(f'<g class="k" {delay(.5 + r * .05)}>{"".join(dots)}</g>')
    t_grid = .5 + rows * .05
    figure = (
        f'<g fill="{INK}" opacity=".85">{"".join(ink_rows)}</g>'
        f'<g class="ink" {delay(t_grid + .2)} fill="{BLUE}">{"".join(blue)}</g>'
    )
    count, _ = strike("1,000 FARMERS", gx, 118, .3, 60, pitch=2.6)

    count += text("Mono", "6.8% REACHED  /  ICRISAT", gx + cols * p, 126, 9, tracking=1.2,
                  fill=PENCIL, anchor="end")

    # the note, with its arrow leaving the end of the first line for a blue pin
    ny = gy + rows * p + 58
    l1 = "the 68 an extension worker reaches."
    end_x = gx + 4 + measure("Voice", l1, 25) + 10
    k = min((k for k in reached if k // cols >= rows - 4),
            key=lambda k: abs(gx + (k % cols) * p - end_x + 30))
    px, py = gx + (k % cols) * p + p / 2, gy + (k // cols) * p + p / 2
    note = (
        f'<g class="ink" {delay(t_grid + .8)}>'
        f'{text("Voice", l1, gx + 4, ny, 25, fill=BLUE)}'
        f'{text("Voice", "everyone else is advised by the dealer,", gx + 4, ny + 32, 25, fill=INK)}'
        f'{text("Voice", "on a chit.", gx + 4, ny + 64, 25, fill=INK)}</g>'
        f'<path class="pen" {delay(t_grid + 1.1)} pathLength="1" stroke="{BLUE}" stroke-width="2.2" '
        f'd="M{end_x:.0f} {ny - 8} C{end_x + 22:.0f} {ny - 24},{px + 18:.0f} {py + 22:.0f},{px + 3:.0f} {py + 7:.0f} '
        f'M{px + 3:.0f} {py + 7:.0f} l2 11 M{px + 3:.0f} {py + 7:.0f} l11 1"/>'
    )

    # right column, same rhythm as Pet Island: result, context, story, aside
    rx = 572
    v_svg, v_css = verdict(rx, 150, X1 - rx)
    ctx1, t = strike("GOOGLE BUILD WITH AI 2026", rx, 196, 1.0, 90, pitch=2.1)
    ctx2, t = strike("TRACK 04, AGRICULTURE", rx, 216, t, 90, pitch=2.1)
    story = [
        "A farmer photographs the dealer's",
        "chit. Gemini reads it, a rule",
        "engine checks every product",
        "against India's pesticide register,",
        "and the verdict is read aloud.",
    ]
    body = "".join(text("Roman", ln, rx, 280 + i * 31, 25, fill=INK) for i, ln in enumerate(story))
    a1, a2 = "the model reads and explains.", "it never decides."
    aside = (
        f'<g class="ink" {delay(t_grid + 1.6)}>'
        f'{text("Voice", a1, rx, 474, 27, fill=BLUE)}{text("Voice", a2, rx + 14, 506, 27, fill=BLUE)}</g>'
    )
    w_nd = measure("Voice", "never decides.", 27)
    ux = rx + 14 + measure("Voice", "it ", 27)
    underline = (
        f'<path class="pen" {delay(t_grid + 2.1)} pathLength="1" stroke="{BLUE}" stroke-width="2.6" '
        f'd="M{ux:.0f} 515 C{ux + w_nd * .4:.0f} 511,{ux + w_nd * .7:.0f} 514,{ux + w_nd + 2:.0f} 509"/>'
    )

    title = f'<g class="press" {delay(t_grid + .2)}>{text("Slab", "PARCHI", X0 - 4, 694, 128, fill=INK)}</g>'
    repo = text("Mono", "GITHUB.COM/TAHCIN/PARCHI", X1, 686, 10, tracking=1.2, fill=PENCIL, anchor="end")

    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{count}{figure}{note}'
        f"{v_svg}{ctx1}{ctx2}{body}{aside}{underline}"
        f"{rule(588, t_grid, X0, X1)}{title}{repo}"
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, BASE_CSS + v_css,
        title="Parchi",
        desc="Case file for Parchi, Google Build with AI 2026, Track 04. A field of 1,000 pins, one "
             "per farmer: the 68 an extension worker reaches are blue; everyone else is advised by "
             "the dealer, on a chit. Parchi's verdict, do not spray this, cycles through 11 Indian "
             "languages. A farmer photographs the dealer's chit; Gemini reads it, a rule engine "
             "checks every product against India's pesticide register, and the verdict is read "
             "aloud. The model reads and explains. It never decides.",
    )
