# Route 4 — Architectural primitive

**Status: interface + feature encoder implemented; training experiment
pre-registered (needs GPU).**
**Branch:** `zijian/paper2-architectural`.

## The idea

Make wall-clock a **first-class input** the policy consumes natively — a
dedicated time channel delivered every invocation — rather than text it must
parse (scaffolding, route 3) or a tool it must remember to fetch (tool interface,
route 2). A model trained under this route attends to a per-step **time feature
vector**; the harness fills the channel from its own clock.

## Why routes 1–3 are not enough (grounded in this project's own results)

- **Route 2 fails on reasoning models.** Our tool-interface run shows o4-mini
  calls `get_current_time()` correctly in 100% of trajectories and faithfully
  reports the measured span, yet |ρ| stays 0.86 — because the tool only
  timestamps the *visible* action stream while ~7× of the wall-clock is spent in
  hidden reasoning the tool cannot see (the Hidden-Time signature, Paper 1
  Thm 2). A pulled tool reading is structurally blind to hidden-reasoning time.
- **Route 3 leaves an action-axis residue.** Live scaffolding eliminates deadline
  overruns but a reasoning model still under-uses large budgets regardless of the
  clock (o4-mini CAR≈0.29 at B=120 s, with or without the scaffold).
- **Route 1 needs retraining anyway** and supervises the *narrative* axis.

The architectural channel is anchored to the harness clock around the **entire**
model invocation, so it captures hidden-reasoning time by construction — exactly
route 2's blind spot — and, being a learned input, can in principle drive the
action axis that prompt-level information (Paper 1 §5/§7) cannot.

## The interface (implemented)

`chronoception/stack/time_channel.py` defines the channel:

- `TimeChannel(t0_epoch, budget_s=None)` — one per trajectory; `observe(epoch,
  step_index)` once per invocation.
- `TimeObservation.feature_vector()` — the float input a trained policy attends
  to: `(elapsed_s, delta_s, step_index, remaining_frac)` (versioned by
  `FEATURE_SCHEMA_VERSION`; "no budget" encoded as `remaining_frac = -1.0`).
- `TimeObservation.render()` — a machine-readable textual fallback
  (`<time elapsed=… step=… budget=… remaining=… [OVER_BUDGET]>`) for handing the
  *same* features to an untrained model in ablations.

Both paths derive from one `TimeObservation`, so the trained-model input and the
text fallback cannot drift apart. Unit tests: `tests/test_time_channel.py`.

## Minimal trainable implementation (the route's actual work — needs GPU)

This is where route 4 differs from 2 and 3: there is **no training-free empirical
MVP**, because the primitive *is* an architectural/training change. The minimal
implementation reuses route 1's A.1 LoRA harness on the lab cluster:

1. Project `feature_vector()` (4 dims) through a small learned MLP into the
   model's embedding dimension; prepend the resulting "time token(s)" to the
   input embeddings at each step (an additive time embedding, analogous to a
   positional encoding but carrying wall-clock).
2. LoRA-fine-tune (start from the A.1 recipe: Qwen2.5-1.5B/7B, rank 16) on
   ChronoBench trajectories where the loss has wall-clock support, so the model
   learns to attend to the time token.
3. Freeze everything else; the only new parameters are the MLP + LoRA adapters.

## Pre-registered experiment (E-ARCH)

- **Train** the time-token model as above on T1.x/T2.x/T3.x trajectories.
- **Primary endpoint**: ε on held-out ChronoBench vs three baselines — the
  untrained model (Paper 1), the route-3 scaffolded model, and the route-2
  tool model — on the *same* instances.
- **Hidden-time test**: on a reasoning-style trace, check that the channel's
  `elapsed_s` tracks true wall-clock including hidden reasoning (the metric route
  2 fails), and that |ρ| no longer shows the Hidden-Time sign flip.
- **Falsification**: if ε does not drop below the route-3 scaffolded baseline,
  the architectural primitive buys nothing over pushing text — report it.
- **Cost**: ~1 GPU-day on the lab cluster (8× RTX 6000 Ada), plus the A.1 venv.
  Requires Justin's approval (server + spend).

## Honest scope

Routes 2 and 3 had cheap, training-free MVPs and were run here. Route 4 does not:
its essence is a learned input modality. The deliverable on this branch is the
**interface + feature encoder + a pre-registered training experiment** — the
concrete spec a GPU run would execute — not a fabricated empirical result.

## Files

- `chronoception/stack/time_channel.py` — the time-channel interface + encoder
- `tests/test_time_channel.py` — unit tests (elapsed/delta, budget, sentinel, render)
- this design doc
