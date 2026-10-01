"""Part 4: guiding data acquisition by epistemic uncertainty.

Two identical copies of model A from subfigures (d, e). Left: data arrives at
random (biased toward the centre); most of it is redundant and the learned
area grows only now and then. Right: the model is queried everywhere, each
query coloured by its epistemic uncertainty (green = low, red = high); an
experiment is run only at a very uncertain query. Three such experiments gain
as much learned area as all the random data on the left.

Render:  uv run manim -qh -p uncertainty_guided_acquisition.py UncertaintyGuidedAcquisition
"""

from radar import *
from what_can_be_predicted import D_CAPACITY, D_DATA, D_LEARNED, K

N_RANDOM = 20          # random acquisitions on the left (= full data bar)
N_GUIDED = 5           # uncertainty-guided experiments on the right
N_QUERIES = 3          # query points per axis and round (right)
PROBE = 0.65           # queries reach this far from the learned outline toward the bound
# random seeds for the queries (right) and the data (left); found by
# `uv run python uncertainty_guided_acquisition.py`, see find_seeds()
SEED_GUIDED, SEED_RANDOM = 91, 3819

RK = 0.76              # radar size relative to the figure
PANEL_X = 205          # pt from the frame centre to each radar centre
RADAR_Y = 46           # pt above the frame centre
BAR_W, BAR_H = 2 * 145 * RK, 8   # pt
BAR_Y = (-128, -170)   # pt: data bar, area bar


def area(radii):
    """Area of the radar polygon (pt^2)."""
    return 0.5 * np.sin(np.pi / 4) * sum(radii[i] * radii[(i + 1) % 8] for i in range(8))


# -------------------------------------------------------- uncertainty model --
UNC_STOPS = [(0.0, "UNC_0"), (0.35, "UNC_1"), (0.55, "UNC_2"), (1.0, "UNC_3")]


def uncertainty(axis, r, learned):
    """0 deep inside the learned area, ~0.5 at its edge, 1 at the capacity bound."""
    L, C = learned[axis], D_CAPACITY[axis]
    if r <= L:
        return 0.5 * (r / L) ** 4
    return 0.5 + 0.5 * min(1.0, (r - L) / (C - L)) ** 0.6


def unc_color(u):
    for (u0, c0), (u1, c1) in zip(UNC_STOPS, UNC_STOPS[1:]):
        if u <= u1:
            return interpolate_color(globals()[c0], globals()[c1], (u - u0) / (u1 - u0))
    return globals()[UNC_STOPS[-1][1]]


# ------------------------------------------------------ the two data stories --
def guided_rounds(seed=SEED_GUIDED):
    """Per round: the query points (axis, r, u) and the index of the one picked."""
    rng = np.random.default_rng(seed)
    learned, rounds = list(D_LEARNED), []
    for _ in range(N_GUIDED):
        queries = []
        for axis in range(8):
            while True:   # a few radii per axis, not overlapping
                L, C = learned[axis], D_CAPACITY[axis]
                rs = np.sort(rng.uniform(10, L + PROBE * (C - L), N_QUERIES))
                if np.all(np.diff(rs) > 13):
                    break
            queries += [(axis, r, uncertainty(axis, r, learned)) for r in rs]
        u = np.array([q[2] for q in queries])
        w = np.exp((u - u.max()) / 0.03)      # strongly biased toward the reddest
        pick = rng.choice(len(queries), p=w / w.sum())
        rounds.append((queries, pick))
        axis, r, _ = queries[pick]
        learned[axis] = max(learned[axis], r)
    return rounds, learned


def random_data(seed):
    """N_RANDOM (axis, r) points. Radii (as a fraction of the capacity) follow a
    flat-topped distribution: uniform on [0.3, 0.7] blurred by a Gaussian, so
    they spread out instead of piling up near the centre."""
    rng = np.random.default_rng(seed)
    axes = rng.integers(8, size=N_RANDOM)
    u = np.clip(rng.uniform(0.3, 0.7, N_RANDOM) + rng.normal(0, 0.12, N_RANDOM), 0.08, 0.97)
    return [(int(a), D_CAPACITY[a] * f) for a, f in zip(axes, u)]


ROUNDS, GUIDED_FINAL = guided_rounds()
GAIN_GUIDED = area(GUIDED_FINAL) - area(D_LEARNED)

def outcome(points, learned=D_LEARNED):
    """Final learned radii and number of points that expanded the outline."""
    learned, helpful = list(learned), 0
    for a, r in points:
        helpful += r > learned[a]
        learned[a] = max(learned[a], r)
    return learned, helpful


RANDOM = random_data(SEED_RANDOM)
gain = area(outcome(RANDOM)[0]) - area(D_LEARNED)
GAIN_FULL = max(gain, GAIN_GUIDED)   # area bar is full at this gain


# --------------------------------------------------------------- the scene --
def pt(x, y):
    return np.array([x * S, y * S, 0.0])


