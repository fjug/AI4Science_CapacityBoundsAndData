"""Shared drawing code for the Fig. 1(a) animations.

All geometry, colours and line weights are taken from source.ai (PDF points,
y pointing down, origin of the radar at (245, 235)).
"""

import numpy as np
from manim import *

# ---------------------------------------------------------------- geometry --
CX, CY = 245.0, 235.0          # radar centre in the .ai file
S = 8.0 / 470.0                # PDF points -> manim units (frame height = 8)
LW = 1.7                       # PDF points -> manim stroke_width (at 1080p)


def P(x, y):
    """PDF coordinates -> manim point."""
    return np.array([(x - CX) * S, -(y - CY) * S, 0.0])


# axis directions, clockwise from 12 o'clock (d1, d2, d3, d4, d5, ..., d_k-1, d_k)
ANGLES = [90 - 45 * i for i in range(8)]
DIRS = [np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0.0]) for a in ANGLES]


def radar_pts(radii):
    return [DIRS[i] * radii[i] * S for i in range(8)]


# radii (pt) read off the vertices of the polygons in source.ai
B_LEARNED = [40.19, 45.0, 44.41, 62.8, 47.58, 45.0, 46.4, 43.6]   # orange solid
B_CAPACITY = [59.92, 66.75, 116.87, 83.7, 76.9, 69.6, 56.94, 56.8]  # orange dashed
A_LEARNED = [75.4, 61.87, 48.2, 40.64, 42.0, 59.4, 69.6, 80.14]   # blue solid
A_CAPACITY = [120.1, 102.53, 87.92, 78.3, 91.72, 98.57, 104.21, 124.69]  # blue dashed

# ------------------------------------------------------------------ colours --
# All colours come from themes.py; THEME=light|dark selects the scheme.
import os
from themes import THEMES

THEME = os.environ.get("THEME", "light")
globals().update({k: ManimColor(v) for k, v in THEMES[THEME].items()})

# --------------------------------------------------------------- data story --
# Part 1 (data_expands_reach): (axis index, radius in pt) fed to model B.
# Inside the orange dashed bound -> learned; outside -> "not actionable",
# only a small nudge to the outline.
DATA_B = [
    (2, 90.0),    # d3: big step
    (4, 57.0),    # d5: well short of the bound, room for the point shared with A (part 2)
    (1, 58.0),    # d2
    (6, 80.0),    # d_k-1: outside B's capacity
    (3, 77.0),    # d4
    (2, 106.0),   # d3: closer to the bound
    (0, 59.92),   # d1: touches the bound
    (7, 92.0),    # d_k: outside B's capacity
    (5, 63.0),    # ...
]
NUDGE = 2.5        # pt the outline moves for an incomprehensible point


def b_after_part1():
    """Model B's radii at the end of part 1."""
    r = list(B_LEARNED)
    for axis, v in DATA_B:
        r[axis] = max(r[axis], v) if v <= B_CAPACITY[axis] + 1e-6 else r[axis] + NUDGE
    return r


# ------------------------------------------------------------------ helpers --
def dashed(mob, dash, gap):
    n = max(1, int(round(mob.get_arc_length() / ((dash + gap) * S))))
    return DashedVMobject(mob, num_dashes=n, dashed_ratio=dash / (dash + gap))


def dot(axis, r, fill, ring=None):
    d = Circle(radius=5.5 * S, fill_color=fill, fill_opacity=1)
    d.set_stroke(ring or fill, width=(2 if ring else 0) * LW)
    return d.move_to(DIRS[axis] * r * S)


def useful_dot(axis, r, model):
    return dot(axis, r, ORANGE_D if model == "B" else BLUE_D, OLIVE)


def unusable_dot(axis, r):
    return dot(axis, r, GREY_FILL, RED)


