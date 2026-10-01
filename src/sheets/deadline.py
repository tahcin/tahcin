"""SHEET 04: case file, Deadline Dash.

One pin per real commit, one column per week. The machine's commits (the
hourly sync bot) stack above the line in ink; Tahcin's own commits hang
below it in ballpoint blue. Data: data/deadline_dash_commits.tsv, refreshed
by the daily print run.
"""
import collections
import datetime as dt
import os

from lib.fonts import measure, text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, shadow, strike

H = 660
DATA = os.path.join(os.path.dirname(__file__), "..", "data", "deadline_dash_commits.tsv")
BASE_Y = 430          # the line between machine and human
PIN = 3.3             # pin pitch inside a week column
PER_ROW = 3           # pins per row inside a week column


def load():
    rows = [l.rstrip("\n").split("\t") for l in open(DATA, encoding="utf-8") if l.strip()]
    weeks = collections.defaultdict(lambda: [0, 0])
    first_bot = None
    for date, login, *_ in rows:
        t = dt.datetime.fromisoformat(date.replace("Z", "+00:00")).date()
        monday = t - dt.timedelta(days=t.weekday())
        bot = login.endswith("[bot]")
        weeks[monday][0 if bot else 1] += 1
        if bot and (first_bot is None or t < first_bot):
            first_bot = t
    return weeks, first_bot


def build():
    weeks, first_bot = load()
    start, end = min(weeks), max(weeks)
    n_weeks = (end - start).days // 7 + 1
    col = (X1 - X0) / n_weeks
    machine = sum(v[0] for v in weeks.values())
    human = sum(v[1] for v in weeks.values())

    sdefs, sbody = sheet(H, seed=53, uid="d", hole_offset=6)
    head = furniture(4, "CASE FILE: DEADLINE DASH")

    title = f'<g class="press" {delay(.3)}>{text("Slab", "DEADLINE DASH", X0 - 3, 186, 104, fill=INK)}</g>'
    tagline = f'<g class="ink" {delay(.7)}>{text("Voice", "never miss a CLA again.", X0 + 4, 232, 32, fill=BLUE)}</g>'

    # the butterfly: one pin per commit, struck left to right
    pins_m, pins_h = [], []
    sweep0, sweep = 1.0, 2.2
    for wk, (m, hmn) in weeks.items():
        i = (wk - start).days // 7
        cx0 = X0 + i * col + (col - PER_ROW * PIN) / 2 + PIN / 2
        t = round(sweep0 + i / n_weeks * sweep, 3)
        for k in range(m):
            r, c = divmod(k, PER_ROW)
            pins_m.append((t, f'<circle cx="{cx0 + c * PIN:.1f}" cy="{BASE_Y - 6 - r * PIN:.1f}" r="1.25"/>'))
        for k in range(hmn):
            r, c = divmod(k, PER_ROW)
            pins_h.append((t, f'<circle cx="{cx0 + c * PIN:.1f}" cy="{BASE_Y + 6 + r * PIN:.1f}" r="1.25"/>'))

    def by_time(pins, fill):
        groups = collections.defaultdict(list)
        for t, c in pins:
            groups[t].append(c)
        return f'<g fill="{fill}">' + "".join(
            f'<g class="k" {delay(t)}>{"".join(cs)}</g>' for t, cs in sorted(groups.items())
        ) + "</g>"

    chart = by_time(pins_m, INK) + by_time(pins_h, BLUE)
    # the bot is still running: its newest week carries a blinking pin
    last_wk = max(wk for wk, (m, _) in weeks.items() if m)
    li = (last_wk - start).days // 7
    lm = weeks[last_wk][0]
    lx = X0 + li * col + (col - PER_ROW * PIN) / 2 + PIN / 2 + ((lm % PER_ROW) * PIN)
    ly = BASE_Y - 6 - (lm // PER_ROW) * PIN
    chart += (f'<g class="k" {delay(sweep0 + sweep)}><circle class="blink" cx="{lx:.1f}" '
              f'cy="{ly:.1f}" r="1.9" fill="{RED}"/></g>')
    axis = f'<path d="M{X0} {BASE_Y}H{X1}" stroke="{INK}" stroke-width="1"/>'
    ticks = ""
    for y, m in [(2025, 7), (2025, 11), (2026, 3), (2026, 7)]:
        d = dt.date(y, m, 1)
        # label only the quiet stretch of the line, never on top of pins
        if start <= d < first_bot - dt.timedelta(days=21):
            x = X0 + (d - start).days / 7 * col
            ticks += f'<path d="M{x:.1f} {BASE_Y - 3}V{BASE_Y + 3}" stroke="{INK}"/>'
            ticks += text("Mono", d.strftime("%b %y").upper(), x + 4, BASE_Y - 7, 9, tracking=.8, fill=PENCIL)

    done = sweep0 + sweep
    machine_lbl, _ = strike(f"THE BOT  {machine:,}", X0, 300, done, 120, pitch=2.4)
    human_lbl = (
        f'<g class="ink" {delay(done + .3)}>'
        f'{text("Voice", f"me  {human}", X0 + 70, 492, 30, fill=BLUE)}</g>'
    )

    # the day the bot took over
    bx = X0 + (first_bot - start).days / 7 * col
    nx = bx - 236
    bot_note = (
        f'<g class="ink" {delay(done + .6)}>'
        f'{text("Voice", "the bot started syncing,", nx, 300, 23, fill=BLUE)}'
        f'{text("Voice", f"{first_bot.day} {first_bot:%B %Y}", nx + 18, 326, 23, fill=BLUE)}</g>'
        f'<path class="pen" {delay(done + 1)} pathLength="1" stroke="{BLUE}" stroke-width="2.2" '
        f'd="M{nx + 204:.0f} 312 C{bx - 16:.0f} 308,{bx - 6:.0f} 340,{bx - 3:.0f} 372 '
        f'M{bx - 3:.0f} 372 l-6 -10 M{bx - 3:.0f} 372 l6 -9"/>'
    )

    # the sentence, in the human's hand
    t_end = done + 1.4
    s1 = f"I made {human} commits. Then I made the thing"
    s2 = f"that has made {machine:,} more."
    statement = (
        f'<g class="ink" {delay(t_end)}>{text("Voice", s1, X0, 590, 34, fill=BLUE)}</g>'
        f'<g class="ink" {delay(t_end + .3)}>{text("Voice", s2, X0, 628, 34, fill=BLUE)}</g>'
    )
    under_x = X0 + measure("Voice", "that has made ", 34)
    under_w = measure("Voice", f"{machine:,}", 34)
    underline = (
        f'<path class="pen" {delay(t_end + .8)} pathLength="1" stroke="{BLUE}" stroke-width="3" '
        f'd="M{under_x - 2:.0f} 636 C{under_x + under_w * .4:.0f} 632,{under_x + under_w * .7:.0f} 635,{under_x + under_w + 4:.0f} 630"/>'
    )

    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{title}{tagline}'
        f"{axis}{ticks}{chart}{machine_lbl}{human_lbl}{bot_note}{statement}{underline}"
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, BASE_CSS,
        title="Deadline Dash",
        desc=f"Case file for Deadline Dash: never miss a CLA again. A chart with one pin per "
             f"commit: {machine:,} commits by the hourly sync bot above the line, {human} "
             f"by Tahcin below it. The bot started syncing on {first_bot:%d %B %Y}. "
             f"Handwritten: I made {human} commits. Then I made the thing that has made "
             f"{machine:,} more.",
    )
