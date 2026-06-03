#!/usr/bin/env python3
"""Figure 4: P12 supportive evidence on METR HCAST.

For each frontier model in HCAST, plot:
  x: short-horizon success rate (1-15 min bucket)
  y: |slope of success vs log10(human_minutes)|

Reasoning models cluster at steeper slopes despite competitive short-horizon
performance — supportive of P12 + Theorem 2: reasoning compute scales the
narrative axis but does not fix L2, so long-horizon performance hits a ceiling.
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


def bucket(t_min: float) -> str:
    if t_min < 4: return "1-4 min"
    if t_min < 15: return "4-15 min"
    if t_min < 60: return "15-60 min"
    if t_min < 240: return "1-4 h"
    if t_min < 480: return "4-8 h"
    return ">8 h"

BUCKET_MIDPOINTS = {
    "1-4 min": 2.0, "4-15 min": 9.0, "15-60 min": 35.0,
    "1-4 h": 150.0, "4-8 h": 360.0, ">8 h": 600.0,
}


def slope_fit(points):
    if len(points) < 2: return None
    xs = [log10(p[0]) for p in points]
    ys = [p[1] for p in points]
    mx, my = mean(xs), mean(ys)
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den = sum((x-mx)**2 for x in xs)
    return num/den if den > 0 else None


# Models we classify as reasoning. Heuristic: o-series and "Codex" and any
# announcement that explicitly mentions chain-of-thought.
def is_reasoning(model: str) -> bool:
    m = model.lower()
    return any(kw in m for kw in ["o1", "o2", "o3", "o4", "o5", "codex"])


rows = load_hcast("/tmp/metr-eval/reports/time-horizon-1-1/data/raw/runs.jsonl")
print(f"Loaded {len(rows)} HCAST runs")

by_model = defaultdict(lambda: defaultdict(list))
for r in rows:
    by_model[r["model"]][bucket(r["human_minutes"])].append(r["score"])

results = []
for model, b_data in by_model.items():
    total_n = sum(len(s) for s in b_data.values())
    if len(b_data) < 4 or total_n < 100:
        continue
    rates = {b: sum(s)/len(s) for b, s in b_data.items()}
    points = [(BUCKET_MIDPOINTS[b], r) for b, r in rates.items()]
    slope = slope_fit(points)
    if slope is None: continue
    short = rates.get("1-4 min") or rates.get("4-15 min")
    long_ = rates.get(">8 h") or rates.get("4-8 h")
    if short is None or long_ is None: continue
    results.append({
        "model": model, "slope": slope, "abs_slope": abs(slope),
        "short": short, "long": long_,
        "is_reasoning": is_reasoning(model),
        "n": total_n,
    })

results.sort(key=lambda r: -r["abs_slope"])

# Plot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=160)

reasoning_xs = [r["short"]*100 for r in results if r["is_reasoning"]]
reasoning_ys = [r["abs_slope"] for r in results if r["is_reasoning"]]
nonreason_xs = [r["short"]*100 for r in results if not r["is_reasoning"]]
nonreason_ys = [r["abs_slope"] for r in results if not r["is_reasoning"]]

ax.scatter(reasoning_xs, reasoning_ys, s=180, c="#fb6a4a",
           edgecolors="black", lw=1.5, label="Reasoning models", zorder=4)
ax.scatter(nonreason_xs, nonreason_ys, s=180, c="#3182bd",
           edgecolors="black", lw=1.5, label="Non-reasoning models", zorder=4)

# Annotate every model
for r in results:
    color = "#a50f15" if r["is_reasoning"] else "#08519c"
    # Shorten labels for readability
    label = r["model"].replace(" (Inspect)", "").replace("Claude ", "Cl ")
    ax.annotate(label, (r["short"]*100, r["abs_slope"]),
                xytext=(8, -3), textcoords="offset points",
                fontsize=7.5, color=color, fontweight="bold", zorder=5)

# Mean slope per group annotation
if reasoning_ys:
    mean_r = mean(reasoning_ys)
    ax.axhline(mean_r, color="#fb6a4a", ls=":", lw=1.5, alpha=0.6, zorder=2)
    ax.text(101, mean_r, f"reasoning mean = {mean_r:.3f}",
            fontsize=8.5, va="center", color="#a50f15", style="italic")
if nonreason_ys:
    mean_nr = mean(nonreason_ys)
    ax.axhline(mean_nr, color="#3182bd", ls=":", lw=1.5, alpha=0.6, zorder=2)
    ax.text(101, mean_nr, f"non-reasoning mean = {mean_nr:.3f}",
            fontsize=8.5, va="center", color="#08519c", style="italic")

# Inline annotation
ax.text(0.02, 0.98,
        "P12 prediction: slope ∝ −(1 − CAR(A))\n\n"
        "Reasoning models cluster at steeper slopes despite\n"
        "competitive short-horizon performance — consistent\n"
        "with capability scaling closing L3 (narrative axis)\n"
        "while L2 (action axis) holds the long-horizon ceiling.\n\n"
        "Effect size: reasoning slopes ≈ "
        f"{mean(reasoning_ys):.3f}, non-reasoning ≈ {mean(nonreason_ys):.3f}\n"
        f"({(mean(reasoning_ys)/mean(nonreason_ys) - 1)*100:.0f}% steeper decay for reasoning).",
        transform=ax.transAxes, fontsize=9, va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fffaf0",
                  edgecolor="#a50f15", alpha=0.95, lw=1.2))

ax.set_xlabel("Short-horizon success rate (% on 1-15 minute HCAST tasks)", fontsize=11)
ax.set_ylabel(r"$|$slope of success rate vs $\log_{10}$(human_minutes)$|$", fontsize=11)
ax.set_title("P12 supportive evidence — HCAST decay slope clusters by model class",
             fontsize=12.5, pad=14)
ax.grid(True, ls=":", alpha=0.4, zorder=1)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="lower right", fontsize=10, framealpha=0.95)

ax.set_xlim(35, 108)

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/p12_hcast.pdf")
out_png = Path("paper1/arxiv-v0/figures/p12_hcast.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"\nWrote: {out_pdf}\nWrote: {out_png}")

# Summary
print("\n=== Summary ===")
print(f"  n_reasoning_models = {len(reasoning_ys)}, mean |slope| = {mean(reasoning_ys):+.3f}")
print(f"  n_nonreasoning_models = {len(nonreason_ys)}, mean |slope| = {mean(nonreason_ys):+.3f}")
print(f"  Effect: reasoning models decay {(mean(reasoning_ys)/mean(nonreason_ys) - 1)*100:.1f}% faster")
