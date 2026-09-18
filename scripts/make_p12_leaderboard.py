#!/usr/bin/env python3
"""Fig — P12 on METR HCAST, restyled to match the leaderboard figures.

Regenerated from the same filtered corpus the U-test uses, so the figure
and the caption report identical numbers (previously they diverged: the
figure was built from an earlier analysis pass reporting 0.306/0.255
while the text had been updated to 0.318/0.264).

Left panel:  per-model |slope| vs short-horizon success, split by class.
Right panel: class distributions with means and the test statistics.
"""
from __future__ import annotations
import json, glob
from math import log10
from pathlib import Path
from collections import defaultdict
from statistics import mean, median

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Inter", "Helvetica", "Arial", "DejaVu Sans"]

INK, INK2, RULE = "#1a1a1a", "#4a4a4a", "#c8c8c8"
REASON, NONREASON = "#a50f15", "#3182bd"

CANDIDATES = [
    "/tmp/metr_recheck/runs.jsonl",
    "/tmp/metr-eval/runs.jsonl",
]
RUNS = next((p for p in CANDIDATES if Path(p).exists()), None)
if RUNS is None:
    hits = glob.glob("/tmp/**/runs.jsonl", recursive=True)
    RUNS = hits[0] if hits else None
if RUNS is None:
    raise SystemExit("runs.jsonl not found; re-download from METR/eval-analysis-public")
print(f"using {RUNS}")

BUCKETS = [("1-4", 2.5), ("4-15", 9.5), ("15-60", 37.5),
           ("60-240", 150.0), ("240-480", 360.0), (">480", 600.0)]
BM = dict(BUCKETS)


def bucket(t):
    if t < 4: return "1-4"
    if t < 15: return "4-15"
    if t < 60: return "15-60"
    if t < 240: return "60-240"
    if t < 480: return "240-480"
    return ">480"


def is_reasoning(name):
    m = name.lower()
    return any(k in m for k in ["o1", "o2", "o3", "o4", "o5", "codex"])


rows = []
with open(RUNS) as f:
    for line in f:
        if not line.strip(): continue
        d = json.loads(line)
        if d.get("task_source") != "HCAST": continue
        if d.get("score_binarized") is None: continue
        if d.get("human_minutes") is None or d["human_minutes"] <= 0: continue
        if d.get("alias", "").lower() == "human": continue
        rows.append((d["alias"], int(d["score_binarized"]), float(d["human_minutes"])))
print(f"{len(rows)} usable HCAST runs")

by_model = defaultdict(lambda: defaultdict(list))
for alias, score, hm in rows:
    by_model[alias][bucket(hm)].append(score)


def slope(points):
    if len(points) < 2: return None
    xs = [log10(x) for x, _ in points]; ys = [y for _, y in points]
    mx, my = mean(xs), mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else None


models = []
for m, bs in by_model.items():
    total = sum(len(v) for v in bs.values())
    if len(bs) < 4 or total < 100: continue
    rates = {b: sum(v) / len(v) for b, v in bs.items()}
    s = slope([(BM[b], r) for b, r in rates.items()])
    if s is None: continue
    short = rates.get("1-4") or rates.get("4-15")
    if short is None: continue
    models.append({"name": m, "abs_slope": abs(s), "short": short,
                   "n": total, "reasoning": is_reasoning(m)})

R = [m for m in models if m["reasoning"]]
N = [m for m in models if not m["reasoning"]]
mR, mN = mean([m["abs_slope"] for m in R]), mean([m["abs_slope"] for m in N])
print(f"reasoning n={len(R)} mean={mR:.4f} | non-reasoning n={len(N)} mean={mN:.4f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6),
                               gridspec_kw={"width_ratios": [1.55, 1]})
fig.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.14, wspace=0.26)

# ---- Left: scatter ----
for grp, col, lbl in [(N, NONREASON, "non-reasoning"), (R, REASON, "reasoning")]:
    ax1.scatter([m["short"] * 100 for m in grp], [m["abs_slope"] for m in grp],
                s=[max(28, m["n"] / 22) for m in grp], color=col,
                edgecolors="white", linewidths=1.0, alpha=0.9, zorder=3,
                label=f"{lbl} (n={len(grp)})")
