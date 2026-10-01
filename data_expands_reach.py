"""Part 1: adding data improves model B (orange) up to its capacity bound.

Render:  uv run manim -qh -p data_expands_reach.py DataExpandsReach
"""

from radar import *


class DataExpandsReach(RadarScene):
    def construct(self):
        self.build(A_LEARNED, B_LEARNED)

        # ~0.8 s hold, one data point every 0.9 s, freeze
        self.wait(0.8)
        for axis, r in DATA_B:
            if r <= B_CAPACITY[axis] + 1e-6:
                self.pop(useful_dot(axis, r, "B"))
                self.play(self.grow("B", axis, r, run_time=0.6))
            else:
                self.pop(unusable_dot(axis, r))
                self.play(self.nudge("B", axis, run_time=0.6))
        self.wait(1.1)
