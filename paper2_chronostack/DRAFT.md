# ChronoStack: Installing Chronoception in LLM Agents

**Working draft — Paper 2 of the chronoception programme.**
**Branch:** `zijian/paper2-draft`. Status: skeleton + first results synthesis.
This markdown draft becomes the LaTeX source once the route experiments are
locked; numbers below are from the runs committed under `*-results/` and
`paper2_chronostack/`.

---

## Abstract

Paper 1 (*The Augustine Problem*) proved that LLM agents cannot acquire wall-clock
chronoception from any token-only training loss (the Chronoception Impossibility
Theorem, CIT) and that reasoning-token expansion degrades it (Reverse-Scaling).
If chronoception cannot be *trained in*, it must be *installed*. ChronoStack
enumerates four installation routes — loss extension, tool interface, harness
scaffolding, and an architectural time primitive — and measures, on ChronoBench,
how much of the gap each one closes and where each one fails. We find that
chronoception is installable, but that **the install must reach where the agent's
wall-clock actually is**, and this differs by axis and by model class. A
wall-clock-supported loss (route 1) and a clock tool (route 2) close the
narrative axis (self-reported duration, |ρ|) for non-reasoning models — a clock
tool drops median |ρ| from 1.06 to 0.17 and is used spontaneously. But for
reasoning models a pulled clock fails (|ρ| stays 0.81, 0% grounded) because it
times only the visible action stream while the wall-clock is dominated by hidden
reasoning — the Hidden-Time signature of Paper 1. The fix is to bracket the
*entire* invocation: a harness-computed elapsed-time signal grounds the same
reasoning model to |ρ|=0.17, 86% grounded. On the action axis, a live
scaffolding clock eliminates deadline overruns across models and a 6× budget
range, where Paper 1 showed static date injection moves nothing. The
architectural primitive builds the bracketing in natively and is pre-registered.
We release all routes, code, trajectories, and a unifying route × axis ×
model-class map.

---

## 1. Introduction — from impossibility to installation

Paper 1 established the negative result: token-only losses carry no wall-clock
gradient (CIT), so additional scale, longer reasoning, and prompt-level date
injection cannot close the chronoception gap. The constructive question follows
immediately: **what *can*?** ChronoStack is the catalogue of answers and the
measurement of each.

The organising claim of this paper: time is installable, but an install only
works if its signal reaches the part of the trajectory where the agent's
wall-clock is actually spent. Two structural facts from Paper 1 shape every
route: (i) the **narrative axis** (τ_self, |ρ|) is text-trainable while the
**action axis** (τ_step/τ_wall, CAR) is not; (ii) for **reasoning models** the
wall-clock hides inside chain-of-thought the surface stream cannot see.

## 2. The four routes

| Route | Mechanism | Targets | Needs training? |
|---|---|---|---|
| 1 Loss extension | wall-clock-supported SFT/RL | narrative axis | yes |
| 2 Tool interface | a clock tool the agent pulls | narrative axis | no (policy already knows when, sometimes) |
| 3 Scaffolding | a live clock the harness pushes each step | action axis | no |
| 4 Architectural primitive | wall-clock as a native learned input | both, incl. hidden time | yes |

## 3. Results

### 3.1 Route 1 — loss extension (A.1 toy positive control)

Wall-clock-supported LoRA SFT on T3.1. Qwen2.5-1.5B: median |ρ| 1.37 → 0.30
(crosses the Augustine threshold ε*=0.20 on T3.1 score, 0.69 → 0.15);
Qwen2.5-7B: 0.93 → 0.51 (partial). Demonstrates CIT's converse: putting
wall-clock in the loss support installs narrative-axis chronoception. Cost: GPU.
(`paper2_chronostack/toy_a1/`.)

### 3.2 Route 2 — tool interface (`get_current_time`), and its reasoning-model failure

Three conditions on T3.1 (no_tool / tool / tool_prompted), n=30.

| Model | no_tool \|ρ\| | tool \|ρ\| | used ≥2× |
|---|---|---|---|
| gpt-4o-mini | 1.06 | **0.17** | 97% (spontaneous) |
| o4-mini | 1.37 | **0.86** | 100% |

A clock tool grounds the **non-reasoning** model and is adopted *without
instruction* (the bare `tool` and `tool_prompted` conditions are
indistinguishable). The **reasoning** model calls the clock twice in 100% of
trajectories and faithfully reports the measured span — yet |ρ| stays 0.86,
because the span (2–7 s) is ~7× smaller than the true wall-clock (8–23 s): the
reasoning happens in hidden tokens *outside* the window between the two visible
calls. The agent uses the tool perfectly and is still wrong. (Route 2 docs +
`tool-interface-results/`.)

### 3.3 Route 2 → 4 bridge — bracket the whole invocation

The diagnosis above predicts a fix: compute elapsed time in the **harness**, from
the invocation start, so it includes hidden reasoning. Same T3.1, adding a
`get_elapsed_time()` whose value the harness returns.

