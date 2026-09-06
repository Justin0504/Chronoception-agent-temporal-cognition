#!/usr/bin/env python3
"""P12 quantitative test: Mann-Whitney U + permutation on per-model HCAST decay slopes.

Extends make_hcast_p12_figure.py from qualitative ("cluster visible by inspection")
to a formal two-sample test between reasoning-model and non-reasoning-model
|slope| distributions.
"""
from __future__ import annotations
import json
from math import log10
from collections import defaultdict
from statistics import mean, median
from pathlib import Path
import random

import numpy as np
from scipy.stats import mannwhitneyu

RUNS = "/tmp/metr-eval/runs.jsonl"


def load_hcast(path):
    rows = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("task_source") != "HCAST": continue
            if d.get("score_binarized") is None: continue
            if d.get("human_minutes") is None or d["human_minutes"] <= 0: continue
            if d.get("alias", "").lower() == "human": continue
            rows.append({
                "model": d["alias"],
                "score": int(d["score_binarized"]),
                "human_minutes": float(d["human_minutes"]),
            })
    return rows


def bucket(t):
    if t < 4: return "1-4"
    if t < 15: return "4-15"
    if t < 60: return "15-60"
    if t < 240: return "60-240"
    if t < 480: return "240-480"
    return ">480"


BM = {"1-4": 2.5, "4-15": 9.5, "15-60": 37.5, "60-240": 150, "240-480": 360, ">480": 600}


def slope(points):
    if len(points) < 2: return None
    xs = [log10(x) for x, _ in points]
    ys = [y for _, y in points]
    mx, my = mean(xs), mean(ys)
    num = sum((x-mx)*(y-my) for x,y in zip(xs, ys))
    den = sum((x-mx)**2 for x in xs)
    return num/den if den > 0 else None


def is_reasoning(name):
    m = name.lower()
    return any(k in m for k in ["o1", "o2", "o3", "o4", "o5", "codex"])


rows = load_hcast(RUNS)
print(f"Loaded {len(rows)} HCAST runs")

by_model = defaultdict(lambda: defaultdict(list))
for r in rows:
    by_model[r["model"]][bucket(r["human_minutes"])].append(r["score"])

results = []
for m, bs in by_model.items():
    total = sum(len(s) for s in bs.values())
    if len(bs) < 4 or total < 100: continue
    rates = {b: sum(s)/len(s) for b, s in bs.items()}
    pts = [(BM[b], r) for b, r in rates.items()]
    sl = slope(pts)
    if sl is None: continue
    results.append({
        "model": m, "slope": sl, "abs_slope": abs(sl),
        "n": total, "is_reasoning": is_reasoning(m),
    })

reasoning = [r["abs_slope"] for r in results if r["is_reasoning"]]
nonreason = [r["abs_slope"] for r in results if not r["is_reasoning"]]

print(f"\nReasoning models ({len(reasoning)}):")
for r in sorted([x for x in results if x["is_reasoning"]], key=lambda x: x["abs_slope"]):
    print(f"  {r['model']:38s} |slope|={r['abs_slope']:.3f}  n={r['n']}")

print(f"\nNon-reasoning models ({len(nonreason)}):")
for r in sorted([x for x in results if not x["is_reasoning"]], key=lambda x: x["abs_slope"]):
    print(f"  {r['model']:38s} |slope|={r['abs_slope']:.3f}  n={r['n']}")

print("\n=== SUMMARY STATS ===")
print(f"reasoning     n={len(reasoning):2d}  mean |slope|={mean(reasoning):.4f}  median={median(reasoning):.4f}")
print(f"non-reasoning n={len(nonreason):2d}  mean |slope|={mean(nonreason):.4f}  median={median(nonreason):.4f}")
print(f"relative     {(mean(reasoning)/mean(nonreason)-1)*100:+.1f}% steeper reasoning")

print("\n=== FORMAL TESTS ===")

# Mann-Whitney U (two-sided, alternative: reasoning distribution > non-reasoning distribution)
u_stat, p_two = mannwhitneyu(reasoning, nonreason, alternative="two-sided")
u_stat_g, p_one = mannwhitneyu(reasoning, nonreason, alternative="greater")
print(f"Mann-Whitney U (two-sided):   U={u_stat:.1f}  p={p_two:.4f}")
print(f"Mann-Whitney U (one-sided g): U={u_stat_g:.1f}  p={p_one:.4f}")

# Permutation test on difference in means, one-sided (reasoning > nonreason)
rng = random.Random(42)
observed = mean(reasoning) - mean(nonreason)
n_iter = 20000
combined = reasoning + nonreason
n_r = len(reasoning)
count_ge = 0
for _ in range(n_iter):
    shuffled = combined[:]
    rng.shuffle(shuffled)
    diff = mean(shuffled[:n_r]) - mean(shuffled[n_r:])
    if diff >= observed:
        count_ge += 1
p_perm = (count_ge + 1) / (n_iter + 1)
print(f"Permutation test (n={n_iter}, one-sided reasoning>nonreason): "
      f"observed_diff={observed:+.4f}  p={p_perm:.4f}")

# Rank-biserial correlation (effect size for Mann-Whitney)
r_rb = 1 - (2 * u_stat) / (len(reasoning) * len(nonreason))
print(f"Rank-biserial correlation:    r = {r_rb:+.3f}  "
      f"({'large' if abs(r_rb) > 0.5 else 'medium' if abs(r_rb) > 0.3 else 'small'} effect)")
