#!/usr/bin/env python3
"""Figure 6 — A.1 positive control: baseline vs fine-tuned across two model scales."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

s_1b = json.loads(Path("paper2_chronostack/toy_a1/a1_summary.json").read_text())
s_7b = json.loads(Path("paper2_chronostack/toy_a1/a1_7b_summary.json").read_text())
eps_star = 0.20

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=160, gridspec_kw=dict(wspace=0.32))

scales = ["Qwen2.5-1.5B", "Qwen2.5-7B"]
x = np.arange(len(scales))
w = 0.36

base_abs = [s_1b["baseline"]["median_abs_rho"], s_7b["baseline"]["median_abs_rho"]]
tuned_abs = [s_1b["finetuned"]["median_abs_rho"], s_7b["finetuned"]["median_abs_rho"]]
base_score = [s_1b["effect"]["T3.1_score_baseline"], s_7b["effect"]["T3.1_score_baseline"]]
tuned_score = [s_1b["effect"]["T3.1_score_finetuned"], s_7b["effect"]["T3.1_score_finetuned"]]

# Panel (a): |rho|
b1 = ax1.bar(x-w/2, base_abs, w, color="#fb6a4a", edgecolor="black", lw=1.3,
             label="Baseline", zorder=3)
b2 = ax1.bar(x+w/2, tuned_abs, w, color="#3182bd", edgecolor="black", lw=1.3,
             label="+ Wall-clock SFT (LoRA)", zorder=3)
for b, v in zip(b1, base_abs):
    ax1.text(b.get_x()+b.get_width()/2, v+0.04, f"{v:.2f}",
             ha="center", fontsize=10.5, fontweight="bold")
for b, v in zip(b2, tuned_abs):
    ax1.text(b.get_x()+b.get_width()/2, v+0.04, f"{v:.2f}",
             ha="center", fontsize=10.5, fontweight="bold")
# Reduction arrows
for i in range(2):
    pct = (1 - tuned_abs[i]/base_abs[i]) * 100
    ax1.annotate(f"−{pct:.0f}%",
                 xy=(i+w/2, tuned_abs[i]+0.04),
                 xytext=(i-w/2, base_abs[i]-0.15),
                 fontsize=10, color="#222", ha="center", fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="#444", lw=1.5,
                                 connectionstyle="arc3,rad=-0.25"))
ax1.set_xticks(x); ax1.set_xticklabels(scales, fontsize=11)
ax1.set_ylabel(r"Median $|\rho|$ on T3.1", fontsize=11)
ax1.set_ylim(0, 1.65)
ax1.set_title("(a) $|\\rho|$ reduction at two model scales", fontsize=12, pad=10)
ax1.grid(True, axis="y", ls=":", alpha=0.4, zorder=1)
ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
ax1.legend(loc="upper right", fontsize=9.5)

# Panel (b): T3.1 score with eps* line
b3 = ax2.bar(x-w/2, base_score, w, color="#fb6a4a", edgecolor="black", lw=1.3,
             label="Baseline", zorder=3)
b4 = ax2.bar(x+w/2, tuned_score, w, color="#3182bd", edgecolor="black", lw=1.3,
             label="+ Wall-clock SFT (LoRA)", zorder=3)
for b, v in zip(b3, base_score):
    ax2.text(b.get_x()+b.get_width()/2, v+0.018, f"{v:.3f}",
             ha="center", fontsize=10.5, fontweight="bold")
for b, v, crosses in zip(b4, tuned_score, [True, False]):
    if v < eps_star:
        # crosses — inside bar + checkmark above
        ax2.text(b.get_x()+b.get_width()/2, v/2, f"{v:.3f}",
                 ha="center", va="center", fontsize=10.5, color="white", fontweight="bold")
        ax2.annotate(r"crosses $\varepsilon^*$",
                     xy=(b.get_x()+b.get_width()/2, v),
                     xytext=(b.get_x()+b.get_width()/2, v+0.18),
                     ha="center", fontsize=9.5, color="#2a7", fontweight="bold",
                     arrowprops=dict(arrowstyle="->", color="#2a7", lw=1.3))
    else:
        ax2.text(b.get_x()+b.get_width()/2, v+0.018, f"{v:.3f}",
                 ha="center", fontsize=10.5, fontweight="bold")
ax2.axhline(eps_star, ls="--", color="#2a7", lw=2.0, alpha=0.85, zorder=2)
ax2.text(1.45, eps_star-0.025, f"Augustine threshold $\\varepsilon^*={eps_star}$",
         fontsize=10, color="#2a7", style="italic", fontweight="bold", ha="right")
ax2.set_xticks(x); ax2.set_xticklabels(scales, fontsize=11)
ax2.set_ylabel("T3.1 axis score (lower = closer to grounded)", fontsize=11)
ax2.set_ylim(0, 0.82)
ax2.set_title("(b) T3.1 score vs Augustine threshold", fontsize=12, pad=10)
ax2.grid(True, axis="y", ls=":", alpha=0.4, zorder=1)
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)

fig.suptitle("Toy positive control: wall-clock SFT reduces $|\\rho|$ at both scales; "
             "1.5B crosses $\\varepsilon^*$ on T3.1, 7B falls short",
             fontsize=12.5, fontweight="bold", y=1.00)

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/a1_positive_control.pdf")
out_png = Path("paper1/arxiv-v0/figures/a1_positive_control.png")
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"Wrote {out_pdf}\nWrote {out_png}")
