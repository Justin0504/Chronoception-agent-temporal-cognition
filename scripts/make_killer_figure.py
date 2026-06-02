#!/usr/bin/env python3
"""Generate the killer figure: Reverse-Scaling Theorem visualization.

x-axis: median wall-clock duration per trajectory (proxy for reasoning compute)
y-axis: |rho| = |log10(tau_self / tau_wall)|
Two model families: o4-mini (low/medium/high effort) + Sonnet 4.6 (no/with thinking).
Horizontal line at Augustine threshold contribution.
"""
from __future__ import annotations
import json
from pathlib import Path
from math import log10
from statistics import median


def load_t31_rhos(*globs: str) -> list[tuple[float, float]]:
    out = []
    for g in globs:
        for path in Path(".").rglob(g):
            try:
                with open(path) as f:
                    d = json.load(f)
            except Exception:
                continue
            if d.get("capability_code") != "T3.1":
                continue
            if d.get("metadata", {}).get("setting") != "no_injection":
                continue
            steps = d.get("steps") or []
            if not steps:
                continue
            tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
            ts = d.get("self_narrated_duration")
            if ts and ts > 0 and tw > 0:
                out.append((tw, log10(ts / tw)))
    return out


def summarize(label: str, points: list[tuple[float, float]]) -> dict:
    if not points:
        return {"label": label, "n": 0}
    tws = [p[0] for p in points]
    abs_rhos = [abs(p[1]) for p in points]
    raw_rhos = [p[1] for p in points]
    return {
        "label": label, "n": len(points),
        "median_tau_wall": median(tws),
        "median_abs_rho": median(abs_rhos),
        "median_rho": median(raw_rhos),
        "raw": points,
    }


groups = [
    summarize("o4-mini (low effort)",    load_t31_rhos("e2-results/o4-mini-low/**/T3.1/no_injection/*.json")),
    summarize("o4-mini (medium effort)", load_t31_rhos("pilot-results/openai_o4-mini/T3.1/no_injection/*.json")),
    summarize("o4-mini (high effort)",   load_t31_rhos("e2-results/o4-mini-high/**/T3.1/no_injection/*.json")),
    summarize("Sonnet 4.6 (no thinking)", load_t31_rhos("pilot-results/anthropic_claude-sonnet-4-6/T3.1/no_injection/*.json")),
    summarize("Sonnet 4.6 (+ thinking)",  load_t31_rhos("e3-results/claude-sonnet-4-6-thinking/**/T3.1/no_injection/*.json")),
]

print("Group summary:")
for g in groups:
    if g["n"]:
        print(f"  {g['label']:35s} n={g['n']:3d}  med_tw={g['median_tau_wall']:6.2f}s  med|ρ|={g['median_abs_rho']:.3f}  med_ρ={g['median_rho']:+.3f}")

# ---------------- Plot ----------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Two-panel side-by-side. Left = intra-model (o4-mini). Right = cross-model (Sonnet).
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0), dpi=160,
                                gridspec_kw=dict(width_ratios=[1, 1], wspace=0.28))

# Augustine threshold line on both
AUGUSTINE = 0.20
COLORS = {
    "o4-mini (low effort)":    "#fcae91",
    "o4-mini (medium effort)": "#fb6a4a",
    "o4-mini (high effort)":   "#a50f15",
    "Sonnet 4.6 (no thinking)": "#9ecae1",
    "Sonnet 4.6 (+ thinking)":  "#08519c",
}

# ---- LEFT PANEL: o4-mini ----
o4 = [g for g in groups if g["label"].startswith("o4-mini") and g["n"]]
o4.sort(key=lambda g: g["median_tau_wall"])

# Scatter the raw points (faint)
for g in o4:
    xs = [p[0] for p in g["raw"]]
    ys = [abs(p[1]) for p in g["raw"]]
    ax1.scatter(xs, ys, c=COLORS[g["label"]], s=22, alpha=0.25, edgecolors="none", zorder=2)

# Medians + connecting line + big markers
med_xs = [g["median_tau_wall"] for g in o4]
med_ys = [g["median_abs_rho"] for g in o4]
ax1.plot(med_xs, med_ys, color="#a50f15", lw=2.2, alpha=0.55, zorder=3)
for g in o4:
    ax1.scatter([g["median_tau_wall"]], [g["median_abs_rho"]],
                c=COLORS[g["label"]], s=260, marker="o",
                edgecolors="black", linewidths=1.6, zorder=5,
                label=f"{g['label']} (n={g['n']})")

# Arrow annotations on each segment
for i in range(len(o4) - 1):
    ax1.annotate("",
                 xy=(o4[i+1]["median_tau_wall"], o4[i+1]["median_abs_rho"]),
                 xytext=(o4[i]["median_tau_wall"], o4[i]["median_abs_rho"]),
                 arrowprops=dict(arrowstyle="-|>", color="#a50f15", lw=2.0, mutation_scale=14),
                 zorder=4)

ax1.axhline(AUGUSTINE, ls="--", color="#444", lw=1.2, alpha=0.7)
ax1.text(1.65, AUGUSTINE + 0.05, "Augustine threshold ε* = 0.20",
         fontsize=9, color="#444", style="italic", ha="left")

