#!/usr/bin/env python3
"""Compute T2.3 CAR (Clock-Adherence Ratio) for the reasoning-model panel.

CAR = tau_wall_star / budget, where tau_wall_star is the actual wall-clock
duration the agent used and budget is the wall-clock budget the harness
gave it. Reads T2.3 trajectories from e1-results/ and e3-results/ and
writes a summary table to stdout.
"""
from __future__ import annotations
import json, glob
from statistics import median, mean

FAMILIES = [
    ("e1-results/o3/openai_o3", "o3"),
    ("e1-results/o4-mini/openai_o4-mini", "o4-mini"),
    ("e3-results/claude-sonnet-4-6-thinking/anthropic_claude-sonnet-4-6",
     "Sonnet 4.6 + thinking"),
]


def load_car(path, setting):
    files = sorted(glob.glob(f"{path}/T2.3/{setting}/*.json"))
    cars_by_budget = {}
    for f in files:
        try:
            t = json.load(open(f))
        except Exception:
            continue
        steps = t.get("steps") or []
        if not steps:
            continue
        tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
        b = t.get("budget")
        if b is None or b <= 0 or tw <= 0:
            continue
        cars_by_budget.setdefault(b, []).append(tw / b)
    return cars_by_budget


print(f"{'Model':<26s} {'setting':<14s} {'budget':>8s} {'n':>3s}  {'CAR med':>9s} {'CAR mean':>9s}")
print("-" * 80)
overall = {}
for path, label in FAMILIES:
    for setting in ("no_injection", "with_injection"):
        cars_by_budget = load_car(path, setting)
        agg = []
        for b, cars in sorted(cars_by_budget.items()):
            print(f"{label:<26s} {setting:<14s} {b:>7.0f}s {len(cars):>3d}  "
                  f"{median(cars):>9.4f} {mean(cars):>9.4f}")
            agg.extend(cars)
        if agg:
            print(f"{label:<26s} {setting:<14s} {'PANEL':>8s} {len(agg):>3d}  "
                  f"{median(agg):>9.4f} {mean(agg):>9.4f}")
            overall[(label, setting)] = (median(agg), len(agg))
    print()

print("=" * 80)
print("Summary — panel-median CAR by model+setting (compare vs base panel median 0.016):")
print("=" * 80)
for (label, setting), (m, n) in overall.items():
    print(f"  {label:<26s} {setting:<14s} CAR_median = {m:.4f}  (n={n})")
