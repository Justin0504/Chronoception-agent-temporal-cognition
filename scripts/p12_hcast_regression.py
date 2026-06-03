#!/usr/bin/env python3
"""P12 regression test: HCAST success-rate slope vs chronoception metrics.

Pre-registered prediction P12 (FRAMING §9.4):
  slope(Δ success_rate / Δ log T) ∝ -(1 - CAR(A))

This script tests P12 on the METR HCAST public dataset (24008 runs across
~20 frontier models). For each model:
  1. Bucket tasks by human_minutes (1m / 4m / 15m / 1h / 4h / 8h+).
  2. Compute success rate per bucket.
  3. Fit slope of success_rate vs log10(human_minutes).
  4. Compare slopes across models.

For models in our ChronoBench panel (o3 in particular), we can directly
correlate the slope with our measured CAR / epsilon.
"""
from __future__ import annotations
import json
from pathlib import Path
from math import log10
from collections import defaultdict
from statistics import mean


def load_hcast(path: str) -> list[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("task_source") != "HCAST":
                continue
            if d.get("score_binarized") is None:
                continue
            if d.get("human_minutes") is None or d["human_minutes"] <= 0:
                continue
            if d.get("alias", "").lower() == "human":
                continue
            rows.append({
                "model": d["alias"],
                "score": int(d["score_binarized"]),
                "human_minutes": float(d["human_minutes"]),
            })
    return rows


def bucket(t_min: float) -> str:
    if t_min < 4: return "1-4 min"
    if t_min < 15: return "4-15 min"
    if t_min < 60: return "15-60 min"
    if t_min < 240: return "1-4 h"
    if t_min < 480: return "4-8 h"
    return ">8 h"


BUCKET_MIDPOINTS = {
    "1-4 min":   2.0,
    "4-15 min":  9.0,
    "15-60 min": 35.0,
    "1-4 h":     150.0,
    "4-8 h":     360.0,
    ">8 h":      600.0,
}


def per_model_curve(rows: list[dict]) -> dict:
    """For each model, return dict bucket → success rate (and n)."""
    by_model = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_model[r["model"]][bucket(r["human_minutes"])].append(r["score"])
    out = {}
    for model, buckets in by_model.items():
        out[model] = {b: (sum(scores)/len(scores), len(scores))
                      for b, scores in buckets.items()}
    return out


def slope_fit(points: list[tuple[float, float]]) -> float:
    """OLS slope of y vs log10(x). Returns None if fewer than 2 points."""
    if len(points) < 2:
        return None
    xs = [log10(p[0]) for p in points]
    ys = [p[1] for p in points]
    mx = mean(xs)
    my = mean(ys)
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den = sum((x-mx)**2 for x in xs)
    return num/den if den > 0 else None


rows = load_hcast("/tmp/metr-eval/reports/time-horizon-1-1/data/raw/runs.jsonl")
print(f"Loaded {len(rows)} HCAST runs")

curves = per_model_curve(rows)

# Compute slope per model — keep only models with ≥4 buckets covered and >=100 total runs
results = []
for model, b_data in curves.items():
    total_n = sum(n for _, n in b_data.values())
    if len(b_data) < 4 or total_n < 100:
        continue
    points = [(BUCKET_MIDPOINTS[b], rate) for b, (rate, _) in b_data.items()]
    slope = slope_fit(points)
    if slope is None:
        continue
    short = b_data.get("1-4 min", (None, 0))[0] or b_data.get("4-15 min", (None, 0))[0]
    long_ = b_data.get(">8 h", (None, 0))[0] or b_data.get("4-8 h", (None, 0))[0]
    results.append({
        "model": model,
        "n_total": total_n,
        "n_buckets": len(b_data),
        "short_success": short,
        "long_success": long_,
        "slope": slope,
        "gap": (short - long_) if (short is not None and long_ is not None) else None,
    })

results.sort(key=lambda r: r["slope"])

print("\n=== HCAST: success rate vs log10(human_minutes) slope per model ===")
print(f"{'Model':<38} {'n':>5} {'short_succ':>11} {'long_succ':>10} {'slope':>9} {'gap':>7}")
print("-" * 90)
for r in results:
    short = f"{r['short_success']*100:.0f}%" if r['short_success'] is not None else "—"
    long_ = f"{r['long_success']*100:.0f}%" if r['long_success'] is not None else "—"
    gap = f"{r['gap']*100:.0f}pp" if r['gap'] is not None else "—"
    print(f"{r['model']:<38} {r['n_total']:>5d} {short:>11} {long_:>10} {r['slope']:>+9.3f} {gap:>7}")
