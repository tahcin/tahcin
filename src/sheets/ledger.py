"""SHEET 06: the job log. Smaller hooks, one per greenbar band.

Greenbar paper existed so ledgers were easy to read across; here each job
sits exactly on one band. Everything in this table is stated in the
projects' own READMEs or live sites.
"""
from lib.fonts import text
from lib.motion import BASE_CSS, delay
from lib.paper import BLUE, INK, PENCIL, RED, sheet, svg_doc
from lib.printing import FILTERS, X0, X1, furniture, glyph_defs, shadow, strike

H = 712
ROW0 = 288      # first row top; rows are 48 tall and land on the greenbar bands
JOBS = [
    ("GRADESTONE", "Free notes and practice quizzes for BBA",
     "students: stats, accounting, marketing.", "2025", "LIVE"),
    ("IIMBX TRANSCRIPTS", "Chrome extension that talks to the Open",
     "edX APIs, not the page. Resumes mid-run.", "2026", "MIT"),
    ("READING BOARD", "17 whiteboard summaries on luck and",
     "serendipity. With Pragya and Amrit.", "2026", "RESEARCH"),
    ("TRUESPORTS", "Site for a children's sports coaching",
     "company in Bengaluru. With Priyanshi.", "2026", "CLIENT"),
    ("IMAGE-KIT", "Background removal in the browser",
     "(RMBG-1.4 on the GPU), plus upscaling.", "2025", "TOOL"),
    ("IKS STUDY GUIDE", "A study site for the Indian Knowledge",
     "Systems course: iks.gradestone.in", "2025", "LIVE"),
    ("STATS QUEST", "Statistics revision as a retro pixel",
     "quest.", "2025", "GAME"),
]


def build():
    sdefs, sbody = sheet(H, seed=71, uid="l", hole_offset=34)
    head = furniture(6, "JOB LOG", f"{len(JOBS):02d} JOBS + PRIVATE")

    title = f'<g class="press" {delay(.3)}>{text("Slab", "MORE HOOKS", X0 - 3, 214, 104, fill=INK)}</g>'
    note = (
        f'<g class="ink" {delay(.8)}>{text("Voice", "the smaller ones,", 612, 166, 32, fill=BLUE)}'
        f'{text("Voice", "still catching things.", 632, 202, 32, fill=BLUE)}</g>'
    )

    cols = {"no": X0, "job": X0 + 40, "what": X0 + 280, "year": X1 - 172, "status": X1 - 52}
    hdr = ""
    for key, label in [("no", "NO"), ("job", "JOB"), ("what", "WHAT IT DOES"), ("year", "YEAR")]:
        g, _ = strike(label, cols[key], 262, 1.0, 200, pitch=1.8)
        hdr += g
    g, _ = strike("STATUS", cols["status"] + 30, 262, 1.0, 200, pitch=1.8, anchor="end")
    hdr += g

    rows = ""
    t = 1.3
    for i, (job, w1, w2, year, status) in enumerate(JOBS):
        y = ROW0 + i * 48
        g, t1 = strike(f"{i + 1:02d}", cols["no"], y + 17, t, 160, pitch=2.2)
        rows += g
        g, t1 = strike(job, cols["job"], y + 17, t, 160, pitch=2.2)
        rows += g
        rows += f'<g class="ink" {delay(t + .1)}>'
        rows += text("Mono", w1, cols["what"], y + 22, 11, fill=INK)
        if w2:
            rows += text("Mono", w2, cols["what"], y + 38, 11, fill=INK)
        rows += "</g>"
        g, _ = strike(year, cols["year"], y + 17, t1, 160, pitch=2.2)
        rows += g
        # status stamp
        color = RED if status == "LIVE" else INK
        sw = len(status) * 9.6 + 14
        rot = (-4, 3, -2, 5, -3, 2, -5)[i]
        rows += (
            f'<g transform="translate({cols["status"]} {y + 24}) rotate({rot})" style="mix-blend-mode:multiply">'
            f'<g class="slam" style="animation-delay:{t1 + .25:.2f}s;--r0:{rot * 3}deg" filter="url(#wear)">'
            f'<rect x="{-sw / 2:.1f}" y="-12" width="{sw:.1f}" height="23" rx="3" fill="none" stroke="{color}" stroke-width="2"/>'
            f'{text("Wide", status, 0, 4.5, 11, tracking=1, anchor="middle", fill=color)}</g></g>'
        )
        t = t1 + .1

    foot_y = ROW0 + len(JOBS) * 48
    foot, t_end = strike("PRIVATE JOBS NOT SHOWN: CLIENT WORK, RESEARCH TOOLING, AI EXPERIMENTS",
                         X0, foot_y + 26, t + .2, 200, pitch=1.9)
    tick = (
        f'<path class="pen" {delay(t_end + .2)} pathLength="1" stroke="{BLUE}" stroke-width="2.2" '
        f'd="M{X0 + 2} {foot_y + 70} C{X0 + 120} {foot_y + 64},{X0 + 300} {foot_y + 66},{X0 + 420} {foot_y + 62}"/>'
    )
    links = text("Mono", "GRADESTONE.IN", X1, foot_y + 64, 10, tracking=1, fill=PENCIL, anchor="end")

    inner = (
        f"{shadow(sdefs)}{sbody}"
        f'<g fill="{INK}">{head}</g>{title}{note}{hdr}'
        f'<path d="M{X0} 278H{X1}" stroke="{INK}" stroke-width="1.2"/>{rows}{foot}{tick}{links}'
    )
    inner = f"<defs>{sdefs}{FILTERS}{glyph_defs()}</defs>" + inner
    desc = "Job log, smaller projects: " + "; ".join(
        f"{j.title()}: {a} {b} ({y}, {s.lower()})" for j, a, b, y, s in JOBS
    ) + ". Plus private jobs not shown."
    return svg_doc(H, inner, BASE_CSS, title="More hooks", desc=desc)
