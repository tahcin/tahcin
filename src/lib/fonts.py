"""Typeset text as outlined vector paths.

GitHub serves repo SVGs with `Content-Security-Policy: default-src 'none'`.
Chrome still allows data-URI fonts under that policy, but Firefox does not,
so embedded fonts silently fall back to Times. To render identically
everywhere, no SVG here contains a single <text> element: every line is
shaped with HarfBuzz (kerning, ligatures, Indic conjuncts) and drawn as
glyph outlines from the OFL font files in ../fonts.
"""
import io
import os
from functools import lru_cache

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

# face name -> (file, variable-axis location or None)
FACES = {
    "Slab": ("Archivo[wdth,wght].ttf", {"wdth": 62, "wght": 900}),    # display: extra-condensed black
    "Wide": ("Archivo[wdth,wght].ttf", {"wdth": 125, "wght": 800}),   # stamps: expanded
    "Body": ("Archivo[wdth,wght].ttf", {"wdth": 100, "wght": 500}),
    "Voice": ("InstrumentSerif-Italic.ttf", None),                      # the human, in ballpoint
    "Roman": ("InstrumentSerif-Regular.ttf", None),
    "Mono": ("MartianMono[wdth,wght].ttf", {"wdth": 87.5, "wght": 400}),
    "MonoB": ("MartianMono[wdth,wght].ttf", {"wdth": 87.5, "wght": 700}),
}


def register(name, file, loc=None):
    FACES[name] = (file, loc)


@lru_cache(maxsize=None)
def _bytes(name):
    file, loc = FACES[name]
    font = TTFont(os.path.join(FONT_DIR, file))
    if loc:
        font = instancer.instantiateVariableFont(font, loc)
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


@lru_cache(maxsize=None)
def _tt(name):
    return TTFont(io.BytesIO(_bytes(name)))


@lru_cache(maxsize=None)
def _hb(name):
    return hb.Font(hb.Face(hb.Blob(_bytes(name))))


def _ntos(v):
    s = f"{v:.1f}"
    return "0" if s in ("0.0", "-0.0") else s.rstrip("0").rstrip(".")


def _ntos0(v):
    return str(round(v))


def glyphs(name, text, x, y, size, tracking=0.0, anchor="start", prec=None):
    """Shape `text` and return (list of per-glyph path d strings, advance width).

    (x, y) is the baseline origin. tracking is extra space per glyph, in px.
    anchor: start | middle | end.
    prec: 0 rounds outlines to whole units (fine for large or stamped type);
    by default type above 60px is rounded, smaller type keeps one decimal.
    """
    if prec is None:
        prec = 0 if size > 60 else 1
    tt = _tt(name)
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    scale = size / tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(_hb(name), buf, {"kern": True, "liga": True})
    infos, poss = buf.glyph_infos, buf.glyph_positions
    width = sum(p.x_advance for p in poss) * scale + tracking * max(0, len(poss) - 1)
    cx = x - (width / 2 if anchor == "middle" else width if anchor == "end" else 0)
    out = []
    for info, pos in zip(infos, poss):
        pen = SVGPathPen(gs, ntos=_ntos0 if prec == 0 else _ntos)
        gx = cx + pos.x_offset * scale
        gy = y - pos.y_offset * scale
        gs[order[info.codepoint]].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, gy)))
        d = pen.getCommands()
        if d:
            out.append(d)
        cx += pos.x_advance * scale + tracking
    return out, width


def text(name, s, x, y, size, tracking=0.0, anchor="start", prec=None, **attrs):
    """A whole line as one <path>."""
    ds, _ = glyphs(name, s, x, y, size, tracking, anchor, prec)
    a = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{"".join(ds)}"{a}/>'


def measure(name, s, size, tracking=0.0):
    return glyphs(name, s, 0, 0, size, tracking)[1]
