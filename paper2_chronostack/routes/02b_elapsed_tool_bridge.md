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
Median |ρ| with 95% bootstrap CIs; grounded = |ρ| < 0.3; no-report = fraction
giving no parseable duration; n_ρ = trajectories with a usable duration.

| Model | Condition | n_ρ | no-report | median \|ρ\| (95% CI) | grounded |
|---|---|---|---|---|---|
| gpt-4o-mini | no_tool | 30 | 0% | 1.09 [1.08, 1.13] | 0% |
| gpt-4o-mini | clock_tool | 29 | 0% | 0.20 [0.17, 0.44] | 62% |
| gpt-4o-mini | elapsed_tool | 27 | 10% | 0.13 [0.08, 0.34] | 67% |
| o4-mini | no_tool | 23 | 23% | 1.18 [0.89, 1.75] | 4% |
| o4-mini | **clock_tool** | 29 | 0% | **0.81 [0.71, 0.94]** | **0%** |
| o4-mini | **elapsed_tool** | 29 | 3% | **0.17 [0.11, 0.19]** | **86%** |
| o3 | no_tool | 8 | 73% | 0.69 [0.53, 0.88] | 12% |
| o3 | clock_tool | 18 | 40% | 0.58 [0.49, 0.76] | 11% |
| o3 | elapsed_tool | 2 | 93% | — (n=2) | — |

## What it shows

**The route-2 failure was the tool's visibility, not the agent.** For the
reasoning model o4-mini, the naive clock tool leaves |ρ| at 0.81 [0.71, 0.94] and
grounds 0% of trajectories (the Hidden-Time signature, Paper 1 Thm 2). Swapping in
a tool whose value brackets the whole invocation collapses |ρ| to 0.17 [0.11,
0.19] and grounds **86%** — the two CIs do not overlap. Same agent, same task; the
only change is that the timing signal now includes the hidden-reasoning time.

**For a non-reasoning model the two tools are equivalent** (gpt-4o-mini: 0.20 vs
0.13, overlapping CIs), exactly as predicted — with no hidden reasoning, the
visible-stream clock already captures the wall-clock.

**The Hidden-Time clock failure generalizes to a second reasoning model.** o3's
naive clock tool also fails to ground (|ρ| 0.58 [0.49, 0.76], 11% grounded,
n=18) — so the clock's blindness to hidden reasoning is a property of the
reasoning *class*, not an o4-mini quirk.

**An honest confound on o3's fix, and a new finding.** We cannot confirm the
bracketed fix on o3, because o3 frequently **refuses to disclose its own task
duration** ("I'm sorry, but I can't share precise timing information") — even when
it has called the tool. The no-report rate rises across conditions and is highest
exactly when it is handed a precise elapsed value (no_tool 73% → clock 40% →
elapsed 93%), leaving only n=2 parsed durations in the elapsed cell. The analyzer
flags this cell `INCONCLUSIVE` rather than reporting a number from n=2. This is a
*second*, distinct obstacle for some reasoning models — a self-timing disclosure
guardrail — orthogonal to the Hidden-Time perception problem, and worth its own
treatment (it is an alignment/refusal behavior, not a measurement failure).

Net: the bracketing fix is **decisive on o4-mini** (non-overlapping CIs), the
clock failure it repairs **generalizes across the reasoning class** (o4-mini +
o3), and o3 surfaces a separate disclosure-refusal obstacle. The architectural
primitive (`chronoception/stack/time_channel.py`) builds the bracketing in
natively; it would also sidestep the "remember to call the tool" gap, though not
the disclosure refusal.

## Files

- `scripts/run_elapsed_tool.py` — three-condition runner (no_tool / clock / elapsed)
- `scripts/analyze_elapsed_tool.py` — |ρ| per condition + fix verdict
- `tests/test_elapsed_tool.py` — unit tests
- data: `elapsed-tool-results/{gpt-4o-mini,o4-mini}/` (+ `summary.csv`)
