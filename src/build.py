"""Build every asset into ../assets.  usage: python build.py [name ...]"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sheets import deadline, end, hero, hooks, island, ledger, parchi, timecard  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")


def today():
    return datetime.date.today().strftime("%d %b %Y")


BUILDERS = {
    "hero": lambda: hero.build(today()),
    "hooks": hooks.build,
    "parchi": parchi.build,
    "deadline": deadline.build,
    "island": lambda: island.build(datetime.date.today()),
    "ledger": ledger.build,
    "timecard": timecard.build,
    "end": lambda: end.build(today()),
}


def main(names):
    os.makedirs(OUT, exist_ok=True)
    for name in names or BUILDERS:
        svg = BUILDERS[name]()
        path = os.path.join(OUT, f"{name}.svg")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(svg)
        print(f"{name:14s} {len(svg.encode()) / 1024:7.1f} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
