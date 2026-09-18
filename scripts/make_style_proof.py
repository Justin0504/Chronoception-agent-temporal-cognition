#!/usr/bin/env python3
"""Style proof sheet: the glyph set, accents and type scale at true print size.

Not a paper figure. Render it when changing chronofig.py so the design system
can be reviewed as a whole rather than one figure at a time. Because the sheet
is authored at ICLR \\linewidth, the type on screen is the type that prints.
"""
import pathlib
import sys
import textwrap

sys.path.insert(0, "scripts")
pathlib.Path("paper1/figures-style").mkdir(parents=True, exist_ok=True)

import matplotlib.pyplot as plt  # noqa: E402
from chronofig import figure, C, PT, axis_glyph, GLYPH_LABEL, textwidth  # noqa: E402

fig, ax = figure(width_frac=1.0, aspect=0.60)
ax.set_xlim(0,100); ax.set_ylim(0,60); ax.axis("off")

ax.text(0,59,"Three Times glyph set", fontsize=PT.title, fontweight="700", color=C.ink, va="top")
ax.text(0,55.5,"vector paths, recolourable; learned once in Fig. 1, reused in every later figure",
        fontsize=PT.subtitle, color=C.ink3, va="top", style="italic")
ax.text(100,59,f"authored at {textwidth():.2f} in = ICLR \\linewidth",
        fontsize=PT.small, color=C.ink3, ha="right", va="top")

meaning = {"wall":"continuous external time; runs whether or not the policy is invoked",
           "step":"countable invocations; the gaps between them carry no time",
           "self":"a sweep that never closes; shape without an anchor"}
for i,k in enumerate(("wall","step","self")):
    cx = 16 + i*34
    axis_glyph(ax, k, cx, 43, 7.5, color=C.ink, lw=1.1)
    ax.text(cx, 35, GLYPH_LABEL[k], fontsize=PT.label, ha="center", color=C.ink)
    ax.text(cx, 31.5, "\n".join(textwrap.wrap(meaning[k], 30)),
            fontsize=PT.small, ha="center", va="top", color=C.ink3, linespacing=1.5)

ax.plot([0,100],[23,23], lw=0.5, color=C.rule)

ax.text(0,20,"Semantic accents", fontsize=PT.subtitle, fontweight="600", color=C.ink, va="top")
ax.text(0,16.8,"used for meaning, never decoration", fontsize=PT.small, color=C.ink3, va="top", style="italic")
for i,(name,col,use) in enumerate([("good",C.good,"threshold met"),("warn",C.warn,"underpowered cell"),
                                   ("bad",C.bad,"failure / reasoning"),("cool",C.cool,"non-reasoning")]):
    y = 12.5 - i*3.6
    ax.add_patch(plt.Rectangle((0,y-1.6),2.6,2.6,color=col))
    ax.text(4, y-0.3, name, fontsize=PT.small, color=C.ink, va="center")
    ax.text(14, y-0.3, use, fontsize=PT.small, color=C.ink3, va="center")

ax.text(52,20,"Type scale", fontsize=PT.subtitle, fontweight="600", color=C.ink, va="top")
ax.text(52,16.8,"literal printed pt (body text = 10 pt)", fontsize=PT.small, color=C.ink3, va="top", style="italic")
for i,(nm,size) in enumerate([("title",PT.title),("label",PT.label),("tick",PT.tick),("small",PT.small)]):
    ax.text(52, 12.0-i*3.6, f"{size} pt  {nm} — Calibration Error", fontsize=size, color=C.ink2, va="center")

fig.savefig("paper1/figures-style/style_proof.png", bbox_inches="tight", pad_inches=0.06, dpi=300)
print("ok")
