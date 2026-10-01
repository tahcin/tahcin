"""SHEET 05: case file, Pet Island.

Pet Island generates a fresh island for every player. So does this sheet:
the figure is a procedural island (fbm value noise with a radial falloff),
seeded with the build date, rendered as a dot-matrix halftone (pin size =
elevation) and printed raster-row by raster-row, the way 9-pin printers
did graphics. Depth contours come from marching squares on the same field.
"""
import math
import random

from lib.fonts import text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, rule, shadow, strike

H = 760
FIG = (80, 104, 520, 544)      # x0, y0, x1, y1 of the island figure
STEP = 9.5                      # halftone pitch


class Noise:
    def __init__(self, seed):
        rng = random.Random(seed)
        self.g = [rng.random() for _ in range(4096)]

    def _v(self, ix, iy):
        return self.g[(ix * 73856093 ^ iy * 19349663) & 4095]

    def value(self, x, y):
        ix, iy = math.floor(x), math.floor(y)
        fx, fy = x - ix, y - iy
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a, b = self._v(ix, iy), self._v(ix + 1, iy)
        c, d = self._v(ix, iy + 1), self._v(ix + 1, iy + 1)
        return (a + (b - a) * sx) * (1 - sy) + (c + (d - c) * sx) * sy

    def fbm(self, x, y, octaves=5):
        s, amp, f, norm = 0.0, 1.0, 1.0, 0.0
        for _ in range(octaves):
            s += amp * self.value(x * f, y * f)
            norm += amp
            amp *= .5
            f *= 2.03
        return s / norm


def field(seed):
    n = Noise(seed)
    rng = random.Random(seed)
    ox, oy = rng.uniform(0, 100), rng.uniform(0, 100)
    stretch = rng.uniform(.75, 1.25)
    cx, cy = (FIG[0] + FIG[2]) / 2, (FIG[1] + FIG[3]) / 2
    r0 = (FIG[2] - FIG[0]) / 2

    def h(x, y):
        dx, dy = (x - cx) / r0 * stretch, (y - cy) / r0 / stretch
        d = math.hypot(dx, dy)
        edge = min(x - FIG[0], FIG[2] - x, y - FIG[1], FIG[3] - y)
        taper = max(0.0, 1 - edge / 44) * .5
        return n.fbm(x / 110 + ox, y / 110 + oy) * 1.25 - d * 1.18 + .02 - taper
    return h


def good(h):
    """An island worth printing: a decent size, clear of the figure frame."""
    pts = [(x, y) for x in range(FIG[0], FIG[2], 10) for y in range(FIG[1], FIG[3], 10) if h(x, y) > 0]
    if not .14 <= len(pts) / 1936 <= .5:
        return False
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs) > FIG[0] + 12 and max(xs) < FIG[2] - 12 and min(ys) > FIG[1] + 12 and max(ys) < FIG[3] - 12


def contours(h, level, step=8):
    """Marching squares: line segments where h == level, as one path."""
    xs = [FIG[0] + i * step for i in range(int((FIG[2] - FIG[0]) / step) + 1)]
    ys = [FIG[1] + j * step for j in range(int((FIG[3] - FIG[1]) / step) + 1)]
    grid = [[h(x, y) - level for x in xs] for y in ys]
    segs = []

    def lerp(p, q, a, b):
        t = a / (a - b)
        return p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t

    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            c = [(xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1])]
            v = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            pts = []
            for k in range(4):
                a, b = v[k], v[(k + 1) % 4]
                if (a > 0) != (b > 0):
                    pts.append(lerp(c[k], c[(k + 1) % 4], a, b))
            for k in range(0, len(pts) - 1, 2):
                (x1, y1), (x2, y2) = pts[k], pts[k + 1]
                segs.append(f"M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}")
    return "".join(segs)


