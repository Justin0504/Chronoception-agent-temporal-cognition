# Brief: conceptual figures for the Augustine Problem preprint

You are designing **conceptual/architecture figures** for an academic preprint.
Data plots are already scripted from the trajectory corpus and are not in scope
— see *Division of labour* below.

---

## 1. What the paper argues, in one paragraph

LLM agents are trained on tokens and deployed in wall-clock time. Under any
loss that is a functional of token sequences, the gradient is invariant to how
long the episode took, so no amount of scale, context, or reasoning compute can
install a representation of elapsed time — **chronoception must be installed
from outside the loss**. The paper names the failure (*the Augustine Problem*),
decomposes it along three times an agent must keep aligned, measures it across
14 agents from 7 vendors, audits the workaround industry has converged on, and
turns it into a deployment bound.

**Why the paper is positioned this way.** The field has converged on *duration*
as the variable governing agent reliability — reliability frameworks for agents
substitute task duration for time and non-completion for failure; long-horizon
surveys report binary outcomes losing information as horizons grow, pushing
evaluation toward process-level signals inside the trajectory; cost attribution
over trajectories is its own subfield. Each of those programmes presupposes an
instrument the policy does not have. A figure that lands this — duration being
treated as the reliability variable by a field whose agents cannot measure it —
is doing the paper's most important work.

The three times are the framework's fundamental objects:

| | symbol | what it is |
|---|---|---|
| wall | τ_wall | external clock, continuous, runs whether or not the policy is invoked |
| step | τ_step | policy invocations, discrete, the gaps between them carry no time |
| self | τ_self | the agent's own narration of how long it took |

Grounded chronoception is `τ_wall ≈ τ_step·⟨Δt⟩ ≈ τ_self`. The Augustine
Problem is joint drift across all three.

---

## 2. Division of labour

**Not yours — already built, scripted, regenerated from data:**

| figure | what it shows |
|---|---|
| `epsilon_panel` | ε leaderboard, 13 scored agents |
| `calibration_catastrophe` | coverage of nominally-90% CIs |
| `reverse_scaling` | four confirmations of the Reverse-Scaling theorem |
| `p12_hcast` | horizon-decay evidence on METR HCAST |
| `a1_positive_control` | LoRA fine-tune crossing the threshold |
| `e11_headroom` | budget response and the headroom law (E11: 6 questions x 5 deadlines x 2 framings, 7 configurations, 2310 trajectories) |

These read their numbers from CSVs at render time. Do not redraw them; if one
looks wrong, say so and I will fix the generator.

**Yours — conceptual figures.** Two exist and can be replaced if you can do
better (`three_times`, `agentic_frontier`); four concepts have no figure at all
and are the real opportunity. Section 5 lists all six, ranked.

---

## 3. The visual system you must match

`scripts/chronofig.py` is the source of truth. Match it; don't invent a parallel
one.

**Palette** — semantic, never decorative:

```
ink       #1a1a1a   primary text, axis labels
ink2      #4a4a4a   secondary text, tick labels
ink3      #7a7a7a   captions, de-emphasised annotation
rule      #d8d8d8   hairlines, row separators, grid
rule_strong #9a9a9a spines, header underline
surface   #f4f4f4   bar troughs, empty track
good      #2a7a2a   threshold met, grounded reference
warn      #b8860b   marginal / underpowered
bad       #a50f15   failure, reasoning-mode degradation
cool      #3182bd   non-reasoning class
schematic #7a7a7a   anything not measured
```

**Type scale** — these are *literal printed point sizes*, not canvas units:

```
title 9.5   subtitle 7.5   label 8.0   tick 7.0   annot 7.0   small 6.5
MIN 6.0  ← hard floor. Below this, cut content rather than shrink type.
```

**The Three Times glyph set** already exists as vector paths in
`chronofig.axis_glyph()`. If a figure refers to the three axes, reuse these
rather than inventing marks — the reader learns them in Figure 1:

- **τ_wall** — an unbroken ring with a radius hand. Continuous external time.
- **τ_step** — three discrete squares with gaps. Countable invocations; the
  gaps carry no time.
- **τ_self** — a sweep that never closes, with a terminal dot. Shape without an
  anchor.

Run `python3 scripts/make_style_proof.py` to see palette, type scale, and
glyphs rendered together at true print size.

---

## 4. Hard constraints

1. **Author at print size.** Final width is **5.50 in** (the ICLR text column;
   the arXiv build is 6.50 in and simply leaves less margin). A figure drawn at
   12 in and scaled down prints its 10 pt type at 4.4 pt. Every figure in this
   paper was rebuilt to fix exactly that — do not reintroduce it.
2. **Vector PDF.** Fonts embedded as TrueType (`pdf.fonttype = 42`). No raster
   except the vendor logos, which are existing PNG assets in `figures/logos/`.
3. **A single-line subtitle will silently undo the size work.** Tight bounding
   boxes expand the canvas to fit the longest line, and the figure then shrinks
   on inclusion. Wrap subtitles to ≤ 3 short lines and anchor them `va="top"`
   in inches from the top edge, not at a figure fraction.
4. **Academic register.** This was rejected once already: an earlier
   "theorem arc" figure used a spray of decorative icons and the author's
   verdict was *"many of the icons are irrelevant — I need a more academic
   style."* Icons earn their place only by encoding information. Vendor logos
   qualify (identity). The Three Times glyphs qualify (they are the ontology).
   A lightbulb next to the word "insight" does not.
