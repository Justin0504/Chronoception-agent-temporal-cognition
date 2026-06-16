# Route 2 → 4 bridge — the harness-bracketed elapsed-time tool

**Status: run complete (gpt-4o-mini + o4-mini, n=30 per condition).**
**Branch:** `zijian/paper2-elapsed-tool`.

This experiment closes the causal loop between the tool-interface route (2) and
the architectural route (4). The route-2 run found that a reasoning model calls
`get_current_time()` correctly yet still mis-reports duration. Two explanations
were possible: the agent is unwilling/unable to use the tool, **or** the tool is
structurally blind to hidden-reasoning time. This experiment distinguishes them.

## Design

Three conditions on the standard T3.1 prompt:
- `no_tool` — baseline (Paper 1).
- `clock_tool` — `get_current_time()`; the agent must call it twice and subtract
  (the naive route-2 tool).
- `elapsed_tool` — `get_elapsed_time()`, whose value the **harness** computes as
  `now − t0` (t0 = invocation start), bracketing the entire wall-clock including
  hidden reasoning. One call suffices.

If the route-2 failure were the agent's fault, neither tool would help reasoning
models. If it were the tool's *visibility*, only `elapsed_tool` would.

## Results

| Model | Condition | tool used | median \|ρ\| | grounded (\|ρ\|<0.3) |
|---|---|---|---|---|
| gpt-4o-mini | no_tool | 0% | 1.09 | 0% |
| gpt-4o-mini | clock_tool | 100% | 0.20 | 62% |
| gpt-4o-mini | elapsed_tool | 100% | 0.13 | 67% |
| o4-mini | no_tool | 0% | 1.18 | 4% |
| o4-mini | **clock_tool** | 83% | **0.81** | **0%** |
| o4-mini | **elapsed_tool** | 100% | **0.17** | **86%** |

## What it shows

**The route-2 failure was the tool's visibility, not the agent.** For the
reasoning model o4-mini, the naive clock tool leaves |ρ| at 0.81 and grounds 0%
of trajectories (the Hidden-Time signature, Paper 1 Thm 2). Swapping in a tool
whose value brackets the whole invocation collapses |ρ| to 0.17 and grounds
**86%** — same agent, same task, the only change is that the timing signal now
includes the hidden-reasoning time. The agent was willing all along; the clock
just couldn't see where its wall-clock went.

**For a non-reasoning model the two tools are equivalent** (gpt-4o-mini: 0.20 vs
0.13), exactly as predicted — with no hidden reasoning, the visible-stream clock
already captures the wall-clock, so there is nothing for bracketing to recover.

This is the cleanest single result in the ChronoStack programme so far: a
controlled, model-class-stratified demonstration that **the fix for reasoning-
model chronoception is to bracket the entire invocation**, and that this is a
property of the *timing signal*, not the agent. It validates route 4's premise
empirically with a cheap tool proxy: the architectural primitive
(`chronoception/stack/time_channel.py`) builds exactly this bracketing in
natively, so it should ground reasoning models where a pulled clock cannot.

## Files

- `scripts/run_elapsed_tool.py` — three-condition runner (no_tool / clock / elapsed)
- `scripts/analyze_elapsed_tool.py` — |ρ| per condition + fix verdict
- `tests/test_elapsed_tool.py` — unit tests
- data: `elapsed-tool-results/{gpt-4o-mini,o4-mini}/` (+ `summary.csv`)
