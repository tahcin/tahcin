"""SHEET 04: case file, Deadline Dash.

One pin per real commit, one column per week. The machine's commits (the
hourly sync bot) stack above the line in ink; Tahcin's own commits hang
below it in ballpoint blue. Data: data/deadline_dash_commits.tsv, refreshed
by the daily print run.
"""
import collections
import datetime as dt
import os
import re

from lib.fonts import measure, text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, rule, shadow, strike

H = 800
DATA = os.path.join(os.path.dirname(__file__), "..", "data", "deadline_dash_commits.tsv")
BASE_Y = 492          # the line between machine and human
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
    head = furniture(4, "CASE FILE: DEADLINE DASH", f"SINCE {start.year}")

    title = f'<g class="press" {delay(.3)}>{text("Slab", "DEADLINE DASH", X0 - 3, 190, 102, fill=INK)}</g>'
    tagline = f'<g class="ink" {delay(.7)}>{text("Voice", "never miss a CLA again.", X0 + 4, 238, 34, fill=BLUE)}</g>'
    what = text("Mono", "A PYTHON JOB LOGS IN TO THE COURSE PORTAL EVERY HOUR, PULLS", X0, 286, 10.5, tracking=.5, fill=INK, opacity=".8")
    what += text("Mono", "EVERY DEADLINE AND PUSHES A REMINDER BEFORE IT LANDS.", X0, 303, 10.5, tracking=.5, fill=INK, opacity=".8")

    # teleprinter window: the hourly sync, feeding forever
    wx, wy, ww, wh = 724, 104, 196, 186
    line_h = 20
    lines = [f"{h:02d}:17 SYNC  OK" for h in range(24)]
    feed = ""
    for copy in range(2):
        for i, ln in enumerate(lines):
            g, _ = strike(ln, wx + 14, wy + 16 + (copy * 24 + i) * line_h, 0, 9999, pitch=1.9)
            feed += re.sub(r' class="k" style="[^"]*"', "", g)
    window = (
        f'<clipPath id="tw"><rect x="{wx}" y="{wy + 6}" width="{ww}" height="{wh - 12}"/></clipPath>'
        f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-dasharray="2 3"/>'
        f'<g clip-path="url(#tw)"><g class="feed">{feed}</g></g>'
        + text("Mono", "CRON  17 * * * *", wx, wy - 8, 10, tracking=1, fill=PENCIL)
        + text("Mono", "FIG. 2", wx + ww, wy - 8, 10, tracking=1, fill=PENCIL, anchor="end")
    )
    feed_css = (
        f".feed{{animation:feed {24 * 1.1:.1f}s steps(24) infinite}}"
        f"@keyframes feed{{to{{transform:translateY(-{24 * line_h}px)}}}}"
    )

    # the butterfly: one pin per commit
    pins_m, pins_h = [], []
    sweep0, sweep = 1.0, 2.2
    for wk, (m, hmn) in weeks.items():
        i = (wk - start).days // 7
        cx0 = X0 + i * col + (col - PER_ROW * PIN) / 2 + PIN / 2
        t = sweep0 + i / n_weeks * sweep
        for k in range(m):
            r, c = divmod(k, PER_ROW)
            pins_m.append((t, f'<circle cx="{cx0 + c * PIN:.1f}" cy="{BASE_Y - 6 - r * PIN:.1f}" r="1.25"/>'))
        for k in range(hmn):
            r, c = divmod(k, PER_ROW)
            pins_h.append((t, f'<circle cx="{cx0 + c * PIN:.1f}" cy="{BASE_Y + 6 + r * PIN:.1f}" r="1.25"/>'))

    def by_time(pins, fill):
        groups = collections.defaultdict(list)
        for t, c in pins:
            groups[round(t, 3)].append(c)
        return f'<g fill="{fill}">' + "".join(
            f'<g class="k" {delay(t)}>{"".join(cs)}</g>' for t, cs in sorted(groups.items())
        ) + "</g>"

    chart = by_time(pins_m, INK) + by_time(pins_h, BLUE)
    axis = f'<path d="M{X0} {BASE_Y}H{X1}" stroke="{INK}" stroke-width="1"/>'
    ticks = ""
    for y, m in [(2025, 3), (2025, 7), (2025, 11), (2026, 3), (2026, 7)]:
        d = dt.date(y, m, 1)
        if start <= d <= end:
            x = X0 + (d - start).days / 7 * col
            ticks += f'<path d="M{x:.1f} {BASE_Y - 3}V{BASE_Y + 3}" stroke="{INK}"/>'
            ticks += text("Mono", d.strftime("%b %y").upper(), x + 3, BASE_Y - 8, 9, tracking=.8, fill=PENCIL)

    # labels for the two halves
    lm, _ = strike(f"MACHINE  {machine:,} SYNCS", X0, 336, sweep0 + sweep, 160, pitch=2.2)
    lh = f'<g class="ink" {delay(sweep0 + sweep + .3)}>{text("Voice", f"me, {human} commits by hand", X0, 646, 30, fill=BLUE)}</g>'

    # mark the day the bot took over
    bx = X0 + (first_bot - start).days / 7 * col
    note_x = bx - 250
    bot_note = (
        f'<g class="ink" {delay(sweep0 + sweep + .6)}>'
        f'{text("Voice", "the bot\'s first sync,", note_x, 366, 24, fill=BLUE)}'
        f'{text("Voice", f"{first_bot.day} {first_bot:%B %Y}", note_x + 18, 392, 24, fill=BLUE)}</g>'
        f'<path class="pen" {delay(sweep0 + sweep + 1)} pathLength="1" stroke="{BLUE}" stroke-width="2.2" '
        f'd="M{note_x + 214:.0f} 376 C{bx - 14:.0f} 372,{bx - 6:.0f} 396,{bx - 3:.0f} 430 M{bx - 3:.0f} 430 l-6 -10 M{bx - 3:.0f} 430 l6 -9"/>'
    )

    # the line, in the human's own hand
    t_end = sweep0 + sweep + 1.4
    s1 = f"I made {human} commits. Then I made the thing"
    s2 = f"that has made {machine:,} more."
    statement = (
        f'<g class="ink" {delay(t_end)}>{text("Voice", s1, X0, 726, 34, fill=BLUE)}</g>'
        f'<g class="ink" {delay(t_end + .3)}>{text("Voice", s2, X0, 766, 34, fill=BLUE)}</g>'
    )
    under_x = X0 + measure("Voice", "that has made ", 34)
    under_w = measure("Voice", f"{machine:,}", 34)
    underline = (
        f'<path class="pen" {delay(t_end + .8)} pathLength="1" stroke="{BLUE}" stroke-width="3" '
        f'd="M{under_x - 2:.0f} 774 C{under_x + under_w * .4:.0f} 770,{under_x + under_w * .7:.0f} 773,{under_x + under_w + 4:.0f} 768"/>'
    )
    facts = (
        text("Mono", "PYTHON / GITHUB ACTIONS / ONESIGNAL / PWA", X1, 726, 10, tracking=1, fill=PENCIL, anchor="end")
        + text("Mono", "DEADLINE-DASH.VERCEL.APP", X1, 744, 10, tracking=1, fill=INK, anchor="end")
    )

    css = BASE_CSS + feed_css
    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{title}{tagline}{what}{window}'
        f"{axis}{ticks}{chart}{lm}{lh}{bot_note}{rule(686, t_end - .2, X0, X1)}{statement}{underline}{facts}"
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, css,
        title="Deadline Dash",
        desc=f"Case file for Deadline Dash: never miss a CLA again. A chart with one pin per "
             f"commit: {machine:,} commits by the hourly sync bot above the line, {human} "
             f"commits by Tahcin below it. The bot's first sync was {first_bot:%d %B %Y}. "
             f"Handwritten: I made {human} commits. Then I made the thing that has made "
             f"{machine:,} more.",
    )
