"""The motion language. Four verbs, shared by every asset.

STRIKE  the printhead hits paper: a column of pins appears in one frame.
FEED    paper advances: stepped, mechanical, never eased.
PEN     a human marks the printout: a stroke drawn with a soft ease.
SLAM    a rubber stamp lands: overshoot, then rest at a slight angle.
PRESS   heavy type is pressed onto the sheet: one short, hard blow.

Rules:
- The resting (un-animated) state of every element is its final state.
  Animations only describe how things *arrive*, so `prefers-reduced-motion`
  (which disables all animation) shows the finished composition.
- Entrances happen once. The only things that loop are machines
  (a blinking cursor, a feeding log) and they loop slowly.
"""

PEN_EASE = "cubic-bezier(.55,.05,.25,1)"
SLAM_EASE = "cubic-bezier(.2,1.4,.4,1)"

BASE_CSS = f"""
.k{{animation:strike .06s linear both}}
@keyframes strike{{from{{opacity:0}}to{{opacity:1}}}}
.pen{{fill:none;stroke-linecap:round;stroke-linejoin:round;animation:pen .8s {PEN_EASE} both}}
@keyframes pen{{from{{stroke-dasharray:1;stroke-dashoffset:1}}to{{stroke-dasharray:1;stroke-dashoffset:0}}}}
.ink{{animation:inkin .5s {PEN_EASE} both}}
@keyframes inkin{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.slam{{transform-box:fill-box;transform-origin:50% 50%;animation:slam .34s {SLAM_EASE} both}}
@keyframes slam{{0%{{opacity:0;transform:scale(1.9) rotate(var(--r0,-16deg))}}55%{{opacity:1}}100%{{opacity:1;transform:scale(1) rotate(0deg)}}}}
.press{{transform-box:fill-box;transform-origin:0 100%;animation:press .2s cubic-bezier(.2,.9,.3,1) both}}
@keyframes press{{from{{opacity:0;transform:scale(1.06) translateY(-6px)}}to{{opacity:1;transform:none}}}}
.blink{{animation:blink 1.06s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.head{{display:none}}}}
"""


def delay(s):
    return f'style="animation-delay:{s:.3f}s"'