def build(seed_date):
    seed = int(seed_date.strftime("%Y%m%d"))
    h = field(seed)
    while not good(h):          # deterministic re-roll: same date, same island
        seed += 1
        h = field(seed)
    sdefs, sbody = sheet(H, seed=61, uid="i", hole_offset=18)
    head = furniture(5, "CASE FILE: PET ISLAND")

    # halftone island, struck one raster row at a time
    rows = []
    y = FIG[1] + STEP / 2
    j = 0
    land = []
    while y < FIG[3]:
        dots = []
        x = FIG[0] + STEP / 2 + (STEP / 2 if j % 2 else 0)
        while x < FIG[2]:
            v = h(x, y)
            if v > 0:
                land.append((x, y))
                r = STEP * (.1 + .36 * min(1, v / .5) ** 1.3)
                dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}"/>')
            x += STEP
        if dots:
            rows.append(f'<g class="k" {delay(.5 + len(rows) * .045)}>{"".join(dots)}</g>')
        y += STEP * .866
        j += 1
    island = f'<g fill="{INK}">{"".join(rows)}</g>'
    t_print = .5 + len(rows) * .045

    depth = "".join(
        f'<path class="pen" {delay(t_print + i * .25)} pathLength="1" d="{contours(h, lv)}" '
        f'stroke="{PENCIL}" stroke-width="1.1" opacity="{.75 - i * .18:.2f}"/>'
        for i, lv in enumerate((-.05, -.13, -.22))
    )

    # a ballpoint pet on the highest ground
    px, py = max(land, key=lambda p: h(*p)) if land else ((FIG[0] + FIG[2]) / 2, (FIG[1] + FIG[3]) / 2)
    pet = (
        f'<g transform="translate({px:.0f} {py - 4:.0f})">'
        f'<circle class="ink" {delay(t_print + .8)} cy="-4" r="25" fill="#F2EDE1"/>'
        f'<path class="pen" {delay(t_print + .9)} pathLength="1" stroke="{BLUE}" stroke-width="2.6" fill="none" '
        f'd="M-13 2 C-14 -10,-8 -15,0 -15 C8 -15,14 -10,13 2 C12 9,-12 9,-13 2Z M-11 -9 L-13 -22 L-4 -14 M11 -9 L13 -22 L4 -14"/>'
        f'<path class="pen" {delay(t_print + 1.2)} pathLength="1" stroke="{BLUE}" stroke-width="2.6" fill="none" '
        f'd="M-5 -5v1 M5 -5v1 M-2 1 q2 2 4 0"/></g>'
    )
    nx, ny = FIG[2] - 60, FIG[3] + 8
    pet_note = (
        f'<g class="ink" {delay(t_print + 1.5)}>'
        f'{text("Voice", "your pet, here.", nx - 110, ny + 20, 26, fill=BLUE)}</g>'
        f'<path class="pen" {delay(t_print + 1.8)} pathLength="1" stroke="{BLUE}" stroke-width="2.2" fill="none" '
        f'd="M{nx - 120:.0f} {ny + 10:.0f} C{px - 30:.0f} {ny + 10:.0f},{px - 30:.0f} {py + 60:.0f},{px - 8:.0f} {py + 18:.0f} '
        f'M{px - 8:.0f} {py + 18:.0f} l-10 4 M{px - 8:.0f} {py + 18:.0f} l1 11"/>'
    )
    # right column: the result first, then what it is
    rx = 572
    win, t = strike("FIRST PLACE", rx, 116, .4, 30, pitch=4.2, fill=RED)
    where, t = strike("OPUS BUILD DAY, BANGALORE", rx, 166, t, 90, pitch=2.1)
    built, t = strike("BUILT IN ONE DAY", rx, 186, t, 90, pitch=2.1)
    body_lines = [
        "Show it a photo of your pet.",
        "A chibi 3D version of it walks",
        "onto a freshly generated island,",
        "meets six villagers, talks back,",
        "and remembers what you told it.",
    ]
    body = "".join(
        text("Roman", ln, rx, 248 + i * 31, 25, fill=INK) for i, ln in enumerate(body_lines)
    )
    aside = (
        f'<g class="ink" {delay(t_print + 2.1)}>'
        f'{text("Voice", "the island on the left is", rx, 450, 25, fill=BLUE)}'
        f'{text("Voice", "procedural too. a new one daily.", rx + 14, 480, 25, fill=BLUE)}</g>'
    )

    # the title, set big across the foot of the sheet
    title = f'<g class="press" {delay(t_print + .2)}>{text("Slab", "PET ISLAND", X0 - 4, 732, 128, fill=INK)}</g>'
    url = text("Mono", "PET-ISLAND.VERCEL.APP", X1, 724, 10, tracking=1.2, fill=PENCIL, anchor="end")

    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{depth}{island}{pet}{pet_note}'
        f"{win}{where}{built}{body}{aside}{rule(626, t_print, X0, X1)}{title}{url}"
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, BASE_CSS,
        title="Pet Island",
        desc="Case file for Pet Island: first place at Opus Build Day, Bangalore, built in one "
             "day. Show it a photo of your pet and a chibi 3D version walks onto a freshly "
             "generated island with six villagers, and talks back. The figure is a procedural "
             "island printed as a dot-matrix halftone, regenerated every day.",
    )
