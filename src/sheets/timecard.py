"""SHEET 07: the time card. A year of contributions, punched.

Each day of the last 53 weeks gets a slot on a buff time card. Quiet days
are a faint pin; busier days get bigger strikes; the busiest days are
punched clean through the paper, so GitHub's own background shows in the
hole. As the punch sweeps, each hole drops its chad.
Data: data/contributions.json, refreshed daily by the print run.
"""
import collections
import datetime as dt
import json
import os

from lib.fonts import measure, text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, shadow, strike

H = 664
DATA = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
CARD = (X0, 316, X1, 532)        # the buff card
GX, GY = X0 + 56, CARD[1] + 44   # grid origin (first slot centre)
BUFF = "#E7D6A4"


def load():
    cal = json.load(open(DATA, encoding="utf-8"))
    weeks = [[(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for d in w["contributionDays"]]
             for w in cal["weeks"]]
    days = [d for w in weeks for d in w]
    return cal["totalContributions"], weeks, days


def stats(days):
    best_streak = streak = 0
    for _, n in days:
        streak = streak + 1 if n else 0
        best_streak = max(best_streak, streak)
    busiest = max(days, key=lambda d: d[1])
    by_wd = collections.Counter()
    for d, n in days:
        by_wd[d.weekday()] += n
    wd = max(by_wd, key=by_wd.get)
    active = sum(1 for _, n in days if n)
    return best_streak, busiest, wd, active


def build():
    total, weeks, days = load()
    best_streak, (bday, bcount), busy_wd, active = stats(days)
    n_weeks = len(weeks)
    pitch = (CARD[2] - 24 - GX) / (n_weeks - 1)

    # size every slot; the top tier is punched out of the paper
    punch_at = max(10, sorted(n for _, n in days)[int(len(days) * .93)])
    slots, holes, chads = [], [], []
    for wi, week in enumerate(weeks):
        t = 1.2 + wi * .045
        x = GX + wi * pitch
        col = []
        for d, n in week:
            # GitHub weeks start on Sunday; put Monday on the top row
            y = GY + ((d.weekday()) % 7) * 24
            if n == 0:
                col.append(f'<circle cx="{x:.1f}" cy="{y}" r="1.1" fill="{PENCIL}" opacity=".55"/>')
            elif n >= punch_at:
                holes.append(f"M{x - 6.2:.1f} {y}a6.2 6.2 0 1 0 12.4 0a6.2 6.2 0 1 0 -12.4 0z")
                col.append(f'<circle cx="{x:.1f}" cy="{y}" r="7.2" fill="none" stroke="{INK}" stroke-width=".8" opacity=".5"/>')
                chads.append(
                    f'<circle class="chad" {delay(t)} cx="{x:.1f}" cy="{y}" r="6.2" fill="{BUFF}"/>'
                )
            else:
                r = 2.0 + 3.6 * min(1, n / punch_at) ** .7
                col.append(f'<circle cx="{x:.1f}" cy="{y}" r="{r:.1f}" fill="{INK}"/>')
        slots.append(f'<g class="k" {delay(t)}>{"".join(col)}</g>')
    t_punch = 1.2 + n_weeks * .045
    # today's slot: the punch that hasn't happened yet
    today_d = days[-1][0]
    tx = GX + (n_weeks - 1) * pitch
    ty0 = GY + today_d.weekday() * 24
    today_ring = (f'<g class="k" {delay(t_punch)}><circle class="blink" cx="{tx:.1f}" cy="{ty0}" r="8.5" '
                  f'fill="none" stroke="{RED}" stroke-width="1.6"/></g>')

    sdefs, sbody = sheet(H, seed=83, uid="c", hole_offset=22, extra_holes="".join(holes))
    head = furniture(7, "TIME CARD")

    # the headline is the number itself
    num = f"{total:,}"
    title = f'<g class="press" {delay(.3)}>{text("Slab", num, X0 - 6, 246, 184, fill=INK)}</g>'
    nw = measure("Slab", num, 184)
    lbl, _ = strike("CONTRIBUTIONS", X0 + nw + 26, 150, .6, 60, pitch=3)
    lbl2, _ = strike("IN THE LAST YEAR", X0 + nw + 26, 180, .9, 60, pitch=3)
    aside = (
        f'<g class="ink" {delay(1.3)}>'
        f'{text("Voice", "mostly in private repos,", X0 + nw + 26, 232, 30, fill=BLUE)}'
        f'{text("Voice", "which is why the public ones look quiet.", X0 + nw + 26, 264, 30, fill=BLUE)}</g>'
    )

    # the card
    months = ""
    seen = set()
    for wi, week in enumerate(weeks):
        d0 = week[0][0]
        key = (d0.year, d0.month)
        if d0.day <= 7 and key not in seen and wi < n_weeks - 2:
            seen.add(key)
            months += text("Mono", d0.strftime("%b").upper(), GX + wi * pitch - 4, CARD[1] + 24, 8.5,
                           tracking=.6, fill=INK, opacity=".7")
    wdays = "".join(
        text("Mono", w, CARD[0] + 18, GY + i * 24 + 3.5, 8.5, tracking=.6, fill=INK, opacity=".7")
        for i, w in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])
    )
    card = (
        f'<g mask="url(#c-mask)">'
        f'<rect x="{CARD[0]}" y="{CARD[1]}" width="{CARD[2] - CARD[0]}" height="{CARD[3] - CARD[1]}" fill="{BUFF}"/>'
        f'<rect x="{CARD[0] + 6}" y="{CARD[1] + 6}" width="{CARD[2] - CARD[0] - 12}" height="{CARD[3] - CARD[1] - 12}" '
        f'fill="none" stroke="{RED}" stroke-width="1" opacity=".55"/>'
        f'{months}{wdays}{"".join(slots)}</g>{"".join(chads)}{today_ring}'
    )

    # the busiest weekday, circled in ballpoint
    ty = GY + busy_wd * 24
    wd_name = ["mondays", "tuesdays", "wednesdays", "thursdays", "fridays", "saturdays", "sundays"][busy_wd]
    ring = (
        f'<path class="pen" {delay(t_punch + .2)} pathLength="1" stroke="{BLUE}" stroke-width="2.2" '
        f'd="M{CARD[0] + 50} {ty - 12} C{CARD[0] + 20} {ty - 14},{CARD[0] + 8} {ty - 2},{CARD[0] + 14} {ty + 8} '
        f'C{CARD[0] + 22} {ty + 16},{CARD[0] + 52} {ty + 12},{CARD[0] + 54} {ty + 1} C{CARD[0] + 55} {ty - 8},{CARD[0] + 42} {ty - 14},{CARD[0] + 30} {ty - 13}"/>'
    )
    legend_y = CARD[3] + 30
    note = (
        f'<g class="ink" {delay(t_punch + .5)}>'
        f'{text("Voice", f"{wd_name}, apparently.", CARD[0], legend_y + 22, 30, fill=BLUE)}</g>'
    )

    facts = [
        ("LONGEST STREAK", f"{best_streak} DAYS"),
        ("BUSIEST DAY", f"{bday:%d %b %Y}: {bcount}".upper()),
        ("ACTIVE DAYS", f"{active} OF {len(days)}"),
    ]
    fx, t, fsvg = 460, t_punch + .3, ""
    for i, (k, v) in enumerate(facts):
        g, t = strike(f"{k:<15}{v}", fx, legend_y + 4 + i * 24, t, 140, pitch=2.1)
        fsvg += g
    css = (
        BASE_CSS
        + ".chad{opacity:0;transform-box:fill-box;transform-origin:50% 50%;animation:chad .5s cubic-bezier(.5,0,1,.5) both}"
        "@keyframes chad{0%{opacity:1;transform:none}100%{opacity:0;transform:translate(3px,22px) rotate(40deg) scale(.8)}}"
    )
    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{title}{lbl}{lbl2}{aside}{card}{ring}{note}{fsvg}'
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    return svg_doc(
        H, inner, css,
        title="Time card",
        desc=f"{total:,} contributions in the last year, mostly in private repositories, shown as a "
             f"punched time card. Longest streak {best_streak} days; busiest day {bday:%d %B %Y} "
             f"with {bcount}; {active} active days; busiest weekday: {wd_name}.",
    )
