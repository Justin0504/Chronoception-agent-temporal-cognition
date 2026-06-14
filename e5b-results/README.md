# E5b — OSS Reverse-Scaling via reasoning-intensity induction

**Status: scaffolded and locally validated; awaiting a GPU run on the lab cluster.**
**Branch:** `zijian/e5b-reasoning-induction`.

This experiment closes the one open gap in the empirical case for the
Reverse-Scaling Theorem (Paper 1 Theorem 2): a *third, open-source, reproducible*
confirmation. Theorem 2 is currently confirmed twice — intra-model on o4-mini
(E2) and cross-model on Sonnet 4.6 ± thinking (E3). The intended open-source
third confirmation (E5) did not deliver one, for a reason that is itself a
finding. E5b fixes the experimental design that caused E5 to come up empty.

## Why E5 came up empty

E5 (`scripts/run_e5_oss_reverse_scaling.sh`) varied reasoning compute on
DeepSeek-R1-Distill-Qwen-14B by sweeping `--max-output-tokens` over
{1024, 4096, 14000}. The model terminated naturally (`finish_reason=stop`) at
~18 s wall-clock at **every** budget — it never approached the cap — so the
reasoning compute it actually spent did not change. `|rho|` stayed flat at
0.531–0.537 across all three levels (`../e5-results/metrics.csv`). Paper 1 §6.2
reports this honestly: *"budget-permitted reasoning is not budget-honoured
reasoning,"* and notes the correct route is *"a native reasoning-budget
interface or system-prompt induction of reasoning intensity."*

A token **cap** is a permit, not a forcing function. To test Theorem 2 you must
make the model actually spend more reasoning compute, then check `|rho|`.

## What E5b does differently

1. **The manipulation is the system prompt, not the token cap.** Three monotone
   reasoning-intensity levels are induced through the base system prompt
   (`brief` / `natural` / `thorough`), the route Paper 1 §6.2 names as correct.
   The token cap is held **fixed and generous (14 000)** at every level so it is
   never the binding constraint — the only thing that changes is how much the
   model is told to deliberate. (Enabled by a new `--system-prompt` flag on
   `run_pilot.py`.)

2. **Reasoning compute is measured, not assumed.** The analyzer reports median
   completion tokens (R1-Distill's chain-of-thought is in-band, so completion
   tokens count it) and median `tau_wall` per level. It **refuses to report a
   rho trend unless reasoning compute is monotonically increasing** across the
   three levels. This validity gate is exactly what E5 lacked; if the
   manipulation fails (flat tokens, the E5 case), the analyzer says
   `MANIPULATION FAILED` rather than reporting a spurious null.

3. **`tau_self` is parsed from the surface answer only.** R1-Distill emits its
   reasoning inline, terminated by `</think>`, then the final answer. The
   analyzer splits on `</think>` and parses the self-reported duration from the
   answer alone. This is required by the theorem's mechanism: `tau_self` anchors
   to the surface output while `tau_wall` absorbs the hidden thinking, which is
   why `rho`'s sign flips negative for reasoning models. (The original inline
   parser ran on the full output, including the chain-of-thought.)

## How to run (lab cluster)

Requires the same setup as E5 — vLLM serving DeepSeek-R1-Distill-Qwen-14B on
`localhost:8001` via `scripts/deploy_oss_reasoning.sh` + SSH port-forward. Server
credentials are not in the repo (ask Justin / Yue Zhao).

```bash
# 1. Deploy the model on the lab server (8x RTX 6000 Ada)
./scripts/deploy_oss_reasoning.sh

# 2. Port-forward and run the three-level sweep + analysis
ssh -L 8001:127.0.0.1:8001 haiyuez@10.136.20.188
./scripts/run_e5b_reasoning_induction.sh
```

Output: `e5b-results/deepseek-r1-14b-{brief,natural,thorough}/` (30 instances ×
2 settings × 3 levels = 180 trajectories), plus `e5b-results/metrics.csv`.
Re-run the analysis at any time without re-querying the model:

```bash
python scripts/analyze_e5b.py --input-dir e5b-results \
    --output-csv e5b-results/metrics.csv --output-json e5b-results/summary.json
```

## What counts as a result

The analyzer prints one of three verdicts on the primary (`no_injection`) setting:

| Verdict | Condition | Meaning for the paper |
|---|---|---|
| `REVERSE-SCALING CONFIRMED` | compute ↑ monotone **and** median `\|rho\|` ↑ monotone non-decreasing | The open-source third confirmation Theorem 2 was missing. Goes into §6.2 / a new appendix. |
| `REVERSE-SCALING REFUTED` | compute ↑ monotone **but** median `\|rho\|` ↓ | A genuine open-source counter-example. Reported honestly; strengthens the paper's credibility either way. |
| `MANIPULATION FAILED` | compute not monotone ↑ | The induction did not move reasoning compute (the E5 outcome). Try a model with a native thinking toggle (see below). |

Either of the first two outcomes is publishable; the design is pre-committed so
the result is informative whichever way it lands.

## If induction fails on R1-Distill (fallback)

If `MANIPULATION FAILED` recurs, the cleanest alternative is a model with a
**native thinking toggle** — Qwen3-14B exposes `enable_thinking` (`/think` vs
`/no_think`), which gives a clean on/off contrast mirroring the Sonnet 4.6 ±
thinking result in E3, plus a prompt-induced intensity sweep on top. Deploy
Qwen3-14B in place of R1-Distill in `deploy_oss_reasoning.sh`, pass
`enable_thinking` via `--extra-body`, and point `analyze_e5b.py` at the new dir.

## Files

- `scripts/run_e5b_reasoning_induction.sh` — the three-level sweep
- `scripts/analyze_e5b.py` — validity-gated analyzer
- `scripts/run_pilot.py` — added `--system-prompt` flag (additive; default behavior unchanged)
- `tests/test_analyze_e5b.py` — unit tests for the analyzer's verdict logic
