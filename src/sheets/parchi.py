"""SHEET 03: case file, Parchi.

A dealer's chit in carbon-violet ballpoint, the rule engine's printout beside
it, and a verdict stamp that keeps re-inking itself in all eleven of Parchi's
languages. Every stamp string is Parchi's own UI copy (src/lib/i18n.ts,
`danger`), and both flags on the chit are examples given in Parchi's README.
"""
import json
import os

from lib.fonts import FACES, glyphs, measure, register, text
from lib.motion import BASE_CSS, SLAM_EASE, delay
from lib.paper import INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, rule, shadow, strike

H = 790
VIOLET = "#4A3B9A"      # carbon-copy ink
CHIT = "#F5E6A8"        # pale yellow chit paper
LANG_STEP = 1.5         # seconds each language holds the stamp

SCRIPT_FONT = {
    "hi": "Baloo2", "mr": "Baloo2", "en": "Baloo2", "gu": "BalooBhai2", "or": "BalooBhaina2",
    "ml": "BalooChettan2", "bn": "BalooDa2", "pa": "BalooPaaji2", "kn": "BalooTamma2",
    "te": "BalooTammudu2", "ta": "BalooThambi2",
}
for _f in set(SCRIPT_FONT.values()):
    if _f not in FACES:
        register(_f, f"{_f}[wght].ttf", {"wght": 760})

LANGS = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "parchi_langs.json"),
                       encoding="utf-8"))


def chit(t0):
    """The dealer's chit: a small yellow slip, written in carbon violet."""
    x, y, w, h = 300, 118, 268, 330
    lines = [
        ("Tomato", 60, 30),
        ("1. Malathion 50 EC", 108, 25),
        ("    500 ml, 2 times", 136, 21),
        ("2. Monocrotophos 36 SL", 212, 25),
        ("    1 bottle", 240, 21),
    ]
    body = "".join(
        f'<g class="ink" {delay(t0 + .25 + i * .18)}>'
        f'{text("Voice", s, x + 22, y + dy, size, fill=VIOLET)}</g>'
        for i, (s, dy, size) in enumerate(lines)
    )
    ruled = "".join(
        f'<path d="M{x + 14} {y + yy}H{x + w - 14}" stroke="#D9C37A" stroke-width="1"/>'
        for yy in range(72, h - 20, 30)
    )
    head = (
        text("Mono", "CROP", x + 22, y + 32, 9.5, tracking=1.2, fill=PENCIL)
        + text("Mono", "SAMPLE CHIT", x + w - 18, y + 32, 9.5, tracking=1.2, fill=PENCIL, anchor="end")
    )
    # rule-engine flags, stamped onto the chit lines once the printout has run
    flags = [("BANNED ON THIS CROP", 170, -5, 4.2), ("STOPPED FORMULATION", 276, 4, 4.9)]
    stamps = ""
    for label, fy, rot, t in flags:
        wl = measure("Wide", label, 12, 1.2)
        stamps += (
            f'<g transform="translate({x + w / 2 + 4} {y + fy}) rotate({rot})">'
            f'<g class="slam" style="animation-delay:{t}s;--r0:{rot * 3}deg" filter="url(#wear)">'
            f'<rect x="{-wl / 2 - 9:.1f}" y="-14" width="{wl + 18:.1f}" height="24" rx="3" '
            f'fill="none" stroke="{RED}" stroke-width="2.4"/>'
            f'{text("Wide", label, 0, 3, 12, tracking=1.2, anchor="middle", fill=RED)}</g></g>'
        )
    return (
        f'<g transform="rotate(-3 {x + w / 2} {y + h / 2})">'
        f'<g class="ink" {delay(t0)}>'
        f'<rect x="{x + 3}" y="{y + 5}" width="{w}" height="{h}" fill="#000" opacity=".12" filter="url(#lift)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{CHIT}"/>{ruled}{head}</g>'
        f"{body}{stamps}</g>"
    )


def printout(t0):
    """The rule engine's verdict, struck in dot-matrix."""
    rows = [
        "RULE ENGINE / CIB&RC",
        "",
        "01 MALATHION 50 EC",
        "   CROP TOMATO",
        "   X BANNED ON THIS CROP",
        "   SRC S.O. 4294(E)",
        "",
        "02 MONOCROTOPHOS 36 SL",
        "   X STOPPED FORMULATION",
        "   SRC S.O. 4294(E)",
        "",
        "VERDICT  DO NOT SPRAY",
    ]
    t, y, out = t0, 122, ""
    for r in rows:
        if r:
            g, t = strike(r, 610, y, t, 150, pitch=2.2, fill=RED if r.startswith("   X") else INK)
            out += g
        y += 25
    return out, t