5. **No claim the data does not support.** If a figure is schematic, it must say
   so on its face. `agentic_frontier` carries the word SCHEMATIC and four lines
   explaining that ε_ST is unmeasured and the constant is a normalisation —
   because without that it read as measured data and overclaimed.

---

## 5. Candidate figures, ranked

### (a) The narrative/action split — **highest value, no figure exists**

The paper's central conceptual claim, currently carried only by prose. Across
five frontier generations the *narrative* axis improves 94% (|ρ| +1.12 → +0.07)
while the *action* axis does not move at all (median CAR stays in 0.004–0.050).
Capability scaling reaches what the agent **says** about time and never reaches
what it **does** with time.

Must show: two axes, one with a steep improvement trend across generations, one
flat; and that injection (a prompt-level intervention) moves the first and not
the second (|ΔCAR| ≤ 0.01). The reader should leave understanding *why* a fix
that works on one axis cannot work on the other.

Must not: imply the action axis is noisy or under-measured. It is measured
precisely and it is flat.

### (b) The Injection Tell mechanism — **no figure, currently a 3-row table**

Closed labs route wall-clock into the token stream by three mechanisms: **M1**
system-prompt insertion, **M2** tool calls, **M3** browser side effects. The
harness perceives time on the model's behalf. The tell: 3/3 consumer web-chat
products inject the current date; 0/3 developer tools do. Three labs converged
on this independently.

Must show: the boundary between harness and policy, with the wall-clock
crossing that boundary as *tokens* rather than as a representation — and that
the same model behaves differently on two sides of the same vendor's product
line (Claude.ai injects; the raw API refuses and discloses its training
cutoff).

Must not: depict the model as "knowing" the time after injection. The whole
point is that the harness knows and the model reads.

Supporting evidence you may want on the face of it: tau_self correlates +0.477
with the length of the model's own visible output and only +0.356 with
wall-clock; among reasoning-mode agents, where hidden chain-of-thought
separates the two, the clock correlation collapses to +0.086 while output holds
at +0.450. The self-report is a readout of how much the model wrote.

### (c) Orchestration does not route around it — **no figure, new claim**

The field's response to horizon limits is to scale out; coordination papers
outnumber single-agent work by orders of magnitude. The paper's answer: a
supervisor apportioning deadlines across sub-agents is apportioning a resource
none of them can perceive, and aggregating progress reports none of them can
ground. There is no model to route to — CAR << 1 on all fourteen
configurations from seven vendors.

Must show: that the blind spot is *multiplied* rather than diluted by
distribution. The supervisor is as blind as the workers, and it is now also
making allocation decisions on their reports.

Must not: suggest the workers are individually broken and a better one exists.
The panel is the point — every configuration, every vendor.

### (d) ChronoBench's design — **no figure, currently a 9-row table**

9 sub-capabilities on 3 axes (T1.1–T1.3 wall, T2.1–T2.3 step, T3.1–T3.3 self).
Design philosophy is single-axis isolation: every instance loads on exactly one
of the three times, so a failure is unambiguously attributable.

Must show: the isolation property. This is what makes the benchmark diagnostic
rather than aggregate. Reuse the glyph set for the three axes.

Lower priority than (a)–(c) — the table is already adequate; a figure would
be an upgrade, not a repair.

### (e) `three_times` — exists, replaceable

Currently Figure 1: three horizontal tracks (continuous bar, discrete blocks,
narration bar) with the grounded-chronoception identity above and the three law
labels. It is serviceable. Replace only if you can make the *drift* between the
three tracks more legible — that drift is the Augustine Problem itself and the
current figure states it rather than showing it.

### (f) `agentic_frontier` — exists, replaceable, read the caveats first

A log-log (T, S) plane with constant-ε_ST level sets and five benchmarks
plotted. **Everything on it is schematic**: ε_ST has never been measured, the
benchmark coordinates are order-of-magnitude readings of a qualitative table,
and the constant C is a normalisation chosen so one level set is centred on the
cluster. If you redraw it, those four facts must survive on the figure face.

---

## 6. How to hand back

- One file per figure. **PDF preferred**; SVG accepted (I will convert and
  check that text stays selectable). A `.py` that regenerates it is better
  still — every other figure in this paper is reproducible from source, and a
  one-off asset is the thing that goes stale.
- Drop into `paper1/figures-incoming/`. Tell me which paper section each
  belongs in and the one-sentence claim it is making.
- I will write the caption, wire the `\includegraphics`, rebuild all three
  documents, and check the page budget — the ICLR main text is at **9/9 pages**
  with zero slack, so a figure landing there displaces something and we decide
  together what.
- Render at 5.50 in and look at it at 100%. If any type is below 6 pt or any
  label collides, it comes back.

---

## 7. Context you may want

- `paper1/arxiv-v0/main.pdf` — the current preprint, 44 pages, two authors
- `scripts/chronofig.py` — the style module, with the reasoning in its docstring
- `paper1/figures-style/style_proof.png` — palette, type scale, glyphs
- `paper1/arxiv-v0/sections/` — the prose each figure would sit beside

Two standing rules from the work so far, which apply to figures as much as to
analysis. **State what is measured and what is assumed, on the face of the
artifact.** And **a claim that does not survive its first test outside its
original setting gets reported as exactly that**, not averaged away.
