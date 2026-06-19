# Within-trajectory drift (P8 / P9)

**Status: scaffolded and locally validated; awaiting an API run.**
**Branch:** `zijian/within-trajectory-drift`.

This is the direct measurement Paper 1 §6 says it cannot make. P8 predicts that
for reasoning-tuned agents, the confabulation magnitude `|rho_t|` *grows* with
step `t` along a single trajectory. ChronoBench's single-step protocol cannot
see within-trajectory dynamics, so the paper reports a cross-trajectory proxy
instead — and that proxy ran *against* P8's direction (`|rho|` fell with
`tau_wall`), logged honestly as a negative. The paper defers the real test to a
multi-step harness (E8). This is a minimal version of that harness.

## What it measures

One multi-turn conversation per trajectory instance. At each step the agent
completes a small homogeneous sub-task (drawn from the T3.1 pool, so wall-clock
per step is comparable) and reports how long *that step* took it. Per step:

```
tau_wall_step[t] = wall-clock the step actually took (timestamps)
tau_self_step[t] = the agent's self-reported step duration (parsed)
rho_step[t]      = log10(tau_self_step[t] / tau_wall_step[t])
```

The analyzer fits the OLS slope of `|rho_t|` against `t` per conversation,
aggregates across conversations (median slope + a sign test on direction), and
reports median `|rho|` at each step position as an eye-check.

Why this is the right test: holding sub-task content homogeneous means the only
quantity expected to move `|rho_t|` is *position in the trajectory* — exactly
P8's claim. The cross-trajectory proxy could not separate position from task
difficulty; this can.

## Verdict logic (per agent)

| Verdict | Condition |
|---|---|
| `P8 SUPPORTED` | median slope `> +tol` and a majority of conversations drift up |
| `P8 REFUTED` | median slope `< -tol` and a majority drift down (the cross-trajectory direction, now confirmed within-trajectory) |
| `FLAT/INCONCLUSIVE` | `\|median slope\| <= tol` or no clear majority |

`tol` defaults to 0.02 and is configurable. Either of the first two outcomes is
a real result: `SUPPORTED` rescues P8 from "deferred"; `REFUTED` upgrades the
paper's honest negative from a proxy to a direct measurement.

## How to run

```bash
# Local smoke check (no API) — the fixed backend with a per-call delay so
# tau_wall per step is nonzero
python scripts/run_within_trajectory_drift.py \
    --backend fixed --fixed-response "Done. This step took me 12 seconds." \
    --delay 0.05 --n-conversations 3 --n-steps 5 \
    --output-dir within-trajectory-results

# Real run: a non-reasoning and a reasoning model, to test P8's model-class claim
OPENAI_API_KEY=sk-... python scripts/run_within_trajectory_drift.py \
    --backend openai --model gpt-4o-mini \
    --n-conversations 20 --n-steps 8 --setting no_injection \
    --output-dir within-trajectory-results
OPENAI_API_KEY=sk-... python scripts/run_within_trajectory_drift.py \
    --backend openai --model o4-mini --extra-body '{"reasoning_effort":"high"}' \
    --n-conversations 20 --n-steps 8 --setting no_injection \
    --output-dir within-trajectory-results

# Analyze (per agent)
python scripts/analyze_within_trajectory.py --input-dir within-trajectory-results \
    --setting no_injection --output-csv within-trajectory-results/slopes.csv
```

Cost note: 20 conversations × 8 steps = 160 calls per agent (a multi-turn
conversation re-sends the growing context each step, so token cost grows with
step count). On gpt-4o-mini this is a few dollars; **keep total spend ≤ $20**
(HANDOFF requires Justin's approval above that), or run on the lab Qwen.

P8 is specifically about *reasoning-tuned* agents, so the informative comparison
is a reasoning model vs a non-reasoning one — run at least one of each.

## Pilot results (2026-06, gpt-4o-mini vs o4-mini, n=20 conversations × 8 steps)

A first run on one non-reasoning and one reasoning model, `no_injection`:

| Agent | median slope | up/down | sign-test p | verdict |
|---|---|---|---|---|
| gpt-4o-mini (non-reasoning) | +0.0024 | 12/8 | 0.50 | FLAT/INCONCLUSIVE |
| o4-mini (reasoning, effort=high) | +0.0053 | 12/8 | 0.50 | FLAT/INCONCLUSIVE |

**P8 is not supported within-trajectory for either model class.** `|rho_t|` shows
no trend across steps (gpt-4o-mini ~0.83→0.88, o4-mini ~0.18→0.21; both flat).
This is the direct within-trajectory measurement the paper could only proxy
across trajectories — and it agrees with the paper's honest negative: drift does
not grow along a single trajectory. Reporting it upgrades §6's deferred P8 from
a cross-trajectory proxy to a direct null.

Two side-findings worth noting:
- **Per-step confabulation is real and opposite in sign by model class.**
  gpt-4o-mini over-reports (self 10–25 s vs ~2 s actual, rho ≈ +0.9); o4-mini is
  near-grounded most of the time (self 2–7 s vs ~3 s actual) but **bimodal** —
  some conversations reproduce the paper's "0.04 seconds" Hidden-Time
  under-report verbatim. The median `|rho|` ≈ 0.17 masks this bimodality.
- **The drift conclusion is robust to the prompt's format example.** The pilot
  prompt included a concrete "12 seconds" example; the data show neither model
  pinned to it (gpt-4o-mini reported 10–25 s, o4-mini 2–7 s or 0.04 s), and
  because the example was identical at every step it cannot create a *trend*. The
  prompt has since been changed to an "N seconds" placeholder for cleaner
  absolute levels; the flat-drift result does not depend on the change.

Caveat: absolute `|rho|` levels here are not comparable to the paper's
single-step T3.1 numbers (different protocol — short per-step tasks, multi-turn
context). The within-trajectory *trend* is the measurement this harness is for.

## Scope and honesty

This is a *minimal* harness: each step is an independent small task within one
conversation, not a single decomposed long-horizon task. It measures whether
self-duration calibration degrades as the conversation lengthens, which is the
cleanest within-trajectory signal obtainable without a full agentic loop. A
SWE-Bench-style decomposed-task harness (the full E8) remains Paper 3 work; this
de-risks it and gives a first data point. Whatever the slope sign, it should be
reported — the design surfaces it either way.

## Files

- `scripts/run_within_trajectory_drift.py` — multi-turn harness
- `scripts/analyze_within_trajectory.py` — per-conversation slope + sign test
- `tests/test_within_trajectory.py` — unit tests (OLS, sign test, verdicts)
