"""Render every movie in every colour theme.

    uv run python render_all.py                  # all movies, all themes, 1080p
    uv run python render_all.py dark             # only the dark theme
    uv run python render_all.py light dark -q l  # quick low-quality drafts

Finished movies land in movies/<theme>/<movie>.mp4.
"""

import argparse
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from themes import THEMES

HERE = Path(__file__).parent
MOVIES = {  # file stem -> scene class
    "data_expands_reach": "DataExpandsReach",
    "not_all_data_is_for_everyone": "NotAllDataIsForEveryone",
    "what_can_be_predicted": "WhatCanBePredicted",
    "uncertainty_guided_acquisition": "UncertaintyGuidedAcquisition",
}
QUALITY_DIR = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}


def render(theme, stem, scene, q):
    media = HERE / "media" / theme / stem   # one dir per job: parallel runs share no cache
    subprocess.run(
        ["manim", f"-q{q}", "--media_dir", str(media), f"{stem}.py", scene],
        cwd=HERE, env={**os.environ, "THEME": theme}, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    out = HERE / "movies" / theme / f"{stem}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(media / "videos" / stem / QUALITY_DIR[q] / f"{scene}.mp4", out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("themes", nargs="*", help=f"any of {list(THEMES)} (default: all)")
    ap.add_argument("-q", default="h", choices=list(QUALITY_DIR))
    args = ap.parse_args()
    args.themes = args.themes or list(THEMES)
    for t in args.themes:
        if t not in THEMES:
            ap.error(f"unknown theme {t!r}, choose from {list(THEMES)}")

    jobs = [(t, stem, scene) for t in args.themes for stem, scene in MOVIES.items()]
    with ThreadPoolExecutor(max_workers=os.cpu_count() // 2 or 1) as pool:
        for out in pool.map(lambda j: render(*j, args.q), jobs):
            print("done", out.relative_to(HERE))