class RadarScene(Scene):
    """Draws the static radar plus two animatable learned outlines.

    self.a_vals / self.b_vals hold one ValueTracker per axis (radius in pt);
    animating them reshapes the solid outlines and fills.
    """

    def build(self, a_learned, b_learned=None, a_capacity=A_CAPACITY):
        self.camera.background_color = BG

        grid = VGroup(*[dashed(Circle(radius=r * S), 3, 3).set_stroke(GRID, LW)
                        for r in (36.2, 72.5, 108.8)])
        grid.add(Circle(radius=145 * S).set_stroke(GRID, 1.5 * LW))

        axes = VGroup()
        for d in DIRS:
            axes.add(Line(ORIGIN, d * 145 * S).set_stroke(AXIS, LW))
            tip = d * 158.2 * S
            n = np.array([-d[1], d[0], 0])
            axes.add(Polygon(tip, tip - d * 7.2 * S + n * 3.6 * S,
                             tip - d * 7.2 * S - n * 3.6 * S,
                             fill_color=ARROW, fill_opacity=1, stroke_width=0))

        labels = VGroup()
        for main, sub, x0, y1 in [("d", "1", 235, 71), ("d", "2", 362, 124),
                                  ("d", "3", 414, 250), ("d", "4", 362, 377),
                                  ("d", "5", 235, 429), ("d", "k-1", 56, 250),
                                  ("d", "k", 108, 124), ("...", "", 108, 377)]:
            m = Text(main, font="Times New Roman", slant=ITALIC, color=TEXT)
            m.scale_to_fit_height(14.0 * S if main == "d" else 2.2 * S)
            m.move_to(P(x0, y1 - 4.3), aligned_edge=DL)
            labels.add(m)
            if sub:
                s = Text(sub, font="Times New Roman", slant=ITALIC, color=TEXT)
                h = 7.8 if sub[0].isdigit() else 8.2
                s.scale(h * S / Text("1", font="Times New Roman").height)
                s.move_to(m.get_corner(DR) + np.array([0.6 * S, -2.6 * S, 0]),
                          aligned_edge=DL)
                labels.add(s)

        centre = Dot(ORIGIN, radius=7 * S, color=CENTRE)

        self.a_vals = [ValueTracker(r) for r in a_learned]
        self.b_vals = [ValueTracker(r) for r in b_learned] if b_learned else None

        def poly(vals):
            return Polygon(*radar_pts([v.get_value() for v in vals]))

        def fill_layers():
            g = VGroup(poly(self.a_vals).set_fill(FILL_A, 1).set_stroke(width=0))
            if self.b_vals:
                g.add(poly(self.b_vals).set_fill(FILL_B, 1).set_stroke(width=0),
                      Intersection(poly(self.a_vals), poly(self.b_vals))
                      .set_fill(FILL_AB, 1).set_stroke(width=0))
            return g

        layers = [always_redraw(fill_layers)]
        # extra layer above the fills, below outlines (e.g. extrapolation reach)
        self.under = VGroup()
        layers.append(self.under)
        layers.append(always_redraw(
            lambda: poly(self.a_vals).set_stroke(BLUE_S, 2 * LW).set_fill(opacity=0)))
        if self.b_vals:
            layers.append(always_redraw(
                lambda: poly(self.b_vals).set_stroke(ORANGE_S, 2 * LW).set_fill(opacity=0)))
        layers.append(dashed(Polygon(*radar_pts(a_capacity)), 8, 7)
                      .set_stroke(BLUE_D, 2 * LW))
        if self.b_vals:
            layers.append(dashed(Polygon(*radar_pts(B_CAPACITY)), 8, 7)
                          .set_stroke(ORANGE_D, 2 * LW))

        self.dots = VGroup()
        self.add(grid, axes, labels, *layers, centre, self.dots)

    def grow(self, model, axis, r, **kw):
        """Animation moving one vertex of a learned outline out to radius r."""
        v = (self.a_vals if model == "A" else self.b_vals)[axis]
        return v.animate(rate_func=rate_functions.ease_in_out_cubic, **kw) \
                .set_value(max(v.get_value(), r))

    def nudge(self, model, axis, **kw):
        v = (self.a_vals if model == "A" else self.b_vals)[axis]
        return v.animate(rate_func=rate_functions.ease_out_cubic, **kw) \
                .set_value(v.get_value() + NUDGE)

    def pop(self, d, run_time=0.3):
        self.dots.add(d)
        self.play(GrowFromCenter(d, rate_func=rate_functions.ease_out_back),
                  run_time=run_time)


def part1_dots():
    """The data points as they stand at the end of part 1."""
    return [useful_dot(a, r, "B") if r <= B_CAPACITY[a] + 1e-6 else unusable_dot(a, r)
            for a, r in DATA_B]