# Monotone annotation
ax1.text(0.97, 0.97,
         "|ρ| monotone increase:\n"
         f"  {o4[0]['median_abs_rho']:.2f}  →  {o4[1]['median_abs_rho']:.2f}  →  {o4[2]['median_abs_rho']:.2f}\n"
         "  (low → med → high effort)\n\n"
         "All trajectories under-report\n(ρ < 0): the Hidden-Time sign",
         transform=ax1.transAxes, fontsize=9, va="top", ha="right",
         color="#a50f15",
         bbox=dict(boxstyle="round,pad=0.45", facecolor="white",
                   edgecolor="#a50f15", alpha=0.95, lw=1.2))

ax1.set_xscale("log")
ax1.set_xlim(1.5, 12)
ax1.set_ylim(0, 2.6)
ax1.set_xlabel("Median wall-clock duration per trajectory (s)\n(proxy for reasoning compute spent)", fontsize=10)
ax1.set_ylabel(r"$|\rho| = |\log_{10}(\tau_{\mathrm{self}} / \tau_{\mathrm{wall}})|$", fontsize=11)
ax1.set_title("(a) Intra-model: o4-mini × reasoning_effort", fontsize=11, pad=10)
ax1.grid(True, which="both", ls=":", alpha=0.4)
ax1.legend(loc="lower left", fontsize=8.5, framealpha=0.95)

# ---- RIGHT PANEL: Sonnet 4.6 ----
sn = [g for g in groups if g["label"].startswith("Sonnet") and g["n"]]
sn.sort(key=lambda g: g["median_tau_wall"])

# Scatter
for g in sn:
    xs = [p[0] for p in g["raw"]]
    ys = [abs(p[1]) for p in g["raw"]]
    ax2.scatter(xs, ys, c=COLORS[g["label"]], s=22, alpha=0.32, edgecolors="none", zorder=2)

med_xs = [g["median_tau_wall"] for g in sn]
med_ys = [g["median_abs_rho"] for g in sn]
ax2.plot(med_xs, med_ys, color="#08519c", lw=2.2, alpha=0.55, zorder=3)
for g in sn:
    ax2.scatter([g["median_tau_wall"]], [g["median_abs_rho"]],
                c=COLORS[g["label"]], s=260, marker="s",
                edgecolors="black", linewidths=1.6, zorder=5,
                label=f"{g['label']} (n={g['n']})")

# Arrow
ax2.annotate("",
             xy=(sn[-1]["median_tau_wall"], sn[-1]["median_abs_rho"]),
             xytext=(sn[0]["median_tau_wall"], sn[0]["median_abs_rho"]),
             arrowprops=dict(arrowstyle="-|>", color="#08519c", lw=2.0, mutation_scale=14),
             zorder=4)

ax2.axhline(AUGUSTINE, ls="--", color="#444", lw=1.2, alpha=0.7)
ax2.text(8.0, AUGUSTINE + 0.02, "Augustine threshold ε* = 0.20",
         fontsize=9, color="#444", style="italic", ha="left")

# Sign flip + magnitude annotation
ax2.text(0.97, 0.97,
         "|ρ| more than doubled:\n"
         f"  {sn[0]['median_abs_rho']:.2f}  →  {sn[1]['median_abs_rho']:.2f}\n\n"
         "Sign flipped:\n"
         f"  ρ = {sn[0]['median_rho']:+.2f}  →  {sn[1]['median_rho']:+.2f}\n"
         "(over-report → under-report)",
         transform=ax2.transAxes, fontsize=9, va="top", ha="right",
         color="#08519c",
         bbox=dict(boxstyle="round,pad=0.45", facecolor="white",
                   edgecolor="#08519c", alpha=0.95, lw=1.2))

ax2.set_xscale("log")
ax2.set_xlim(4.5, 15)
ax2.set_ylim(0, 0.6)
ax2.set_xlabel("Median wall-clock duration per trajectory (s)\n(proxy for reasoning compute spent)", fontsize=10)
ax2.set_ylabel(r"$|\rho| = |\log_{10}(\tau_{\mathrm{self}} / \tau_{\mathrm{wall}})|$", fontsize=11)
ax2.set_title("(b) Cross-model: Claude Sonnet 4.6 ± extended thinking", fontsize=11, pad=10)
ax2.grid(True, which="both", ls=":", alpha=0.4)
ax2.legend(loc="lower left", fontsize=8.5, framealpha=0.95)

# Super-title
fig.suptitle("The Reverse-Scaling Theorem — reasoning-token expansion monotonically degrades chronoception",
             fontsize=13.5, y=1.00)

# Source footnote
fig.text(0.5, -0.02,
         "T3.1 retrospective self-duration estimation, Setting A (no harness injection).  "
         "Augustine threshold marks the chronoceptive-grounded boundary (ε* = 0.20).",
         ha="center", fontsize=8.5, color="#555", style="italic")

plt.tight_layout()
out_pdf = Path("paper1/arxiv-v0/figures/reverse_scaling.pdf")
out_png = Path("paper1/arxiv-v0/figures/reverse_scaling.png")
out_pdf.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_pdf, bbox_inches="tight")
plt.savefig(out_png, bbox_inches="tight")
print(f"\nWrote: {out_pdf}\nWrote: {out_png}")
