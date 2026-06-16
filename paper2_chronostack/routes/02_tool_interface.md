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

## Results

_(populated when the full gpt-4o-mini + o4-mini run completes)._

A 2-instance smoke check already shows the mechanism working: `no_tool` reports
45 s for a ~3 s task (|ρ| ≈ 1.1, the Paper 1 failure); under `tool`, gpt-4o-mini
spontaneously called `get_current_time()` twice and reported the measured span
(τ_self ≈ the gap between its two calls), i.e. near-grounded — without being told
to. The full run tests whether that holds at n=30 and on a reasoning model.
