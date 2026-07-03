#!/usr/bin/env python3
"""Fig 5 — A.1 positive control (LoRA SFT with wall-clock support).

Two-panel leaderboard: baseline vs fine-tuned |rho| and T3.1 score,
across two Qwen scales. Augustine threshold ε*=0.20 drawn as green
reference. Vendor logo (Qwen) chip in each panel.
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import numpy as np

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"]  = 42
mpl.rcParams["font.family"]  = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Inter", "Helvetica", "Arial", "DejaVu Sans"]

LOGO_DIR = Path("paper1/arxiv-v0/figures/logos")

# Data
s_1b = json.loads(Path("paper2_chronostack/toy_a1/a1_summary.json").read_text())
s_7b = json.loads(Path("paper2_chronostack/toy_a1/a1_7b_summary.json").read_text())

scales = ["Qwen2.5-1.5B", "Qwen2.5-7B"]
base_abs  = [s_1b["baseline"]["median_abs_rho"],  s_7b["baseline"]["median_abs_rho"]]
tuned_abs = [s_1b["finetuned"]["median_abs_rho"], s_7b["finetuned"]["median_abs_rho"]]
base_sc   = [s_1b["effect"]["T3.1_score_baseline"],  s_7b["effect"]["T3.1_score_baseline"]]
tuned_sc  = [s_1b["effect"]["T3.1_score_finetuned"], s_7b["effect"]["T3.1_score_finetuned"]]

EPS_STAR = 0.20
INK  = "#1a1a1a"; INK2 = "#4a4a4a"; RULE = "#c8c8c8"
BASELINE = "#c8c8c8"
TUNED    = "#6a4c93"       # Qwen violet (matches leaderboard vendor colour)

fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2))
fig.subplots_adjust(left=0.06, right=0.98, top=0.85, bottom=0.10, wspace=0.28)

for ax, ys_base, ys_tuned, metric_lbl, ymax_hint in [
    (axes[0], base_abs,  tuned_abs, r"median $|\rho|$", 1.5),
    (axes[1], base_sc,   tuned_sc,  r"T3.1 score",       0.7),
]:
    x = np.arange(len(scales))
    w = 0.34

    b1 = ax.bar(x - w/2, ys_base,  w, color=BASELINE, edgecolor="none",
                label="baseline", zorder=3)
    b2 = ax.bar(x + w/2, ys_tuned, w, color=TUNED,    edgecolor="none",
                label="+ wall-clock LoRA SFT ($\\sim$60 s)", zorder=3)

    for bars, ys in [(b1, ys_base), (b2, ys_tuned)]:
        for b, v in zip(bars, ys):
            ax.text(b.get_x() + b.get_width()/2, v + ymax_hint * 0.03,
                    f"{v:.2f}", ha="center", va="bottom",
                    fontsize=10, fontweight="700", color=INK, zorder=4)

    # Reduction annotation
    for i in range(2):
        pct = (1 - ys_tuned[i] / ys_base[i]) * 100
        mid_y = (ys_base[i] + ys_tuned[i]) / 2
        ax.annotate("", xy=(x[i] + w/2 - 0.03, ys_tuned[i]),
                    xytext=(x[i] - w/2 + 0.03, ys_base[i]),
                    arrowprops=dict(arrowstyle="->", color="#2a7a2a", lw=1.4,
                                    connectionstyle="arc3,rad=-0.18"),
                    zorder=5)
        ax.text(x[i], max(ys_base[i], ys_tuned[i]) + ymax_hint * 0.10,
                f"−{pct:.0f}%", ha="center", fontsize=10,
                fontweight="700", color="#2a7a2a", zorder=6,
                bbox=dict(boxstyle="round,pad=0.15",
                          facecolor="white", edgecolor="#2a7a2a", lw=0.6))

    ax.axhline(EPS_STAR, ls=(0, (4, 3)), lw=1.0, color="#2a7a2a", zorder=1)
    ax.text(-0.35, EPS_STAR, r"$\varepsilon^\star$",
            fontsize=10, color="#2a7a2a", ha="right", va="center",
            fontstyle="italic", fontweight="600")

    ax.set_xticks(x)
    ax.set_xticklabels(scales, fontsize=11, color=INK)
    ax.set_ylabel(metric_lbl, fontsize=11, color=INK)
    ax.set_ylim(0, max(max(ys_base), ymax_hint) * 1.35)
    ax.tick_params(axis="y", labelsize=9, colors=INK2)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#c0c0c0")
        ax.spines[spine].set_linewidth(0.8)

    ax.legend(loc="upper right", frameon=False, fontsize=9.5)

# Panel titles
axes[0].set_title(r"(a) Median $|\rho|$ reduction from wall-clock-supported SFT",
                  loc="left", fontsize=11.5, pad=8, color=INK, fontweight="600",
                  x=0.11)
axes[1].set_title(r"(b) T3.1 axis score — 1.5B crosses $\varepsilon^\star$, 7B partial",
                  loc="left", fontsize=11.5, pad=8, color=INK, fontweight="600",
                  x=0.11)

# Qwen logo chip in each panel (upper-left corner)
qwen_logo = LOGO_DIR / "qwen.png"
if qwen_logo.exists():
    img = mpimg.imread(qwen_logo)
    for ax in axes:
        oi = OffsetImage(img, zoom=0.09)
        ab = AnnotationBbox(oi, (0.03, 0.94), frameon=False,
                            box_alignment=(0, 1), xycoords="axes fraction",
                            zorder=6, pad=0)
        ax.add_artist(ab)

fig.suptitle(
    "Toy positive control: wall-clock signal in the loss support installs chronoception",
    x=0.02, y=0.975, ha="left", fontsize=15, fontweight="700", color=INK,
)
fig.text(0.02, 0.925,
    r"Qwen2.5-{1.5B, 7B}, 30 held-out T3.1 instances each.  LoRA rank $16$, "
    r"three epochs, wall-clock-grounded SFT targets.  "
    r"Dashed green rule = Augustine threshold $\varepsilon^\star=0.20$.  "
    r"The 1.5B fine-tuned agent crosses $\varepsilon^\star$ on the narrative axis.",
    ha="left", fontsize=10, color=INK2, fontstyle="italic")

out_pdf = Path("paper1/arxiv-v0/figures/a1_positive_control.pdf")
out_png = Path("paper1/arxiv-v0/figures/a1_positive_control.png")
fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.15)
fig.savefig(out_png, bbox_inches="tight", pad_inches=0.15, dpi=300)
print(f"Wrote: {out_pdf}")
print(f"Wrote: {out_png}")