| Model | clock_tool \|ρ\| (grounded) | elapsed_tool \|ρ\| (grounded) |
|---|---|---|
| gpt-4o-mini | 0.20 (62%) | 0.13 (67%) |
| o4-mini | **0.81 (0%)** | **0.17 (86%)** |

Bracketing collapses the reasoning model's error from 0.81 to 0.17 and grounds
86% of trajectories — same agent, same task, only the timing signal changed. For
the non-reasoning model the two tools are equivalent (no hidden time to recover).
**The route-2 failure was the signal's visibility, not the agent's willingness.**
(`elapsed-tool-results/`.)

### 3.4 Route 3 — scaffolding (budget-honoring loop)

A multi-step loop where the agent decides when to stop, given a wall-clock budget
B, with vs without a live `[clock] elapsed/remaining/step` readout. Sweep
B ∈ {20,60,120}s × {gpt-4o-mini, o4-mini}, n=10.

Native (no clock) behaviour is the opposite of the naive L2 expectation:
agents **overrun** deadlines, worsening with budget (gpt-4o-mini: 50/100/80% of
runs over budget at B=20/60/120). The live scaffold drives the overrun rate to
~0 across both models and every budget (gpt-4o-mini 50/100/80% → 0/0/0; o4-mini
100/30/0% → 10/0/0) — the action-axis win static date injection could not buy
(Paper 1 §7). Limits: the scaffold trades overrun for mild under-use (ON median
CAR 0.65–0.83), and a reasoning model under-uses large budgets regardless
(o4-mini CAR≈0.29 at B=120 either way). (`scaffolding-sweep/`.)

### 3.5 Route 4 — architectural primitive

Wall-clock as a native learned input. Interface + feature encoder implemented
(`chronoception/stack/time_channel.py`): per-step features
`(elapsed_s, delta_s, step_index, remaining_frac)` anchored to the harness clock
around the entire invocation — covering exactly the hidden-time blind spot route 2
hits. No training-free empirical MVP; experiment E-ARCH (LoRA time-token on the
A.1 harness, ε vs routes 2/3 baselines) is pre-registered. Needs GPU.

## 4. Synthesis — route × axis × model class

| | narrative axis (\|ρ\|) | action axis (CAR / overrun) |
|---|---|---|
| **non-reasoning** | route 1 (train) ✓; route 2 clock ✓ (spontaneous) | route 3 scaffold ✓ (overruns → 0) |
| **reasoning** | route 2 clock ✗ (Hidden-Time) → **bracketed elapsed ✓** / route 4 | route 3 scaffold ✓ overruns; under-use residue |

Three regularities:
1. **Installable, but axis-specific.** The narrative axis yields to loss or tool;
   the action axis yields to a live pushed clock, not to information alone.
2. **Reasoning models need the signal to bracket hidden time.** A pulled clock
   sees only the surface stream and fails (Hidden-Time); a harness/architectural
   signal that brackets the whole invocation succeeds (0.81 → 0.17).
3. **Push beats pull for the action axis.** Scaffolding (push) eliminates
   overruns where the tool (pull) and static injection do not act.

## 5. Limitations & honest negatives

- Routes 1 and 4 require training/GPU; route 4 has no empirical result yet
  (interface + pre-registration only).
- Scaffolding's median-CAR effect is null at budgets near the natural landing
  point; the real signal is dispersion/overrun (pre-registered as primary in the
  sweep). Reasoning-model under-use at large budgets is unsolved by scaffolding.
- Tool/bridge use a local duration-parse fallback for the "Task duration: X s"
  phrasing; the canonical parser is tried first for comparability.
- Single seed, modest n per cell; provider-side tool/temperature behaviour may
  shift across model versions.

## 6. Conclusion

Chronoception can be installed, and which route works is predicted by *which axis*
and *which model class* you target. The programme's sharpest result is the
reasoning-model fix: the failure of a clock tool is not the agent's — it is the
signal's blindness to hidden reasoning, and bracketing the whole invocation
repairs it. That principle, proven here with a cheap tool proxy, is what the
architectural primitive (route 4) is designed to make native.

---

## Appendix — reproduction

| Route | Code | Data |
|---|---|---|
| 1 | `paper2_chronostack/toy_a1/` | `toy_a1/a1_summary.json` |
| 2 | `scripts/run_tool_interface.py`, `analyze_tool_interface.py` | `tool-interface-results/` |
| 2→4 | `scripts/run_elapsed_tool.py`, `analyze_elapsed_tool.py` | `elapsed-tool-results/` |
| 3 | `scripts/run_scaffolding_budget.py`, `analyze_scaffolding.py` | `scaffolding-sweep/` |
| 4 | `chronoception/stack/time_channel.py` | (pre-registered E-ARCH) |

Each route's design doc and per-route result tables: `paper2_chronostack/routes/`.