class Bar:
    """Horizontal progress bar with a label above and a value at its right."""

    def __init__(self, x, y, label, color, fmt):
        self.v = ValueTracker(0)
        left = pt(x - BAR_W / 2, y)
        track = Rectangle(width=BAR_W * S, height=BAR_H * S).set_stroke(GRID, LW * 0.8)
        track.move_to(left, aligned_edge=LEFT)
        title = Text(label, font="Times New Roman", color=TEXT).scale(0.3)
        title.next_to(track, UP, buff=4 * S, aligned_edge=LEFT)
        fill = always_redraw(lambda: Rectangle(
            width=max(1e-3, self.v.get_value()) * BAR_W * S, height=BAR_H * S,
            fill_color=color, fill_opacity=1, stroke_width=0)
            .move_to(left, aligned_edge=LEFT))
        value = always_redraw(lambda: Text(
            fmt(self.v.get_value()), font="Times New Roman", color=TEXT).scale(0.3)
            .next_to(track, RIGHT, buff=6 * S))
        self.group = VGroup(track, fill, title, value)

    def to(self, frac, **kw):
        return self.v.animate(**kw).set_value(frac)


class UncertaintyGuidedAcquisition(Scene):
    def construct(self):
        self.camera.background_color = BG
        base_area = area(D_LEARNED)

        def panel(x, title):
            radar = Radar(D_LEARNED, a_capacity=D_CAPACITY, center=pt(x, RADAR_Y), k=RK)
            radar.dots.add(*[radar.place(dot(0, 0, BLUE_D), a, K * r) for a, r in D_DATA])
            head = Text(title, font="Times New Roman", color=TEXT).scale(0.4)
            head.move_to(pt(x, 213))
            data = Bar(x, BAR_Y[0], "new data acquired", BLUE_D,
                       lambda f: f"{round(f * N_RANDOM)}")
            gain = Bar(x, BAR_Y[1], "new area covered", OLIVE,
                       lambda f: f"+{100 * f * GAIN_FULL / base_area:.0f} %")
            self.add(radar.group, head, data.group, gain.group)
            return radar, data, gain

        left, l_data, l_gain = panel(-PANEL_X, "random data acquisition")
        right, r_data, r_gain = panel(PANEL_X, "guided by epistemic uncertainty")
        self.wait(0.8)

        def acquire(radar, data_bar, gain_bar, n, axis, r, run_time, extra=()):
            """Add one data point; grow the outline if it lies beyond it."""
            useful = r > radar.learned()[axis]
            d = radar.place(dot(0, 0, BLUE_D if useful else REDUNDANT, OLIVE), axis, r)
            radar.dots.add(d)
            anims = [GrowFromCenter(d, rate_func=rate_functions.ease_out_back),
                     data_bar.to(n / N_RANDOM), *extra]
            if useful:
                new = list(radar.learned())
                new[axis] = r
                anims += [radar.grow("A", axis, r),
                          gain_bar.to((area(new) - base_area) / GAIN_FULL,
                                      rate_func=rate_functions.ease_in_out_cubic)]
            self.play(*anims, run_time=run_time if useful else run_time * 0.6)
            return d

        # 1 -- random acquisition: most new data is redundant -------------------
        for n, (axis, r) in enumerate(RANDOM, 1):
            acquire(left, l_data, l_gain, n, axis, r, run_time=0.5)
        self.wait(0.6)

        # 2 -- guided by epistemic uncertainty -----------------------------------
        for i, (queries, pick) in enumerate(ROUNDS):
            slow = [1.5, 1.0, 0.8, 0.7, 0.7][min(i, 4)]   # later rounds faster
            qs = VGroup(*[
                right.place(Circle(radius=4.2 * S).set_fill(unc_color(u), 1)
                            .set_stroke(BG, 0.8 * LW), axis, r)
                for axis, r, u in queries])
            self.add(qs)
            self.play(LaggedStart(*[GrowFromCenter(q) for q in qs], lag_ratio=0.06),
                      run_time=0.9 * slow)
            self.wait(0.4 * slow)

            chosen = qs[pick]
            ring = Circle(radius=9 * S * RK).set_stroke(TEXT, 1.4 * LW).move_to(chosen)
            self.play(Create(ring), chosen.animate.scale(1.3),
                      *[q.animate.set_opacity(0.15) for j, q in enumerate(qs) if j != pick],
                      run_time=0.5 * slow)
            self.play(FadeOut(VGroup(*[q for j, q in enumerate(qs) if j != pick])),
                      run_time=0.25 * slow)
            # the experiment: a real data point where the model was most unsure
            axis, r, _ = queries[pick]
            acquire(right, r_data, r_gain, i + 1, axis, r, run_time=0.7 * slow,
                    extra=[FadeOut(ring), FadeOut(chosen)])
        self.wait(1.5)


def find_seeds(n_guided_seeds=150, n_random_seeds=4000):
    """Seed pairs for which only a handful of the random points help, yet the
    random data gains about the same area as the guided experiments and ends
    in about the same shape. Prints the best few: (shape difference in pt,
    seed guided, seed random, % gain guided, % gain random, helpful points)."""
    base, found = area(D_LEARNED), []
    candidates = []
    for s in range(n_random_seeds):
        final, helpful = outcome(random_data(s))
        if 4 <= helpful <= 7:
            candidates.append((s, np.array(final), area(final) - base, helpful))
    for gs in range(n_guided_seeds):
        g_final = np.array(guided_rounds(gs)[1])
        g_gain = area(g_final) - base
        for s, final, gain_, helpful in candidates:
            if abs(gain_ / g_gain - 1) < 0.04:
                found.append((round(np.abs(final - g_final).sum(), 1), gs, s,
                              round(100 * g_gain / base), round(100 * gain_ / base), helpful))
    for row in sorted(found)[:5]:
        print(row)


if __name__ == "__main__":
    find_seeds()
