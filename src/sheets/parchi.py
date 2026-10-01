"""SHEET 03: case file, Parchi.

One object and one sentence. The object is the dealer's chit, written in
carbon violet, with Parchi's verdict stamped across it; the stamp re-inks
itself in each of Parchi's eleven languages (its own UI copy, `danger` in
src/lib/i18n.ts). The sentence is the design rule from Parchi's README.
"""
import json
import os

from lib.fonts import FACES, glyphs, measure, register, text
from lib.motion import BASE_CSS, SLAM_EASE, delay
from lib.paper import INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, furniture, glyph_defs, shadow, strike

H = 640
VIOLET = "#4A3B9A"      # carbon-copy ink
CHIT = "#F6E9B4"        # pale yellow chit paper
CHIT_LINE = "#E2CF8A"
LANG_STEP = 1.6         # seconds each language holds the stamp

SCRIPT_FONT = {
    "hi": "Baloo2", "mr": "Baloo2", "en": "Baloo2", "gu": "BalooBhai2", "or": "BalooBhaina2",
    "ml": "BalooChettan2", "bn": "BalooDa2", "pa": "BalooPaaji2", "kn": "BalooTamma2",
    "te": "BalooTammudu2", "ta": "BalooThambi2",
}
for _f in set(SCRIPT_FONT.values()):
    if _f not in FACES:
        register(_f, f"{_f}[wght].ttf", {"wght": 700})

LANGS = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "parchi_langs.json"),
                       encoding="utf-8"))


def verdict_stamp(cx, cy, box_w=272):
    """A clean double-ruled stamp whose wording cycles through eleven languages."""
    n = len(LANGS)
    cycle = n * LANG_STEP
    css, groups = [], []
    for i, lang in enumerate(LANGS):
        font = SCRIPT_FONT[lang["code"]]
        size = 34
        w = measure(font, lang["danger"], size)
        if w > box_w - 36:
            size *= (box_w - 36) / w
        ds, _ = glyphs(font, lang["danger"], cx, cy + size * .32, size, anchor="middle", prec=0)
        a, b = i / n * 100, (i + 1) / n * 100
        css.append(
            f"@keyframes lg{i}{{0%,{a:.2f}%{{opacity:0;transform:scale(1.25)}}"
            f"{a + .8:.2f}%{{opacity:1;transform:none}}{b - .4:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}"
        )
        rest = "" if lang["code"] == "en" else ' opacity="0"'   # English when motion is off
        groups.append(
            f'<g{rest} style="transform-box:fill-box;transform-origin:50% 50%;'
            f'animation:lg{i} {cycle}s {SLAM_EASE} infinite"><path d="{"".join(ds)}"/>'
            f'{text("Mono", lang["english"].upper(), cx, cy + 44, 9, tracking=2, anchor="middle")}</g>'
        )
    frame = (
        f'<rect x="{cx - box_w / 2}" y="{cy - 40}" width="{box_w}" height="100" rx="8" '
        f'fill="none" stroke="{RED}" stroke-width="3.2"/>'
        f'<rect x="{cx - box_w / 2 + 6}" y="{cy - 34}" width="{box_w - 12}" height="88" rx="5" '
        f'fill="none" stroke="{RED}" stroke-width="1"/>'
    )
    return f'<g fill="{RED}" opacity=".92">{frame}{"".join(groups)}</g>', "".join(css)


def chit(t0):
    x, y, w, h = 100, 112, 330, 440
    rule_lines = "".join(
        f'<path d="M{x + 18} {y + yy}H{x + w - 18}" stroke="{CHIT_LINE}" stroke-width="1"/>'
        for yy in range(96, h - 30, 34)
    )
    paper = (
        f'<rect x="{x + 4}" y="{y + 7}" width="{w}" height="{h}" fill="#000" opacity=".12" filter="url(#lift)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{CHIT}"/>{rule_lines}'
        + text("Mono", "CROP", x + 24, y + 36, 9, tracking=1.6, fill=PENCIL)
        + text("Mono", "No. 214", x + w - 24, y + 36, 9, tracking=1.6, fill=PENCIL, anchor="end")
    )
    lines = [
        ("Tomato", 74, 32),
        ("Malathion 50 EC", 160, 28),
        ("500 ml, spray twice", 194, 22),
        ("Monocrotophos 36 SL", 262, 28),
        ("1 bottle", 296, 22),
    ]
    ink = "".join(
        f'<g class="ink" {delay(t0 + .3 + i * .16)}>'
        f'{text("Voice", s, x + 26 + (14 if size == 22 else 0), y + dy, size, fill=VIOLET)}</g>'
        for i, (s, dy, size) in enumerate(lines)
    )
    stamp, css = verdict_stamp(x + w / 2, y + 362)
    stamp = (
        f'<g transform="rotate(-6 {x + w / 2} {y + 362})">'
        f'<g class="slam" style="animation-delay:{t0 + 1.5:.2f}s;--r0:-14deg">{stamp}</g></g>'
    )
    return (
        f'<g transform="rotate(-2.5 {x + w / 2} {y + h / 2})">'
        f'<g class="ink" {delay(t0)}>{paper}</g>{ink}{stamp}</g>',
        css,
    )


def build():
    sdefs, sbody = sheet(H, seed=41, uid="p", hole_offset=30)
    head = furniture(3, "CASE FILE: PARCHI")
    chit_svg, stamp_css = chit(.4)

    rx = 500
    title = f'<g class="press" {delay(.3)}>{text("Slab", "PARCHI", rx - 4, 214, 132, fill=INK)}</g>'
    gloss = text("Voice", "parchi (n.): the chit a pesticide dealer writes.", rx, 254, 22, fill=PENCIL)
    story = [
        "A farmer photographs the dealer's chit.",
        "Gemini reads it, a rule engine checks every",
        "product against India's pesticide register,",
        "and the verdict is spoken in their language.",
    ]
    body = "".join(text("Roman", ln, rx, 304 + i * 30, 23, fill=INK) for i, ln in enumerate(story))
    quote = (
        f'<g class="press" {delay(1.6)}>{text("Slab", "THE MODEL READS", rx - 2, 474, 46, fill=INK)}</g>'
        f'<g class="press" {delay(1.8)}>{text("Slab", "AND EXPLAINS.", rx - 2, 520, 46, fill=INK)}</g>'
        f'<g class="press" {delay(2.1)}>{text("Slab", "IT NEVER DECIDES.", rx - 2, 566, 46, fill=RED)}</g>'
    )
    foot, _ = strike("BUILD WITH AI 2026  /  11 LANGUAGES", rx, 594, 2.4, 160, pitch=1.8)

    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{chit_svg}{title}{gloss}{body}{quote}{foot}'
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, BASE_CSS + stamp_css,
        title="Parchi",
        desc="Case file for Parchi, built for Google Build with AI 2026. A pesticide dealer's chit "
             "for tomato, stamped with the verdict, do not spray this, which cycles through 11 "
             "Indian languages. A farmer photographs the dealer's chit; Gemini reads it, a rule "
             "engine checks every product against India's pesticide register, and the verdict is "
             "spoken in their language. The model reads and explains. It never decides.",
    )
