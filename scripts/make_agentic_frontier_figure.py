#!/usr/bin/env python3
"""Figure 7 — Agentic Frontier (T,S) plane diagram."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 6.5), dpi=160)

# Plot T·S = const contour for three eps_ST levels
T = np.logspace(0, 4, 400)  # 1s → ~3h
for eps_ST, color, label in [
    (1.2, "#3182bd", "Current frontier agent ($\\varepsilon_{ST}\\approx 0.6$)"),
    (0.5, "#fb6a4a", "ChronoStack+ target ($\\varepsilon_{ST}\\approx 0.2$)"),
    (0.15, "#2a7", "Grounded agent ($\\varepsilon_{ST}\\approx 0.05$)"),
]:
    C = 50000  # arbitrary constant
    S = C / (eps_ST * T)
    S_clip = np.clip(S, 1, 1000)
    ax.plot(T, S_clip, lw=2.5, color=color, label=label)

# Benchmark dots
benchmarks = [
    ("METR HCAST",       1800,  3,  "#08519c"),  # ~30min, ~3 files
    ("SWE-Bench Lite",   600,   8,  "#a50f15"),  # ~10min, ~8 files
    ("WebArena",         300,   25, "#cc6600"),  # ~5min, multi-page
    ("GAIA",             1200,  60, "#666666"),  # ~20min, open web
    ("MLE-Bench",        86400, 200,"#404040"),  # day, large ML pipeline
]
for name, t, s, c in benchmarks:
    ax.scatter([t], [s], s=200, color=c, edgecolor="black", lw=1.5, zorder=5)
    ax.annotate(name, (t, s), xytext=(7, 7), textcoords="offset points",
                fontsize=9.5, fontweight="bold", color=c)

# Augustine Problem region annotation
ax.fill_between([10**3.3, 10**4], 0.5, 1000, color="#fb6a4a", alpha=0.07, zorder=1)
ax.text(10**3.65, 350, "Augustine\nbinding\n($T$-axis)", fontsize=9.5,
        ha="center", color="#a50f15", style="italic", fontweight="bold")
# Cartographic region
ax.fill_between([1, 100], 30, 1000, color="#3182bd", alpha=0.07, zorder=1)
ax.text(10, 350, "Cartographic\nbinding\n($S$-axis)", fontsize=9.5,
        ha="center", color="#08519c", style="italic", fontweight="bold")
# Joint region
ax.fill_between([10**3, 10**4], 30, 500, color="#666666", alpha=0.08, zorder=1)
ax.text(10**3.5, 130, "Joint\nbinding", fontsize=9.5, ha="center",
        color="#222", style="italic", fontweight="bold")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1, 10**4)
ax.set_ylim(0.5, 1000)
ax.set_xlabel(r"Deployment horizon $T_{\max}$ (wall-clock seconds)", fontsize=11)
ax.set_ylabel(r"Spatial reach $S_{\max}$ (distinct files / pages)", fontsize=11)
ax.set_title(r"The Agentic Frontier: $T_{\max}(A)\cdot S_{\max}(A)\leq C/\varepsilon_{ST}(A)$",
             fontsize=12.5, pad=12)
ax.grid(True, which="both", ls=":", alpha=0.4)
ax.legend(loc="lower left", fontsize=9.5, framealpha=0.95)

# Augustine Problem (Paper 1) + Cartographic (Paper 3) markers
ax.text(0.99, 0.02,
        "Paper 1 bounds the $T$-axis (Augustine Problem, CIT).\n"
        "Paper 3 bounds the $S$-axis (Cartographic Problem, SIT).\n"
        "Together they specify the joint Agentic Frontier.",
        transform=ax.transAxes, fontsize=9, va="bottom", ha="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#fffaf0",
                  edgecolor="#a50f15", alpha=0.95, lw=1.0))

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/agentic_frontier.pdf")
out_png = Path("paper1/arxiv-v0/figures/agentic_frontier.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"Wrote {out_pdf}\nWrote {out_png}")