def language_stamp(cx, cy):
    """One stamp, re-inked in each of Parchi's eleven languages, in a loop."""
    n = len(LANGS)
    cycle = n * LANG_STEP
    css, groups = [], []
    box_w = 300
    for i, lang in enumerate(LANGS):
        font = SCRIPT_FONT[lang["code"]]
        size = 40
        w = measure(font, lang["danger"], size)
        if w > box_w - 30:
            size *= (box_w - 30) / w
        ds, _ = glyphs(font, lang["danger"], cx, cy + size * .3, size, anchor="middle", prec=0)
        label = f'{lang["english"].upper()}  {i + 1:02d}/{n}'
        a = i / n * 100
        b = (i + 1) / n * 100
        name = f"lg{i}"
        css.append(
            f"@keyframes {name}{{0%,{a:.2f}%{{opacity:0;transform:scale(1.5)}}"
            f"{a + .9:.2f}%{{opacity:1;transform:scale(.97)}}{a + 1.6:.2f}%{{transform:none}}"
            f"{b - .3:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}"
        )
        # the English stamp is the resting state when motion is off
        rest = "" if lang["code"] == "en" else ' opacity="0"'
        groups.append(
            f'<g{rest} style="transform-box:fill-box;transform-origin:50% 50%;'
            f'animation:{name} {cycle}s {SLAM_EASE} infinite">'
            f'<path d="{"".join(ds)}" fill="{RED}"/>'
            f'{text("Mono", label, cx, cy + 52, 10, tracking=1.4, anchor="middle", fill=RED)}</g>'
        )
    frame = (
        f'<rect x="{cx - box_w / 2}" y="{cy - 46}" width="{box_w}" height="112" rx="10" '
        f'fill="none" stroke="{RED}" stroke-width="4"/>'
        f'<rect x="{cx - box_w / 2 + 8}" y="{cy - 38}" width="{box_w - 16}" height="96" rx="6" '
        f'fill="none" stroke="{RED}" stroke-width="1.4"/>'
        f'<path d="M{cx - box_w / 2 + 24} {cy + 34}H{cx + box_w / 2 - 24}" stroke="{RED}" stroke-width="1"/>'
    )
    return (
        f'<g transform="rotate(-4 {cx} {cy})" style="mix-blend-mode:multiply" filter="url(#wear)">'
        f'{frame}{"".join(groups)}</g>',
        "".join(css),
    )


def build():
    sdefs, sbody = sheet(H, seed=41, uid="p", hole_offset=30)
    head = furniture(3, "CASE FILE: PARCHI", "BUILD WITH AI 2026")

    # the title, set vertically up the left edge
    title_ds, title_w = glyphs("Slab", "PARCHI", 0, 0, 212)
    title = (
        f'<g transform="translate(262 {104 + title_w:.0f}) rotate(-90)">'
        f'<g class="press" {delay(.3)}><path d="{"".join(title_ds)}" fill="{INK}"/></g></g>'
    )
    gloss = (
        text("Voice", "parchi (n.): the chit a", 300, 486, 25, fill=INK)
        + text("Voice", "pesticide dealer writes.", 300, 514, 25, fill=INK)
    )

    chit_svg = chit(.6)
    pr, t_end = printout(1.4)
    stamp, stamp_css = language_stamp(765, 492)
    stamp_caption = text("Mono", "THE VERDICT, SPOKEN IN 11 LANGUAGES", 765, 586, 10,
                         tracking=1.2, anchor="middle", fill=PENCIL)

    # the line that explains the whole design, from Parchi's README
    quote = (
        f'<g class="press" {delay(t_end + .1)}>{text("Slab", "THE MODEL READS AND EXPLAINS.", 300, 664, 50, fill=INK)}</g>'
        f'<g class="press" {delay(t_end + .4)}>{text("Slab", "IT NEVER DECIDES.", 300, 716, 50, fill=RED)}</g>'
    )
    facts, _ = strike("GEMINI READS  /  RULES DECIDE  /  22 CROPS  /  2,210 APPROVED USES  /  APACHE 2.0",
                      X0, 752, t_end, 220, pitch=1.75)

    css = (
        BASE_CSS + stamp_css
    )
    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{title}{gloss}{chit_svg}{pr}{stamp}{stamp_caption}'
        f"{rule(620, t_end, 300, X1)}{quote}{facts}"
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, css,
        title="Parchi",
        desc="Case file for Parchi, built for Google Build with AI 2026, Track 04. A pesticide "
             "dealer's chit for tomato lists Malathion 50 EC and Monocrotophos 36 SL; a rule "
             "engine checks them against India's CIB&RC register and flags them as banned on "
             "this crop and a stopped formulation. A stamp cycles the verdict, do not spray "
             "this, through 11 Indian languages. Quote: The model reads and explains. It never decides.",
    )
