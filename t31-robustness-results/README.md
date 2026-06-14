# T3.1 paraphrase robustness

**Status: scaffolded and locally validated; awaiting an API (or vLLM) run.**
**Branch:** `zijian/t31-paraphrase-robustness`.

A reviewer-anticipated control for Paper 1 §6.1. The retrospective confabulation
result (median `rho` on T3.1) is currently measured with one fixed prompt
template. The obvious objection: *is the finding an artifact of that exact
wording?* This experiment answers it directly.

## Design

Run T3.1 under five semantically-equivalent paraphrases of the instruction,
holding the sub-task content **fixed** across variants (same seed → same
sub-tasks in the same order), so the only thing that changes between variants is
the wording of "complete the task, then report how long it took, in seconds."

| Variant | Changes |
|---|---|
| `v0_original` | the exact wording used to build the committed dataset |
| `v1_casual` | casual register, "roughly how many seconds" |
| `v2_formal` | formal register, "precise number of seconds" |
| `v3_question_first` | task first, duration asked as a trailing question |
| `v4_imperative` | terse imperative, "report the elapsed time" |

Everything else — `tau_self` parsing, Setting A/B injection, trajectory IO — is
the standard pipeline (the script reuses `run_pilot`'s backend factory and IO),
so results are directly comparable to the committed dataset. The frozen
generators in `chronoception/bench/tasks/instances.py` are **not** modified;
`run_t31_paraphrase_robustness.py::_matched_sub_tasks` reproduces their seeded
sub-task selection (pinned by a unit test).

## Two robustness measures

1. **Within-agent stability.** For each agent, the spread (max − min) of median
   `|rho|` across the five paraphrases. The finding is not a wording artifact if
   that spread is small relative to the Augustine threshold (ε\* = 0.20) — and
   tiny relative to the paper's cross-generation effect (median `|rho|` 1.12 →
   0.07, a range of ~1.05). Verdict: `ROBUST` / `MOSTLY ROBUST` / `NOT ROBUST`.

2. **Cross-agent rank stability** (when ≥ 2 agents are run). For each pair of
   paraphrases, the Spearman rank correlation of the agents' `|rho|` ordering. A
   high mean correlation means the paper's panel ranking survives rewording.
   Spearman is computed with the standard library only (no scipy dependency).

## How to run

```bash
# Cheap single model on the OpenAI API (gpt-4o-mini keeps cost to a few $)
OPENAI_API_KEY=sk-... python scripts/run_t31_paraphrase_robustness.py \
    --backend openai --model gpt-4o-mini \
    --setting no_injection,with_injection --count 30 \
    --output-dir t31-robustness-results

# Free alternative: a self-hosted model via vLLM
python scripts/run_t31_paraphrase_robustness.py \
    --backend openai --base-url http://127.0.0.1:8001/v1 \
    --model qwen2.5-7b --agent-id-override oss/qwen2.5-7b \
    --count 30 --output-dir t31-robustness-results

# Analyze (re-runnable without re-querying)
python scripts/analyze_t31_paraphrase.py --input-dir t31-robustness-results \
    --setting no_injection --output-csv t31-robustness-results/metrics.csv
```

Cost: 5 variants × 30 instances × 2 settings = 300 calls per agent. On
gpt-4o-mini that is a few US dollars; on a self-hosted model it is free.
**Keep total API spend ≤ $20** (HANDOFF requires Justin's approval above that),
or run it on the lab Qwen for free.

To strengthen the cross-agent rank-stability claim, run more than one agent
(each into the same `--output-dir`); the analyzer enables the Spearman path
automatically once ≥ 2 agents are present.

## What goes into the paper

A `ROBUST` within-agent verdict (small spread) plus high cross-agent Spearman is
a one-paragraph appendix (`paper1/arxiv-v0/sections/G_*.tex`) and a small table
that closes the "prompt-wording artifact" objection before a reviewer raises it.
If the result is *not* robust, that is itself important and should be reported —
the design surfaces it either way.

## Files

- `scripts/run_t31_paraphrase_robustness.py` — the five-variant sweep
- `scripts/analyze_t31_paraphrase.py` — within-agent spread + cross-agent Spearman
- `tests/test_t31_paraphrase.py` — unit tests (sub-task matching, rho, Spearman, verdicts)
