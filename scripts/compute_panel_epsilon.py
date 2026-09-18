#!/usr/bin/env python3
"""Panel epsilon on one consistent convention, computed from the trajectories.

Why this script exists
----------------------
The published epsilon column was produced by `chronoception.bench.metrics.
chronoceptive_calibration_error` over `pilot-results/` alone, and that
combination had two problems that distorted the cross-agent ranking:

1. The alpha axis was never populated. The epsilon routine collects alpha only
   from WALL-axis capabilities carrying a wall-clock budget, but the only
   capability in the 90-trajectory protocol with a wall budget is T2.3, which
   is a STEP-axis capability. So `alpha_terms` was empty for every agent, the
   mean was imputed as 0.0, and its 1/3 weight stayed in the denominator:
   every agent was credited with a perfect score on an axis nobody measured.

2. The imputation was not uniform. Agents with a full 90-trajectory pilot set
   lost one axis (a flat x1.5 deflation). o4-mini had only T3.1 in
   `pilot-results/`, so it lost two (x3.0) -- and o4-mini is the panel's most
   severe confabulator, so the convention flattered precisely the agent whose
   failure the paper leans on hardest.

This script puts every agent on the same two measured axes -- mean |CAR - 1|
over T2.3 and mean |rho| over T3.1 -- drawing T2.3 for the reasoning models
from the Route B-1 corpus where `pilot-results/` has none. Missing axes are
dropped and the remaining weights renormalised, which is what the paper's
Definition says and what `metrics.py` now does.

Usage
-----
    python3 scripts/compute_panel_epsilon.py            # print + write CSV
    python3 scripts/compute_panel_epsilon.py --check    # exit 1 if CSV stale

Writes pilot-results/panel_epsilon.csv, which the leaderboard figure reads so
that the figure can never drift from the trajectories again.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
from math import log10
from pathlib import Path
from statistics import mean, median

OUT = Path("pilot-results/panel_epsilon.csv")
SETTINGS = ("no_injection", "with_injection")

# agent label -> (T2.3 globs for CAR, T3.1 globs for rho). "{s}" is the setting.
PANEL: dict[str, tuple[list[str], list[str]]] = {
    "Claude Sonnet 4.6": (
        ["pilot-results/anthropic_claude-sonnet-4-6/T2.3/{s}/*.json"],
        ["pilot-results/anthropic_claude-sonnet-4-6/T3.1/{s}/*.json"],
    ),
    "Claude Sonnet 4.6 + thinking": (
        ["e3-results/claude-sonnet-4-6-thinking/**/T2.3/{s}/*.json"],
        ["e3-results/claude-sonnet-4-6-thinking/**/T3.1/{s}/*.json"],
    ),
    "gpt-5.1": (
        ["pilot-results/openai_gpt-5.1/T2.3/{s}/*.json"],
        ["pilot-results/openai_gpt-5.1/T3.1/{s}/*.json",
         "e1-results/gpt-5.1/**/T3.1/{s}/*.json"],
    ),
    "GLM-5.2-FP8": (
        ["vultr-results/glm-5.2-fp8/**/T2.3/{s}/*.json"],
        ["vultr-results/glm-5.2-fp8/**/T3.1/{s}/*.json"],
    ),
    "Claude Haiku 4.5": (
        ["pilot-results/anthropic_claude-haiku-4-5/T2.3/{s}/*.json"],
        ["pilot-results/anthropic_claude-haiku-4-5/T3.1/{s}/*.json"],
    ),
    "o3 (reasoning)": (
        ["pilot-results/openai_o3/T2.3/{s}/*.json"],
        ["pilot-results/openai_o3/T3.1/{s}/*.json",
         "e1-results/o3/**/T3.1/{s}/*.json"],
    ),
    "Kimi-K2.6": (
        ["vultr-results/kimi-k2.6/**/T2.3/{s}/*.json"],
        ["vultr-results/kimi-k2.6/**/T3.1/{s}/*.json"],
    ),
    "MiniMax-M2.7": (
        ["vultr-results/minimax-m2.7/**/T2.3/{s}/*.json"],
        ["vultr-results/minimax-m2.7/**/T3.1/{s}/*.json"],
    ),
    "Qwen3.6-27B": (
        ["vultr-results/qwen3.6-27b/**/T2.3/{s}/*.json"],
        ["vultr-results/qwen3.6-27b/**/T3.1/{s}/*.json"],
    ),
    "gpt-4o": (
        ["pilot-results/openai_gpt-4o/T2.3/{s}/*.json"],
        ["pilot-results/openai_gpt-4o/T3.1/{s}/*.json"],
    ),
    "Qwen2.5-7B": (
        ["pilot-results/oss_qwen2.5-7b-instruct-yuezhao/T2.3/{s}/*.json"],
        ["pilot-results/oss_qwen2.5-7b-instruct-yuezhao/T3.1/{s}/*.json"],
    ),
    "o4-mini (reasoning)": (
        # pilot-results has no T2.3 for o4-mini; Route B-1 measured it.
        ["e1-results/o4-mini/**/T2.3/{s}/*.json"],
        ["pilot-results/openai_o4-mini/T3.1/{s}/*.json",
         "e1-results/o4-mini/**/T3.1/{s}/*.json"],
    ),
    "gpt-4o-mini": (
        ["pilot-results/openai_gpt-4o-mini/T2.3/{s}/*.json"],
        ["pilot-results/openai_gpt-4o-mini/T3.1/{s}/*.json"],
    ),
}

# Reasoning-effort ladder, reported separately (Reverse-Scaling on the aggregate).
# T2.3 was only run at the default effort, so the low and high tiers have no CAR
# axis. Mixing a two-axis medium with one-axis neighbours would make the ladder
# incomparable in exactly the way this script exists to prevent, so the ladder is
# reported on the rho axis alone at all three tiers (LADDER_RHO_ONLY).
LADDER_RHO_ONLY = True
LADDER: dict[str, tuple[list[str], list[str]]] = {
    "o4-mini (low)": (
        ["e2-results/o4-mini-low/**/T2.3/{s}/*.json"],
        ["e2-results/o4-mini-low/**/T3.1/{s}/*.json"],
    ),
    "o4-mini (medium)": (
        ["e1-results/o4-mini/**/T2.3/{s}/*.json"],
        ["pilot-results/openai_o4-mini/T3.1/{s}/*.json",
         "e1-results/o4-mini/**/T3.1/{s}/*.json"],
    ),
    "o4-mini (high)": (
        ["e2-results/o4-mini-high/**/T2.3/{s}/*.json"],
        ["e2-results/o4-mini-high/**/T3.1/{s}/*.json"],
    ),
}


def _elapsed(d: dict) -> float | None:
    steps = d.get("steps") or []
    if not steps:
        return None
    return float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])


def car_terms(patterns: list[str]) -> list[float]:
    """|CAR - 1| over trajectories carrying a wall-clock budget."""
    out = []
    for pat in patterns:
        for fp in glob.glob(pat, recursive=True):
            try:
                d = json.load(open(fp))
            except (OSError, json.JSONDecodeError):
                continue
            budget = d.get("budget")
            if d.get("budget_kind") != "wall" or not budget or budget <= 0:
                continue
            tw = _elapsed(d)
            if tw is None:
                continue
            out.append(abs(tw / budget - 1.0))
    return out


def rho_terms(patterns: list[str]) -> list[float]:
    """|rho| = |log10(tau_self / tau_wall)| over trajectories with a parsed duration."""
    out = []
    for pat in patterns:
        for fp in glob.glob(pat, recursive=True):
            try:
                d = json.load(open(fp))
            except (OSError, json.JSONDecodeError):
                continue
            tw = _elapsed(d)
            ts = d.get("self_narrated_duration")
            if tw and tw > 0 and ts and ts > 0:
                out.append(abs(log10(ts / tw)))
    return out


def epsilon_for(car_pats: list[str], rho_pats: list[str], setting: str):
    c = car_terms([p.format(s=setting) for p in car_pats])
    r = rho_terms([p.format(s=setting) for p in rho_pats])
    # Median, not mean: the paper reports median CAR and median rho everywhere
    # else, and two harness-artefact trajectories (gpt-4o-mini T2.3, tau_wall =
    # 14.9 h against a 900 s budget -- a stalled request, not inference) move a
    # mean |CAR-1| from 0.04 to 2.02 and would decide the bottom of the ranking.
    axes = [median(x) for x in (c, r) if x]       # drop empty axes
    eps = sum(axes) / len(axes) if axes else None  # renormalise over those present
    return eps, len(c), len(r)


def build_rows(table: dict) -> list[dict]:
    rows = []
    for label, (car_pats, rho_pats) in table.items():
        rec: dict = {"agent": label}
        for s_ in SETTINGS:
            eps, n_car, n_rho = epsilon_for(car_pats, rho_pats, s_)
            suffix = "A" if s_ == "no_injection" else "B"
            rec[f"eps_{suffix}"] = None if eps is None else round(eps, 4)
            rec[f"car_{suffix}"] = round(median(car_terms([p.format(s=s_) for p in car_pats])), 4) if n_car else None
            rec[f"rho_{suffix}"] = round(median(rho_terms([p.format(s=s_) for p in rho_pats])), 4) if n_rho else None
            rec[f"n_car_{suffix}"] = n_car
            rec[f"n_rho_{suffix}"] = n_rho
        rows.append(rec)
    return rows


FIELDS = ["agent", "eps_A", "eps_B", "car_A", "rho_A", "car_B", "rho_B",
          "n_car_A", "n_rho_A", "n_car_B", "n_rho_B"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed CSV differs from a fresh computation")
    args = ap.parse_args()

    rows = build_rows(PANEL)
    rows.sort(key=lambda r: r["eps_A"] if r["eps_A"] is not None else 9.0)
    ladder = build_rows({k: ([] if LADDER_RHO_ONLY else v[0], v[1])
                         for k, v in LADDER.items()})

    width = max(len(r["agent"]) for r in rows + ladder)
    print(f"{'agent':<{width}}  {'eps(A)':>7}  {'eps(B)':>7}   n_car/n_rho (A)")
    for r in rows + [{"agent": "-- effort ladder --"}] + ladder:
        if "eps_A" not in r:
            print(r["agent"])
            continue
        a = "  --   " if r["eps_A"] is None else f"{r['eps_A']:7.3f}"
        b = "  --   " if r["eps_B"] is None else f"{r['eps_B']:7.3f}"
        print(f"{r['agent']:<{width}}  {a}  {b}   {r['n_car_A']}/{r['n_rho_A']}")

    fresh = [{k: r.get(k) for k in FIELDS} for r in rows]
    if args.check:
        if not OUT.exists():
            print(f"\n{OUT} missing"); return 1
        on_disk = list(csv.DictReader(open(OUT)))
        same = len(on_disk) == len(fresh) and all(
            str(d[k]) == str(f[k]) for d, f in zip(on_disk, fresh) for k in FIELDS
        )
        print("\nCSV up to date" if same else f"\n{OUT} is STALE -- rerun without --check")
        return 0 if same else 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(fresh)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