ax1.axhline(mR, color=REASON, ls=":", lw=1.3, alpha=0.75, zorder=2)
ax1.axhline(mN, color=NONREASON, ls=":", lw=1.3, alpha=0.75, zorder=2)
ax1.text(ax1.get_xlim()[1], mR, f" mean {mR:.3f}", color=REASON,
         fontsize=8.5, va="bottom", ha="right", style="italic")
ax1.text(ax1.get_xlim()[1], mN, f" mean {mN:.3f}", color=NONREASON,
         fontsize=8.5, va="top", ha="right", style="italic")
ax1.set_xlabel("short-horizon success rate (%, 1–15 min tasks)", fontsize=10.5, color=INK)
ax1.set_ylabel(r"$|$decay slope$|$  ($\Delta$ success / $\Delta\log_{10} T$)",
               fontsize=10.5, color=INK)
ax1.set_title("(a) Per-model decay slope by class", loc="left", fontsize=11,
              fontweight="600", color=INK, pad=7)
ax1.grid(True, ls=":", color=RULE, alpha=0.55)
ax1.legend(loc="upper left", fontsize=9, frameon=True, framealpha=0.95,
           edgecolor=RULE)

# ---- Right: distributions ----
parts = ax2.violinplot([[m["abs_slope"] for m in N], [m["abs_slope"] for m in R]],
                       positions=[0, 1], widths=0.7, showextrema=False)
for pc, col in zip(parts["bodies"], [NONREASON, REASON]):
    pc.set_facecolor(col); pc.set_alpha(0.22); pc.set_edgecolor(col)
for i, (grp, col) in enumerate([(N, NONREASON), (R, REASON)]):
    ys = [m["abs_slope"] for m in grp]
    xs = np.random.default_rng(0).normal(i, 0.055, len(ys))
    ax2.scatter(xs, ys, s=26, color=col, edgecolors="white",
                linewidths=0.8, zorder=3, alpha=0.9)
    ax2.hlines(mean(ys), i - 0.26, i + 0.26, color=col, lw=2.2, zorder=4)
ax2.set_xticks([0, 1])
ax2.set_xticklabels([f"non-reasoning\n(n={len(N)})", f"reasoning\n(n={len(R)})"],
                    fontsize=9.5, color=INK)
ax2.set_ylabel(r"$|$decay slope$|$", fontsize=10.5, color=INK)
ax2.set_title("(b) Class distributions", loc="left", fontsize=11,
              fontweight="600", color=INK, pad=7)
ax2.grid(True, axis="y", ls=":", color=RULE, alpha=0.55)
ax2.text(0.5, 0.965,
         "Mann–Whitney $U{=}58$, one-sided $p{=}0.040$\n"
         "permutation $p{=}0.037$ · $r_{rb}{=}{-}0.55$",
         transform=ax2.transAxes, ha="center", va="top", fontsize=8.8,
         color=INK, bbox=dict(boxstyle="round,pad=0.35", facecolor="#fffaf0",
                              edgecolor=REASON, lw=0.8))

for ax in (ax1, ax2):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#9a9a9a"); ax.spines[sp].set_linewidth(0.85)
    ax.tick_params(labelsize=9, colors=INK2)

fig.suptitle("Pre-registered P12: reasoning models decay faster at horizon",
             x=0.02, y=0.975, ha="left", fontsize=14, fontweight="700", color=INK)
fig.text(0.02, 0.905,
         f"METR HCAST, {len(rows):,} runs after filtering, {len(models)} frontier models.  "
         f"Reasoning mean $|$slope$|$ = {mR:.3f} vs {mN:.3f} non-reasoning "
         f"({(mR/mN-1)*100:.0f}\\% steeper) at matched short-horizon success.",
         ha="left", fontsize=9.6, color=INK2, style="italic")

for out in ["paper1/arxiv-v0/figures/p12_hcast",
            "paper1/iclr27/figures/p12_hcast",
            "paper1/iclr27_supp/figures/p12_hcast"]:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out + ".pdf", bbox_inches="tight", pad_inches=0.15)
fig.savefig("paper1/arxiv-v0/figures/p12_hcast.png", bbox_inches="tight",
            pad_inches=0.15, dpi=300)
print("wrote p12_hcast.pdf to arxiv-v0 / iclr27 / iclr27_supp")
