"""Part 2: data outside model B's (orange) capacity is still useful to a
complementary model A (blue), e.g. a human next to an agentic LLM system.
The last point lies within reach of both and expands both.

Starts on the exact final frame of data_expands_reach.

Render:  uv run manim -qh -p not_all_data_is_for_everyone.py NotAllDataIsForEveryone
"""

from radar import *

# (axis index, radius in pt): outside B's capacity, inside A's capacity
DATA_A = [
    (0, 108.0),   # d1
    (6, 97.0),    # d_k-1
    (1, 92.0),    # d2
    (5, 90.0),    # ...
]
# inside both capacities and beyond both learned outlines: helps both
SHARED = (4, 72.0)  # d5


def shared_dot(axis, r):
    """Useful to both models: half blue, half orange, olive ring."""
    halves = VGroup(*[
        AnnularSector(inner_radius=0, outer_radius=5.5 * S, angle=PI, start_angle=a,
                      fill_color=c, fill_opacity=1, stroke_width=0)
        for a, c in ((PI / 2, BLUE_D), (-PI / 2, ORANGE_D))])
    ring = Circle(radius=5.5 * S).set_stroke(OLIVE, 2 * LW)
    return VGroup(halves, ring).move_to(DIRS[axis] * r * S)


class NotAllDataIsForEveryone(RadarScene):
    def construct(self):
        self.build(A_LEARNED, b_after_part1())
        old = part1_dots()
        self.dots.add(*old)
        self.wait(0.6)

        # the points B could not use are picked up by A
        for (axis, r), d in zip(DATA_B, old):
            if r > B_CAPACITY[axis] + 1e-6:
                self.play(d.animate.set_fill(BLUE_D).set_stroke(OLIVE),
                          self.grow("A", axis, r), run_time=0.8)

        # new data in a region only A can make sense of
        for axis, r in DATA_A:
            self.pop(useful_dot(axis, r, "A"))
            self.play(self.grow("A", axis, r, run_time=0.5))

        # finally, one observation both can learn from
        self.wait(0.2)
        self.pop(shared_dot(*SHARED))
        self.play(self.grow("A", *SHARED), self.grow("B", *SHARED), run_time=0.9)
        self.wait(1.2)
