#!/usr/bin/env python3
"""Figure 0: The Three Times ontology — the paper's conceptual diagram.

Shows tau_wall (continuous), tau_step (discrete), tau_self (narrative)
as three parallel timelines for one agent trajectory, with the implicit
identity that grounded chronoception must enforce.
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=160)

# Three timelines stacked vertically
Y_WALL = 4
Y_STEP = 2.5
Y_SELF = 1

# X axis: 0 to 10 (representing the trajectory)
T_END = 10

# ===== tau_wall (continuous, external) =====
# Wide rectangle showing continuous time
ax.barh(Y_WALL, T_END, height=0.6, color="#3182bd", alpha=0.7,
        edgecolor="black", lw=1.5, zorder=3)
ax.text(T_END + 0.3, Y_WALL, r"$\tau_{\mathrm{wall}}$  (external clock, continuous)",
        fontsize=12, va="center", color="#08519c", fontweight="bold")

# Tick marks on the wall axis
for t in range(0, T_END+1):
    ax.plot([t, t], [Y_WALL - 0.35, Y_WALL - 0.55], color="black", lw=0.8, zorder=4)
    ax.text(t, Y_WALL - 0.75, f"{t}s", fontsize=8.5, ha="center", color="#444")

# ===== tau_step (discrete, internal) =====
# Show discrete policy invocations as boxes
step_centers = [1, 2.5, 4.2, 5.5, 7, 8.5, 9.5]  # not evenly spaced — real LLM latencies vary
for i, c in enumerate(step_centers):
    rect = patches.FancyBboxPatch((c - 0.32, Y_STEP - 0.28), 0.64, 0.56,
                                    boxstyle="round,pad=0.02",
                                    facecolor="#fb6a4a", edgecolor="black", lw=1.4, zorder=3)
    ax.add_patch(rect)
    ax.text(c, Y_STEP, f"a_{i}", fontsize=9, ha="center", va="center",
            color="white", fontweight="bold")

ax.text(T_END + 0.3, Y_STEP, r"$\tau_{\mathrm{step}}$  (policy invocations, discrete)",
        fontsize=12, va="center", color="#a50f15", fontweight="bold")
ax.text(T_END + 0.3, Y_STEP - 0.5, r"$\langle \Delta t \rangle$ = average per-step latency",
        fontsize=9.5, va="center", color="#666", style="italic")

# ===== tau_self (narrative, agent's report) =====
# Show as a thought bubble with a number
ax.barh(Y_SELF, T_END, height=0.45, color="#fcd5b5", alpha=0.4,
        edgecolor="#cc6600", lw=1.2, zorder=3)
# A representative self-narrated estimate (much smaller than tau_wall — typical confab)
SELF_REPORT = 2.4
ax.barh(Y_SELF, SELF_REPORT, height=0.45, color="#fcd5b5", alpha=1.0,
        edgecolor="#cc6600", lw=1.2, zorder=4)
ax.text(SELF_REPORT + 0.15, Y_SELF + 0.15, f'"about {int(SELF_REPORT)}s"',
        fontsize=9.5, va="center", color="#cc6600", style="italic", fontweight="bold")

ax.text(T_END + 0.3, Y_SELF, r"$\tau_{\mathrm{self}}$  (agent's self-narration)",
        fontsize=12, va="center", color="#cc6600", fontweight="bold")

# ===== Implicit identity equation (between the three) =====
ax.text(5, 5.55,
        r"Grounded chronoception:  $\tau_{\mathrm{wall}} \approx \tau_{\mathrm{step}} \cdot \langle \Delta t \rangle \approx \tau_{\mathrm{self}}$",
        fontsize=13, ha="center", va="center", fontweight="bold", color="#222",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fffaf0",
                  edgecolor="#444", lw=1.4))

# Arrows showing the identity (or its failure)
# tau_wall to tau_step (factor: <Δt>)
ax.annotate("", xy=(5, Y_STEP + 0.4), xytext=(5, Y_WALL - 0.7),
            arrowprops=dict(arrowstyle="<->", color="#666", lw=1.5))
ax.text(5.15, (Y_WALL + Y_STEP)/2 - 0.05, r"$\langle \Delta t \rangle$",
        fontsize=10, va="center", color="#666", fontweight="bold")

# tau_wall to tau_self gap arrow — shows the Augustine Problem visually
# (the dashed orange arc from the end of wall-time to the much shorter self-narrated bar)
ax.annotate("", xy=(SELF_REPORT + 0.2, Y_SELF + 0.3), xytext=(T_END - 0.5, Y_WALL - 0.6),
            arrowprops=dict(arrowstyle="->", color="#cc6600", lw=2.0, linestyle="--",
                            connectionstyle="arc3,rad=0.30"))

# ===== Three Laws annotations =====
ax.text(0.3, Y_WALL + 0.45, "L1 Parkinson: trained α → 1, native α ≈ 0",
        fontsize=8.5, color="#08519c", style="italic")
ax.text(0.3, Y_STEP + 0.45, "L2 Step-Clock Conflation: CAR < 0.05 across panel",
        fontsize=8.5, color="#a50f15", style="italic")
ax.text(0.3, Y_SELF + 0.45, "L3 Temporal Confabulation: ρ off by 10–100×",
        fontsize=8.5, color="#cc6600", style="italic")

ax.set_xlim(-0.5, T_END + 8.5)
ax.set_ylim(-0.2, 6.5)
ax.set_xticks([])
ax.set_yticks([])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.set_title("The Three Times ontology — chronoception is the policy's enforcement of the implicit identity",
             fontsize=13, pad=12, fontweight="bold")

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/three_times.pdf")
out_png = Path("paper1/arxiv-v0/figures/three_times.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"Wrote: {out_pdf}\nWrote: {out_png}")
