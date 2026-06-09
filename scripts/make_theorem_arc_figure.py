#!/usr/bin/env python3
"""Figure 0 — Theorem flow + 3-paper arc orient reader at start of paper."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 6.5), dpi=160)

def box(x, y, w, h, label, sub, fc, ec, fontsize=11):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                   facecolor=fc, edgecolor=ec, lw=1.8, zorder=3)
    ax.add_patch(rect)
    ax.text(x+w/2, y+h*0.62, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color="#222")
    ax.text(x+w/2, y+h*0.25, sub, ha="center", va="center",
            fontsize=9, color="#444", style="italic")

# Row 1: Three theorems (the framework's spine)
box(0.5, 5.4, 3.0, 1.3, "Theorem 1: CIT",
    "Token-only loss has no\nwall-clock gradient.", "#fce8e6", "#a50f15")
box(4.5, 5.4, 3.0, 1.3, "Theorem 2: Reverse-Scaling",
    "Reasoning-token expansion\nmonotonically degrades $|\\rho|$.", "#fce8e6", "#a50f15")
box(8.5, 5.4, 3.0, 1.3, "Theorem 3: SIT",
    "Generalises CIT to any\nexternal metric (space or time).", "#fce8e6", "#a50f15")

# Row 2: Three empirical laws / phenomena
box(0.5, 3.6, 3.0, 1.3, "L1 / L2 / L3",
    "Three empirical laws on\n$\\tau_{\\mathrm{wall}}, \\tau_{\\mathrm{step}}, \\tau_{\\mathrm{self}}$.",
    "#e6f0fc", "#08519c")
box(4.5, 3.6, 3.0, 1.3, "Calibration Catastrophe",
    "Nominally 90% CI achieves\n0–50% actual coverage.", "#e6f0fc", "#08519c")
box(8.5, 3.6, 3.0, 1.3, "Cartographic Problem",
    "Spatial mirror of the\nAugustine Problem.", "#e6f0fc", "#08519c")

# Row 3: Three-paper arc
box(0.5, 1.6, 3.0, 1.3, "Paper 1\n(this paper)",
    "Diagnose. Prove CIT.\nMeasure. Audit harnesses.", "#fffaf0", "#cc6600", 12)
box(4.5, 1.6, 3.0, 1.3, "Paper 2: ChronoStack",
    "Construct: loss extensions,\nwall-clock tools, primitives.", "#fffaf0", "#cc6600", 12)
box(8.5, 1.6, 3.0, 1.3, "Paper 3: Agentic Frontier",
    "Generalise to $(T, S)$ plane.\nJoint deployment bound.", "#fffaf0", "#cc6600", 12)

# Arrows: theorem chain
for x_start, x_end in [(3.5, 4.5), (7.5, 8.5)]:
    ax.annotate("", xy=(x_end, 6.05), xytext=(x_start, 6.05),
                arrowprops=dict(arrowstyle="->", color="#a50f15", lw=2))

# Vertical arrows: theorem → phenomenon
for x in [2.0, 6.0, 10.0]:
    ax.annotate("", xy=(x, 4.92), xytext=(x, 5.38),
                arrowprops=dict(arrowstyle="->", color="#444", lw=1.5))

# Arrows: paper arc
for x_start, x_end in [(3.5, 4.5), (7.5, 8.5)]:
    ax.annotate("", xy=(x_end, 2.25), xytext=(x_start, 2.25),
                arrowprops=dict(arrowstyle="->", color="#cc6600", lw=2))

# Row labels
ax.text(-0.2, 6.05, "Theorems",
        ha="right", va="center", fontsize=11, fontweight="bold", color="#a50f15")
ax.text(-0.2, 4.25, "Empirical /\nstructural\nphenomena",
        ha="right", va="center", fontsize=10, fontweight="bold", color="#08519c")
ax.text(-0.2, 2.25, "Research\nprogramme",
        ha="right", va="center", fontsize=11, fontweight="bold", color="#cc6600")

# Title
ax.text(6, 7.4, "The framework's spine: three theorems, three phenomena, three papers",
        ha="center", fontsize=13.5, fontweight="bold")

ax.set_xlim(-2.5, 12.5)
ax.set_ylim(1, 8)
ax.set_xticks([]); ax.set_yticks([])
for spine in ax.spines.values(): spine.set_visible(False)

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/theorem_arc.pdf")
out_png = Path("paper1/arxiv-v0/figures/theorem_arc.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"Wrote {out_pdf}\nWrote {out_png}")
