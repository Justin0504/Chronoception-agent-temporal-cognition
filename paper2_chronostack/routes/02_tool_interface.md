# Route 2 — Tool interface

**Status: MVP scaffolded and locally validated; full run in progress.**
**Branch:** `zijian/paper2-tool-interface`.

## The idea

Give the agent a `get_current_time()` tool and let it **pull** the wall-clock
when it decides it needs to — as opposed to the scaffolding route (route 3),
which **pushes** a clock readout at it every turn. Eventually the route's full
form is a *learned* policy over the tool; the MVP asks the prior question of
whether a frontier agent already knows when to call it.

## The open question it attacks

Paper 1 (CIT) shows the agent has no internal time representation. A tool gives
it *access* to external time. But **access is not use**: does the agent know
*when* to reach for the clock?

To report how long a task took (T3.1), a grounded policy calls
`get_current_time()` before doing the task and again after, then subtracts.
Because a completion is a single generation, the wall-clock between those two
tool calls is the agent's own generation time for the task — the true τ_wall. So
an agent that uses the tool correctly can report an accurate duration (|ρ| → 0).
The MVP measures whether it spontaneously does.

## MVP design (T3.1)

Three conditions on the standard T3.1 prompt ("do the task, then report how long
it took you, in seconds"):

| Condition | Tool offered? | System prompt | Tests |
|---|---|---|---|
| `no_tool` | no | neutral | baseline (reproduces Paper 1's high \|ρ\|) |
| `tool` | yes (`tool_choice=auto`) | neutral | **spontaneous** use |
| `tool_prompted` | yes | "use the tool to time the task" | availability + explicit instruction (upper bound) |

The `tool` vs `tool_prompted` contrast isolates "does the agent know to use the
clock" (the learned-policy gap) from "can the tool ground the report when used".

Primary readouts (`analyze_tool_interface.py`):
- tool-use rates: fraction calling the clock ≥1× and ≥2× (≥2 is the minimum to
  measure a duration);
- |ρ| overall, and **|ρ| split by whether the agent called the clock ≥2×** — the
  direct test of availability-vs-use;
- a per-model diagnosis: `AVAILABILITY != USE` / `TOOL SUFFICES` / `USE INSUFFICIENT`.

The tool-calling loop is implemented directly against the OpenAI API (the shared
backends do not expose tools); the harness executes `get_current_time()` with
real `time.time()` and records every call's timestamp.

## How to run

```bash
OPENAI_API_KEY=sk-... python scripts/run_tool_interface.py \
    --model gpt-4o-mini --count 30 \
    --condition no_tool,tool,tool_prompted \
    --output-dir tool-interface-results

python scripts/analyze_tool_interface.py --input-dir tool-interface-results \
    --output-csv tool-interface-results/summary.csv
```

Run a reasoning model too (e.g. `--model o4-mini`) for the model-class contrast.

## Files

- `scripts/run_tool_interface.py` — three-condition T3.1 runner with the OpenAI tool loop
- `scripts/analyze_tool_interface.py` — use-rates + |ρ| split + diagnosis
- `tests/test_tool_interface.py` — unit tests (condition config, ρ, summary, diagnosis)

## Results (2026-06, gpt-4o-mini + o4-mini, n=30 per condition)

| Model | Condition | used ≥2× | median \|ρ\| | \|ρ\| when used ≥2× |
|---|---|---|---|---|
| gpt-4o-mini | no_tool | 0% | 1.06 | — |
| gpt-4o-mini | tool | **97%** | **0.17** | 0.17 |
| gpt-4o-mini | tool_prompted | 97% | 0.18 | 0.18 |
| o4-mini | no_tool | 0% | 1.37 | — |
| o4-mini | tool | **100%** | **0.86** | 0.86 |
| o4-mini | tool_prompted | 100% | 0.83 | 0.83 |

**The tool grounds a non-reasoning model and is used spontaneously.** gpt-4o-mini
calls `get_current_time()` before and after the task in 97% of trajectories
*without being told to* (the `tool` and `tool_prompted` columns are
indistinguishable), and |ρ| collapses 1.06 → 0.17 — a 6× reduction, where static
date injection moved nothing (Paper 1 §7). For a non-reasoning agent the route
works and needs no instruction.

**The tool FAILS on a reasoning model — and the failure is the Hidden-Time
signature.** o4-mini calls the clock twice in 100% of trajectories and faithfully
reports the span it measured (τ_self = the gap between its two calls, to 1.0×).
Yet |ρ| stays at 0.86, because the **measured span (2–7 s) is ~7× smaller than
the true wall-clock (8–23 s)**: the model's reasoning happens in hidden thinking
tokens *outside* the window between its two visible tool calls, so the clock —
which can only timestamp the visible action stream — under-measures the duration.
The agent uses the tool perfectly and is still wrong.

This is Paper 1's Hidden-Time / Reverse-Scaling mechanism resurfacing one level
up: **the tool-interface route inherits CIT's blind spot for reasoning models.** A
clock tool grounds you only if your wall-clock lives in the part of the stream
the tool can see; for a reasoning model the bulk of it does not. The
`USE INSUFFICIENT` diagnosis fires automatically (≥2 calls, |ρ| still ≥ 0.3).

**Takeaways for the route.**
1. Tool-interface is a cheap, training-free win for non-reasoning agents and
   they adopt it spontaneously — a clean constructive result vs Paper 1's
   baselines.
2. For reasoning agents the tool must be able to see hidden-reasoning time
   (e.g. a harness that brackets the *entire* invocation, or a provider-reported
   reasoning-duration field) — otherwise the route silently under-measures.
   This is the concrete design requirement the MVP surfaces for the route's full
   (learned-policy) form.

Data: `tool-interface-results/{gpt-4o-mini,o4-mini}/` (+ `summary.csv`).
