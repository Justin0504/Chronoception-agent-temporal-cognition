#!/usr/bin/env python3
"""E11 figure: L1 on the crossed deadline design.

Left   the budget response itself, tau_wall against the stated deadline, one
       line per question. Parkinson's law would be the diagonal; the measured
       lines are nearly flat, and how flat depends on the question.
Right  why. The fitted elasticity against the task's expansion headroom, the
       duration the agent takes when given no deadline at all.

Authored at ICLR \\linewidth through chronofig, so every fontsize is a literal
printed point size.
"""
from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from math import log10
from statistics import median

import numpy as np

sys.path.insert(0, "scripts")
from chronofig import C, PT, figure, save, tidy  # noqa: E402

DEADLINES = [10, 30, 60, 300, 900]
QLABEL = {
    "q1_capital": "capital of Australia",
    "q2_ww1": "three causes of WWI",
    "q4_carbon": "three carbon strategies",
    "q3_rna": "RNA vs DNA",
    "q6_lighthouse": "short story",
    "q5_transformer": "how a transformer works",
}
# ordered by headroom so the colour ramp carries the variable of interest
QORDER = ["q1_capital", "q2_ww1", "q4_carbon", "q3_rna", "q6_lighthouse", "q5_transformer"]
FOCUS = "gpt-4o-mini"   # the agent with all six questions and the tightest fit


def load():
    rows = []
    for fp in glob.glob("e11-results/*/*.json"):
        try:
            d = json.load(open(fp))
        except (OSError, json.JSONDecodeError):
            continue
        md = d.get("metadata", {})
        if md.get("experiment") != "E11":
            continue
        rows.append((d["agent_id"], md["question_id"], md["deadline_s"],
                     md["framing"], float(d["tau_wall"])))
    return rows


def elasticity(pairs):
    x = np.array([log10(b) for b, t in pairs if t > 0])
    y = np.array([log10(t) for _, t in pairs if t > 0])
    if len(x) < 4 or len(set(x.tolist())) < 2:
        return None
    return float(np.polyfit(x, y, 1)[0])


rows = load()
agents = sorted({r[0] for r in rows})

fig, (ax1, ax2) = figure(width_frac=1.0, aspect=0.50, ncols=2)
fig.subplots_adjust(left=0.105, right=0.985, top=0.70, bottom=0.17, wspace=0.34)

# ---------------- left: budget response, one line per question -------------
ramp = ["#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594"]
for qi, q in enumerate(QORDER):
    xs, ys = [], []
    for b in DEADLINES:
        t = [r[4] for r in rows if r[0] == FOCUS and r[1] == q
             and r[2] == b and r[3] == "neutral"]
        if t:
            xs.append(b); ys.append(median(t))
    if xs:
        ax1.plot(xs, ys, "o-", ms=2.6, lw=1.1, color=ramp[qi],
                 label=QLABEL[q], zorder=3)

# what Parkinson's law would look like, anchored at the smallest budget
anchor = [r[4] for r in rows if r[0] == FOCUS and r[2] == 10 and r[3] == "neutral"]
if anchor:
    a = median(anchor)
    ax1.plot(DEADLINES, [a * b / 10 for b in DEADLINES], ls="--", lw=1.0,
             color=C.bad, zorder=2)
    ax1.text(330, a * 33 * 0.55, "Parkinson's law\n($e=1$)", fontsize=PT.small,
             color=C.bad, ha="center", va="top", style="italic")

ax1.set_xscale("log"); ax1.set_yscale("log")
ax1.set_xticks(DEADLINES)
ax1.set_xticklabels([f"{b}" for b in DEADLINES], fontsize=PT.tick)
ax1.set_xlabel("stated deadline $B$ (s)", fontsize=PT.label, color=C.ink)
ax1.set_ylabel(r"median $\tau_{\mathrm{wall}}$ (s)", fontsize=PT.label, color=C.ink)
ax1.set_title(f"(a) Budget response, {FOCUS}", loc="left",
              fontsize=PT.label, fontweight="600", color=C.ink, pad=5)
ax1.legend(fontsize=PT.small - 0.5, frameon=False, loc="upper left",
           labelspacing=0.25, handlelength=1.4, handletextpad=0.4)
tidy(ax1, grid="both")

# ---------------- right: elasticity against headroom -----------------------
marks = {a: m for a, m in zip(agents, ["o", "s", "^", "D", "v"])}
for agent in agents:
    xs, ys = [], []
    for q in QORDER:
        pairs = [(r[2], r[4]) for r in rows
                 if r[0] == agent and r[1] == q and r[3] == "neutral" and r[2]]
        ctrl = [r[4] for r in rows if r[0] == agent and r[1] == q and r[2] is None]
        e = elasticity(pairs)
        if e is None or not ctrl:
            continue
        xs.append(median(ctrl)); ys.append(e)
    if xs:
        ax2.scatter(xs, ys, s=22, marker=marks[agent], color=C.cool,
                    edgecolors="white", linewidths=0.6, alpha=0.9,
                    zorder=3, label=agent)

ax2.axhline(0, color=C.rule_strong, lw=0.7, zorder=1)
ax2.set_xscale("log")
ax2.set_xlabel("expansion headroom: unconstrained $\\tau_{\\mathrm{wall}}$ (s)",
               fontsize=PT.label, color=C.ink)
ax2.set_ylabel("fitted elasticity $e$", fontsize=PT.label, color=C.ink)
ax2.set_title("(b) Headroom predicts the response", loc="left",
              fontsize=PT.label, fontweight="600", color=C.ink, pad=5)
ax2.legend(fontsize=PT.small - 0.5, frameon=False, loc="upper left",
           labelspacing=0.25, handletextpad=0.2)
tidy(ax2, grid="both")

fig.suptitle("E11: L1 measured on a crossed deadline design",
             x=0.02, y=1.0 - 0.15 / fig.get_figheight(), ha="left",
             fontsize=PT.title, fontweight="700", color=C.ink)
fig.text(0.02, 1.0 - 0.30 / fig.get_figheight(),
         "Six questions x five deadlines x two framings, fully crossed, plus an unconstrained\n"
         "control. Parkinson's law is $e=1$; indifference to the budget is $e=0$.",
         ha="left", va="top", fontsize=PT.small, color=C.ink2,
         fontstyle="italic", linespacing=1.6)

save(fig, "e11_headroom")
