#!/usr/bin/env python3
"""Figure 2: Calibration Catastrophe (T3.3).

For each panel agent, plot the actual coverage of nominally-90% confidence
intervals. Bar chart sorted by coverage, with the 90% target as a reference
line and the gap visualized.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from statistics import median

# Re-use the T3.3 parser from analyze_e1.py
import sys
sys.path.insert(0, str(Path(__file__).parent))
from analyze_e1 import t3_3_score

# Pull coverage data per agent from e1-results T3.3 trajectories
def load_t33(path_root: str) -> dict:
    out = {}
    for p in Path(path_root).rglob("T3.3/no_injection/*.json"):
        with open(p) as f:
            d = json.load(f)
        agent = d.get("agent_id", "unknown")
        steps = d.get("steps") or []
        if not steps:
            continue
        action = steps[-1].get("action", "")
        tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
        r = t3_3_score(action, tw)
        out.setdefault(agent, {"in_ci": [], "widths": [], "actual": []})
        if r["in_ci"] is not None:
            out[agent]["in_ci"].append(r["in_ci"])
        if r["width"] is not None:
            out[agent]["widths"].append(r["width"])
        out[agent]["actual"].append(tw)
    return out

data = load_t33("e1-results")

# Pretty labels
PRETTY = {
    "anthropic/claude-haiku-4-5":   "Claude Haiku 4.5",
    "anthropic/claude-sonnet-4-6":  "Claude Sonnet 4.6",
    "openai/gpt-4o":                "GPT-4o",
    "openai/gpt-4o-mini":           "GPT-4o-mini",
    "openai/gpt-5.1":               "GPT-5.1",
    "openai/o3":                    "o3 (reasoning)",
    "openai/o4-mini":               "o4-mini (reasoning)",
}

# Compute coverage and 'width factor' (median CI width / median actual)
rows = []
for agent, info in data.items():
    if agent not in PRETTY: continue
    if not info["in_ci"]: continue
    cov = sum(info["in_ci"]) / len(info["in_ci"])
    wid = median(info["widths"]) if info["widths"] else None
    act = median(info["actual"]) if info["actual"] else None
    rows.append({"agent": PRETTY[agent], "coverage": cov, "width": wid,
                 "actual": act, "n": len(info["in_ci"])})

rows.sort(key=lambda r: -r["coverage"])
for r in rows:
    print(f"  {r['agent']:30s} cov={r['coverage']*100:5.1f}%  width={r['width']:5.1f}s  actual={r['actual']:5.1f}s  n={r['n']}")

# Plot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(9, 5.0), dpi=160)

agents = [r["agent"] for r in rows]
covs   = [r["coverage"] for r in rows]
xs = np.arange(len(rows))

# Color by deficit severity (red = worse)
colors = []
for c in covs:
    # 0.9 = green, 0.0 = dark red
    severity = (0.9 - c) / 0.9  # 0 → 1
    r_v = min(1.0, 0.85 + 0.15*severity)
    g_v = max(0.15, 0.85 - 0.55*severity)
    b_v = max(0.15, 0.40 - 0.40*severity)
    colors.append((r_v, g_v, b_v))

bars = ax.bar(xs, [c*100 for c in covs], color=colors, edgecolor="black",
              linewidth=1.0, width=0.7, zorder=3)

# Target line at 90%
ax.axhline(90, ls="--", color="#2a7", lw=1.8, alpha=0.85, zorder=2)
ax.text(-0.4, 92.5, "Nominal coverage target = 90%",
        fontsize=10, color="#2a7", style="italic", ha="left", fontweight="bold")

# Annotate each bar with value above and deficit centered inside (white text)
for i, (b, r) in enumerate(zip(bars, rows)):
    h = b.get_height()
    deficit = 90 - r["coverage"]*100
    # Value above the bar
    ax.text(b.get_x() + b.get_width()/2, h + 2.0, f"{r['coverage']*100:.0f}%",
            ha="center", fontsize=10.5, fontweight="bold")
    # Deficit inside the bar (or above the value if bar is too short)
    if h >= 10:
        ax.text(b.get_x() + b.get_width()/2, h / 2, f"−{deficit:.0f}pp",
                ha="center", va="center", fontsize=9, color="white",
                fontweight="bold")
    else:
        # bar is too short to fit text inside; put deficit BELOW the bar value
        # but high enough to not overlap the 90% line
        ax.text(b.get_x() + b.get_width()/2, 76, f"−{deficit:.0f}pp",
                ha="center", fontsize=8.5, color="#a50f15", fontweight="bold")

ax.set_xticks(xs)
ax.set_xticklabels(agents, rotation=25, ha="right", fontsize=9.5)
ax.set_ylabel("Actual coverage of nominally-90% confidence intervals (%)", fontsize=10.5)
ax.set_ylim(0, 105)
ax.set_yticks([0, 25, 50, 75, 90, 100])
ax.set_title("The Calibration Catastrophe — every panel agent under-covers its own 90% CI on self-duration",
             fontsize=12, pad=14)
ax.grid(True, axis="y", ls=":", alpha=0.4, zorder=1)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Inline annotation: best vs worst, placed at right (above the short-bar agents)
ax.text(0.99, 0.66,
        "Standard calibration tooling\n"
        "(temperature scaling, isotonic regression,\n"
        "RLHF-with-confidence-targets) cannot apply:\n"
        "the loss contains no wall-clock signal\n"
        "(CIT, Theorem 1).",
        transform=ax.transAxes, fontsize=8.5, va="top", ha="right",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#fffaf0",
                  edgecolor="#a50f15", alpha=0.95, lw=1.0))

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/calibration_catastrophe.pdf")
out_png = Path("paper1/arxiv-v0/figures/calibration_catastrophe.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"\nWrote: {out_pdf}\nWrote: {out_png}")
