#!/usr/bin/env python3
"""Figure 6 — A.1 positive control: baseline vs fine-tuned |rho| on T3.1."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

summary = json.loads(Path("paper2_chronostack/toy_a1/a1_summary.json").read_text())

base_abs = summary["baseline"]["median_abs_rho"]
tuned_abs = summary["finetuned"]["median_abs_rho"]
base_rho = summary["baseline"]["median_rho"]
tuned_rho = summary["finetuned"]["median_rho"]
base_score = summary["effect"]["T3.1_score_baseline"]
tuned_score = summary["effect"]["T3.1_score_finetuned"]
eps_star = 0.20

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=160, gridspec_kw=dict(wspace=0.35))

# Left: |rho|
labels = ["Baseline\nQwen2.5-1.5B", "+ Wall-clock SFT\n(LoRA, 76s training)"]
abs_vals = [base_abs, tuned_abs]
colors = ["#fb6a4a", "#3182bd"]
bars1 = ax1.bar(labels, abs_vals, color=colors, edgecolor="black", lw=1.4, width=0.55, zorder=3)
for b, v in zip(bars1, abs_vals):
    ax1.text(b.get_x()+b.get_width()/2, v+0.05, f"{v:.3f}",
             ha="center", fontsize=12, fontweight="bold")
ax1.set_ylabel(r"Median $|\rho| = |\log_{10}(\tau_\mathrm{self}/\tau_\mathrm{wall})|$", fontsize=11)
ax1.set_ylim(0, 1.65)
# arrow
ax1.annotate("", xy=(1, tuned_abs+0.05), xytext=(0, base_abs-0.1),
             arrowprops=dict(arrowstyle="->", color="black", lw=2.5, connectionstyle="arc3,rad=-0.25"))
ax1.text(0.5, 0.85, "78% reduction", fontsize=11, ha="center",
         fontweight="bold", color="#222",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#444"))
ax1.set_title("(a) Median $|\\rho|$ on T3.1", fontsize=11.5, pad=10)
ax1.grid(True, axis="y", ls=":", alpha=0.4, zorder=1)
ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)

# Right: T3.1 score with epsilon* threshold
score_vals = [base_score, tuned_score]
bars2 = ax2.bar(labels, score_vals, color=colors, edgecolor="black", lw=1.4, width=0.55, zorder=3)
for b, v in zip(bars2, score_vals):
    if v >= eps_star:
        # label above the bar
        ax2.text(b.get_x()+b.get_width()/2, v+0.025, f"{v:.3f}",
                 ha="center", fontsize=11.5, fontweight="bold")
    else:
        # label inside the bar (centered), plus "crosses" below threshold area
        ax2.text(b.get_x()+b.get_width()/2, v/2, f"{v:.3f}",
                 ha="center", va="center", fontsize=11.5, fontweight="bold", color="white")
        ax2.annotate(r"\textbf{crosses $\varepsilon^*$}".replace(r"\textbf{","").replace("}",""),
                     xy=(b.get_x()+b.get_width()/2, v), xytext=(b.get_x()+b.get_width()/2, 0.32),
                     ha="center", fontsize=10, fontweight="bold", color="#2a7",
                     arrowprops=dict(arrowstyle="->", color="#2a7", lw=1.5))
ax2.axhline(eps_star, ls="--", color="#2a7", lw=2.0, alpha=0.85, zorder=2)
ax2.text(-0.45, eps_star+0.018, f"Augustine threshold $\\varepsilon^*={eps_star}$",
         fontsize=10, color="#2a7", style="italic", fontweight="bold", ha="left")
ax2.set_ylabel("T3.1 axis score (lower = closer to grounded)", fontsize=11)
ax2.set_ylim(0, 0.82)
ax2.set_title("(b) T3.1 axis score vs Augustine threshold", fontsize=11.5, pad=10)
ax2.grid(True, axis="y", ls=":", alpha=0.4, zorder=1)
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)

fig.suptitle("Toy positive control: wall-clock SFT installs partial chronoception (60 s LoRA training)",
             fontsize=13, fontweight="bold", y=1.00)

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/a1_positive_control.pdf")
out_png = Path("paper1/arxiv-v0/figures/a1_positive_control.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"Wrote {out_pdf}\nWrote {out_png}")
