"""Refresh the data the sheets are printed from.

Run by the daily print run (.github/workflows/print.yml) before build.py.
Needs GITHUB_TOKEN (or GH_TOKEN) in the environment. Any source that fails
keeps its last good file, so a flaky API never blanks a sheet.
"""
import json
import os
import sys
import urllib.request

USER = "tahcin"
DATA = os.path.join(os.path.dirname(__file__), "data")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def api(url, body=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body else None,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USER}-profile-printer",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def contributions():
    q = (
        '{user(login:"%s"){contributionsCollection{contributionCalendar{'
        "totalContributions weeks{contributionDays{date contributionCount}}}}}}" % USER
    )
    data = api("https://api.github.com/graphql", {"query": q})
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    assert cal["weeks"], "empty calendar"
    path = os.path.join(DATA, "contributions.json")
    if os.path.exists(path):  # a token that can't see private work would halve the count
        old = json.load(open(path, encoding="utf-8"))["totalContributions"]
        assert cal["totalContributions"] >= old * .5, f"total fell {old} -> {cal['totalContributions']}"
    with open(os.path.join(DATA, "contributions.json"), "w", encoding="utf-8") as f:
        json.dump(cal, f)
    return cal["totalContributions"]


def deadline_dash_commits():
    rows, page = [], 1
    while True:
        batch = api(f"https://api.github.com/repos/{USER}/deadline-dash/commits?per_page=100&page={page}")
        if not batch:
            break
        for c in batch:
            login = (c.get("author") or {}).get("login") or "none"
            msg = c["commit"]["message"].split("\n")[0].replace("\t", " ")
            rows.append(f'{c["commit"]["author"]["date"]}\t{login}\t{c["commit"]["author"]["name"]}\t{msg}')
        page += 1
    assert len(rows) > 100, "suspiciously few commits"
    with open(os.path.join(DATA, "deadline_dash_commits.tsv"), "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(rows) + "\n")
    return len(rows)


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("set GITHUB_TOKEN")
    for job in (contributions, deadline_dash_commits):
        try:
            print(f"{job.__name__}: {job()}")
        except Exception as e:  # keep the last good data
            print(f"{job.__name__}: kept previous data ({e})")
