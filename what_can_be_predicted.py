"""Part 3: prediction, not learning. Model A (blue) of subfigures (d, e)
answers query points: interpolation works, extrapolation works, points beyond
the capacity bound fail -- and so do some *inside* it, because they lie beyond
the (revealed at the end) extrapolation reach (dotted olive line).

Render:  uv run manim -qh -p what_can_be_predicted.py WhatCanBePredicted
"""

from radar import *

# subfigures (d, e) are drawn on a radar of radius 139.25 pt instead of 145 pt
K = 145 / 139.25

# radii (pt), axis order d1, d2, d3, d4, d5, ..., d_k-1, d_k
D_LEARNED = [K * r for r in [75.95, 55.22, 66.09, 60.22, 71.95, 56.2, 72.36, 61.35]]
D_CAPACITY = [K * r for r in [114.8, 105.95, 100.1, 91.99, 103.6, 95.02, 108.75, 97.84]]
# olive region of (e): reaches past the learned outline on d_k, d1, d2, d3 only
D_REACH = [K * r for r in [86.36, 78.25, 79.55, 60.22, 71.95, 56.2, 72.36, 75.41]]
D_DATA = [(0, 76.0), (1, 55.2), (2, 65.1), (3, 60.2), (4, 72.0), (5, 55.2),
          (6, 70.5), (7, 61.4)]


# query points (axis, radius in (d)-pt)
INTERP = [(0, 54.9), (2, 42.6), (5, 39.7)]
EXTRAP = [(1, 75.2), (0, 83.0), (2, 77.0), (7, 72.0)]
BEYOND = [(3, 112.7), (2, 106.8), (5, 104.8)]
INSIDE_FAIL = [(3, 80.0), (6, 90.0)]


def at(axis, r):
    return DIRS[axis] * K * r * S


def query(axis, r, ring):
    """Hollow query point with a dashed ring, as in (d)."""
    disc = Circle(radius=5.5 * S).set_fill(BG, 1).set_stroke(width=0)
    rim = dashed(Circle(radius=5.5 * S), 3, 2).set_stroke(ring, 2 * LW)
    return VGroup(disc, rim).move_to(at(axis, r))


def note(lines, color, anchor, target):
    """Annotation in the style of (d): Times, coloured, bold key word, arrow."""
    rows = VGroup()
    for txt, weight, size in lines:
        t = Text(txt, font="Times New Roman", weight=weight, color=color)
        t.scale(size * 0.45 * S / Text("x", font="Times New Roman").height)
        rows.add(t)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=3 * S)
    rows.move_to(np.array([anchor[0] * S, anchor[1] * S, 0]), aligned_edge=LEFT)
    start = rows.get_left() + LEFT * 4 * S
    end = target + normalize(start - target) * 9 * S
    arrow = Arrow(start, end, buff=0, stroke_width=1 * LW, color=color,
                  tip_length=9 * S, max_tip_length_to_length_ratio=1,
                  max_stroke_width_to_length_ratio=100)
    return VGroup(rows, arrow)


def dotted(mob, color):
    n = int(round(mob.get_arc_length() / (5 * S)))
    d = DashedVMobject(mob, num_dashes=n, dashed_ratio=0.02)
    d.set_stroke(color, 2.6 * LW)
    for sub in d.submobjects:
        sub.cap_style = CapStyleType.ROUND
    return d


class WhatCanBePredicted(RadarScene):
    def construct(self):
        self.build(D_LEARNED, a_capacity=D_CAPACITY)
        self.dots.add(*[dot(a, K * r, BLUE_D) for a, r in D_DATA])
        self.wait(0.6)

        def ask(axis, r, ring=None):
            ring = ring or (OLIVE if K * r <= D_LEARNED[axis] else RED)
            q = query(axis, r, ring)
            self.pop(q)
            self.wait(0.15)
            return q

        def succeed(q):
            self.play(q[0].animate.set_fill(GREEN), q[1].animate.set_stroke(OLIVE, 1.5 * LW),
                      run_time=0.35)

        def fail(q):
            self.play(q[0].animate.set_fill(FAIL), q[1].animate.set_stroke(RED),
                      run_time=0.35)
            self.play(Wiggle(q, scale_value=1.15, rotation_angle=0.03 * TAU),
                      run_time=0.4)

        def show_note(n, hold=1.0):
            self.play(FadeIn(n[0], shift=LEFT * 4 * S), GrowArrow(n[1]), run_time=0.4)
            self.wait(hold)
            self.play(FadeOut(n), run_time=0.3)

        # 1 -- interpolation ----------------------------------------------------
        q = ask(*INTERP[0])
        succeed(q)
        show_note(note([("predicting via", NORMAL, 19.9),
                        ("interpolation", BOLD, 19.9)],
                       TXT_INTER, (60, 170), q.get_center()))
        for a, r in INTERP[1:]:
            succeed(ask(a, r))

        # 2 -- extrapolation (succeeds) ----------------------------------------
        q = ask(*EXTRAP[0])
        succeed(q)
        show_note(note([("prediction via", NORMAL, 19.9),
                        ("extrapolation", BOLD, 19.9)],
                       TXT_EXTRA, (150, 120), q.get_center()))
        for a, r in EXTRAP[1:]:
            succeed(ask(a, r))

        # 3 -- beyond the capacity bound (fails) --------------------------------
        q = ask(*BEYOND[0])
        fail(q)
        show_note(note([("strictly unpredictable", NORMAL, 19.9),
                        ("(not within capacity bounds)", NORMAL, 14.0)],
                       TXT_FAIL, (150, -120), q.get_center()))
        for a, r in BEYOND[1:]:
            fail(ask(a, r))

        # 4 -- inside the capacity bound, still fails ---------------------------
        qs = []
        for a, r in INSIDE_FAIL:
            q = ask(a, r)
            fail(q)
            qs.append(q)
        puzzled = note([("within capacity bounds,", NORMAL, 19.9),
                        ("yet unpredictable?", BOLD, 19.9)],
                       TXT_FAIL, (150, -60), qs[0].get_center())
        self.play(FadeIn(puzzled[0], shift=LEFT * 4 * S), GrowArrow(puzzled[1]),
                  run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(puzzled), run_time=0.3)

        # 5 -- reveal: the extrapolation reach ----------------------------------
        reach = Polygon(*radar_pts(D_REACH))
        region = Difference(reach, Polygon(*radar_pts(D_LEARNED))) \
            .set_fill(REACH_FILL, 1).set_stroke(width=0)
        line = dotted(reach, OLIVE)
        self.under.add(region)
        self.add(line)
        self.bring_to_front(self.dots)
        self.play(Create(line), FadeIn(region), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)
        reveal = note([("extrapolation reach", BOLD, 19.9),
                       ("narrower than the capacity bound", NORMAL, 14.0)],
                      TXT_INTER, (150, 95), at(1, 78.25) * 1.0)
        show_note(reveal, hold=1.5)
        self.wait(1.0)
