#!/usr/bin/env python3
"""Fig 4 — Agentic Frontier: publication-grade log-log plot."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"]  = 42
mpl.rcParams["font.family"]  = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Inter", "Helvetica", "Arial", "DejaVu Sans"]

INK   = "#1a1a1a"; INK2 = "#4a4a4a"; RULE = "#c8c8c8"
BLUE  = "#3182bd"; CORAL = "#a50f15"; GREEN = "#2a7a2a"
CREAM = "#fffaf0"; PALE_BLUE = "#e6f0fc"; PALE_RED = "#fce8e6"

BENCHMARKS = [
    ("METR HCAST",       1800,   3,  "T-bound",     "#08519c"),
    ("SWE-Bench Lite",    600,   8,  "mixed",       "#a50f15"),
    ("WebArena",          300,  25,  "S-bound",     "#cc6600"),
    ("GAIA",             1200,  60,  "S-bound",     "#4a4a4a"),
    ("MLE-Bench",       86400, 200,  "joint",       "#2a4a2a"),
]

CONTOURS = [
    (0.6,  BLUE,   "Current frontier ($\\varepsilon_{ST} \\approx 0.6$)"),
    (0.2,  CORAL,  "ChronoStack$^+$ target ($\\varepsilon_{ST} \\approx 0.2$)"),
    (0.05, GREEN,  "Grounded agent ($\\varepsilon_{ST} \\approx 0.05$)"),
]

fig, ax = plt.subplots(figsize=(9.5, 6.0))
fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.16)

ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(20, 3e5); ax.set_ylim(0.7, 2e3)
ax.set_xlabel(r"Deployment horizon $T_{\max}$ (wall-clock seconds)",
              fontsize=11.5, color=INK)
ax.set_ylabel(r"Spatial reach $S_{\max}$ (distinct files / pages)",
              fontsize=11.5, color=INK)
ax.grid(True, which="major", ls=":", color=RULE, alpha=0.6)
ax.grid(True, which="minor", ls=":", color=RULE, alpha=0.25)

ax.set_xticks([60, 600, 3600, 36000, 3.6e5])
ax.set_xticklabels(["1 min", "10 min", "1 h", "10 h", "100 h"], fontsize=10)
ax.set_yticks([1, 10, 100, 1000])
ax.set_yticklabels(["1", "10", "100", "1000"], fontsize=10)

# Shaded regions
xs = np.logspace(3.5, 5.5, 20)
ax.fill_between(xs, 0.7, 15, color=PALE_RED, alpha=0.35, zorder=1)
ax.text(6e4, 1.6, "Augustine binding\n(T-axis)",
        ha="center", fontsize=9, color=CORAL,
        fontstyle="italic", zorder=6, fontweight="600")

xs = np.logspace(1.4, 2.6, 20)
ax.fill_between(xs, 40, 2000, color=PALE_BLUE, alpha=0.4, zorder=1)
ax.text(60, 800, "Cartographic binding\n(S-axis)",
        ha="center", fontsize=9, color=BLUE,
        fontstyle="italic", zorder=6, fontweight="600")

# Contour curves — C chosen so ε_ST=0.6 frontier passes through current benchmark cluster
C = 3e4  # calibration constant; ε_ST=0.6 gives T·S=5e4 (roughly current frontier)
xs_c = np.logspace(np.log10(30), np.log10(3e5), 200)
for eps_st, colour, label in CONTOURS:
    ys_c = (C / eps_st) / xs_c
    mask = (ys_c >= 0.7) & (ys_c <= 2e3)
    ax.plot(xs_c[mask], ys_c[mask], color=colour, lw=1.8,
            ls="-" if eps_st == 0.05 else ("--" if eps_st == 0.2 else ":"),
            zorder=3, alpha=0.90, label=label)

ax.legend(loc="lower left", fontsize=9.2, frameon=True,
          facecolor="white", edgecolor=RULE, framealpha=0.95,
          title="$T \\cdot S = C / \\varepsilon_{ST}$",
          title_fontsize=9.5)

# Benchmark points
for label, T, S, cat, colour in BENCHMARKS:
    ax.scatter([T], [S], s=180, color=colour, edgecolors="white",
               linewidths=1.5, zorder=5)
    dx, dy = (1.15, 1.15) if cat == "mixed" else (1.25, 1.20)
    ax.text(T * dx, S * dy, label, fontsize=10.5,
            color=INK, fontweight="600", zorder=6)

# Paper-arc line as bottom caption (not an inset box; avoids overlapping data points)
fig.text(0.5, 0.03,
    "Paper 1 bounds the $T$-axis (Augustine, CIT).   "
    "Paper 3 bounds the $S$-axis (Cartographic, SIT).   "
    "Together: the joint Agentic Frontier.",
    fontsize=9.5, color=INK, ha="center", fontstyle="italic")

fig.suptitle("The Agentic Frontier:  $T_{\\max}(A) \\cdot S_{\\max}(A) \\leq C / \\varepsilon_{ST}(A)$",
             x=0.02, y=0.965, ha="left", fontsize=14, fontweight="700", color=INK)
fig.text(0.02, 0.925,
    "Joint deployment region on the $(T, S)$ plane.  "
    "Five long-horizon benchmarks placed at their characteristic load; "
    "three constant-$\\varepsilon_{ST}$ frontiers plotted.  "
    "Shaded regions name the binding axis.",
    ha="left", fontsize=10, color=INK2, fontstyle="italic")

for spine in ("top", "right"):
    ax.spines[spine].set_color(RULE)
    ax.spines[spine].set_linewidth(0.7)
for spine in ("left", "bottom"):
    ax.spines[spine].set_color("#8a8a8a")
    ax.spines[spine].set_linewidth(0.9)

out_pdf = Path("paper1/arxiv-v0/figures/agentic_frontier.pdf")
out_png = Path("paper1/arxiv-v0/figures/agentic_frontier.png")
fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.15)
fig.savefig(out_png, bbox_inches="tight", pad_inches=0.15, dpi=300)
print(f"Wrote: {out_pdf}\nWrote: {out_png}")

import shutil
shutil.copy(out_pdf, "paper1/iclr27/figures/agentic_frontier.pdf")
shutil.copy(out_pdf, "paper1/iclr27_supp/figures/agentic_frontier.pdf")
print("Copied to iclr27/ + iclr27_supp/")
