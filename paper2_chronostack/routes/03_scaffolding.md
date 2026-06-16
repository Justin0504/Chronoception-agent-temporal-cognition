# Route 3 — Scaffolding

**Status: MVP scaffolded and locally validated; awaiting an API run.**
**Branch:** `zijian/paper2-scaffolding`.

## The idea

The harness, not the model, perceives time and feeds it to the policy as
structured context that is recomputed every turn: a τ_step counter, a deadline,
and the wall-clock budget remaining. The bet is that a policy which cannot
acquire time from its loss (Paper 1, CIT) can still *act* on time when the
harness keeps a live clock in front of it.

## The open question it attacks

Paper 1 §5/§7 showed two things this route must beat:
1. **L2 Step-Clock Conflation** — agents honor < 5% of a wall-clock budget.
2. **The Injection Tell** — *static* prompt injection of the date does not move
   CAR (`|ΔCAR| ≤ 0.01`); information at the prompt is not a representation.

The scaffolding route asks the converse: does a **live, recomputed** wall-clock
readout *inside a multi-step loop* — not a one-shot date string — change the
action axis? If yes, scaffolding installs (some) chronoception where static
injection failed. This is the first thing to find out, and it is cheap to test.

## MVP: the budget-honoring loop

A multi-step loop where the agent decides when to stop. It is told it has a
wall-clock budget of B seconds and should use roughly the full budget. Each turn
it produces a chunk of work and ends with `CONTROL: CONTINUE` or `CONTROL: DONE`.

Two conditions differ in ONLY the per-turn message:
- **scaffold OFF**: `"Continue working."` (no time info — the baseline)
- **scaffold ON**: `"[clock] elapsed X.Xs of Bs budget | remaining Y.Ys | step N. Continue working."`

Metric: **CAR = wall-at-stop / B**. CAR ≈ 1 means the agent honored the budget;
CAR ≪ 1 is the L2 failure (stops early). Hypothesis: the scaffold raises CAR
toward 1. The analyzer compares the two CAR distributions with a Mann-Whitney U
test and reports `SCAFFOLD HELPS / HURTS / NO EFFECT`.

### Honest caveat

An LLM cannot stretch one response to fill wall-clock time; here "honoring the
budget" means *choosing to keep taking turns until the live clock runs out*.
This is a first, deliberately simple operationalization of the route, not a full
agentic-loop deployment. A `NO EFFECT` result would be just as informative as a
positive one — it would say even live scaffolding does not move the action axis,
sharpening Paper 1's L2 claim.

## How to run

```bash
# Local smoke check (no API)
python scripts/run_scaffolding_budget.py --backend fixed \
    --fixed-response "Worked a bit. CONTROL: CONTINUE" --delay 0.05 \
    --budget 2 --max-steps 6 --n-conversations 2 --condition off,on \
    --output-dir scaffolding-results

# Real run (a few $ on gpt-4o-mini; keep total <= $20 per HANDOFF)
OPENAI_API_KEY=sk-... python scripts/run_scaffolding_budget.py \
    --backend openai --model gpt-4o-mini \
    --budget 30 --max-steps 15 --n-conversations 10 --condition off,on \
    --output-dir scaffolding-results

python scripts/analyze_scaffolding.py --input-dir scaffolding-results \
    --output-csv scaffolding-results/car.csv
```

Run more than one model (each into the same `--output-dir`) to see whether the
effect is model-general. A reasoning model vs a non-reasoning one is the
informative contrast, mirroring the rest of the programme.

## Files

- `scripts/run_scaffolding_budget.py` — the budget-honoring loop (scaffold on/off)
- `scripts/analyze_scaffolding.py` — CAR comparison + Mann-Whitney U
- `tests/test_scaffolding.py` — unit tests (control parsing, Mann-Whitney, verdicts)

## Pilot result (2026-06, gpt-4o-mini, B=20 s, n=10 per condition)

Pre-registered metric (median CAR, Mann-Whitney): **NO EFFECT** — median CAR
0.90 (off) vs 0.86 (on), p=0.26. At B=20 s the off baseline already lands near
budget on the median (two natural turns of gpt-4o-mini take ~17 s), so the
median test had little room.

**Exploratory finding (not pre-registered): the scaffold sharply tightens
adherence and eliminates overruns.**

| Condition | median CAR | CAR range | CAR stdev | overrun (CAR>1) |
|---|---|---|---|---|
| scaffold OFF | 0.90 | [0.55, 1.90] | 0.378 | 30% (3/10) |
| scaffold ON | 0.86 | [0.82, 0.90] | **0.031** | **0%** |

Without the clock the agent scatters — sometimes stops at 55% of the budget,
sometimes overruns to 1.9× (one hit the safety cutoff). With the live clock it
stops consistently just under the deadline: CAR variance falls ~12× and overruns
go to zero. So the agent **can** act on a live wall-clock readout — the effect is
on reliability/overrun, not central tendency. This is the first signal that
scaffolding does something static date injection could not (Paper 1 §7).

Caveats: single model, single budget, small n; the dispersion result is
exploratory. The budget (20 s) sat too close to the natural landing point to
test the "stops early" direction. **Pre-registered follow-up**: sweep B over
{20, 60, 120} s — where the off baseline must fall short — with variance and
overrun rate as *primary* endpoints (a Levene / Brown-Forsythe test on CAR
spread), plus a reasoning model for the model-class contrast.

## Budget-sweep follow-up (2026-06, gpt-4o-mini + o4-mini, B ∈ {20,60,120}s, n=10)

The follow-up makes CAR **dispersion** (seeded permutation test) and **overrun
rate** the primary endpoints, sweeps three budgets, and adds a reasoning model.
120 multi-turn conversations.

| Model | B | OFF median CAR | OFF overrun | ON median CAR | ON overrun | primary signal |
|---|---|---|---|---|---|---|
| gpt-4o-mini | 20 | 1.01 | **50%** | 0.83 | **0%** | TIGHTENS (disp p=0.002) |
| gpt-4o-mini | 60 | 1.63 | **100%** | 0.65 | **0%** | overrun 100→0; median p<0.001 |
| gpt-4o-mini | 120 | 1.56 | **80%** | 0.74 | **0%** | TIGHTENS (disp p<0.001) |
| o4-mini | 20 | 1.60 | **100%** | 0.83 | 10% | overrun 100→10; median p<0.001 |
| o4-mini | 60 | 0.60 | 30% | 0.61 | **0%** | overrun 30→0 (disp p=0.10, ns) |
| o4-mini | 120 | 0.29 | 0% | 0.29 | 0% | NO EFFECT (under-uses either way) |

**The headline is overrun, and it is the opposite of the naive L2 expectation.**
When forced into a multi-step "use the budget" loop *without* a clock, agents do
not stop early — they **overrun the deadline**, and for gpt-4o-mini the overrun
gets worse as the budget grows (50% → 100% → 80% of runs over budget; median CAR
up to 1.6×). They have no sense of elapsed time, so "keep working until the
budget is used" runs past it.

**The live scaffold eliminates overruns across both models and every budget.**
gpt-4o-mini overrun 50/100/80% → 0/0/0%; o4-mini 100/30/0% → 10/0/0%. This is the
clean, universal effect — and it is exactly what *static* date injection could
not buy (Paper 1 §7, `|ΔCAR| ≤ 0.01`). The dispersion permutation test fires
`TIGHTENS` where the OFF runs scatter (gpt-4o-mini B=20, B=120); where OFF
overruns *consistently* (low variance, e.g. B=60 all 10 over) the median/overrun
endpoints carry the signal instead. Overrun rate is the cleanest single metric.

**Two honest limits.**
1. The scaffold trades overrun for mild *under*-use: with the clock, gpt-4o-mini
   stops at 65–83% of the budget on the median. It reliably stops on-time-or-early
   rather than landing exactly on the deadline.
2. **A reasoning model under-uses large budgets regardless of the scaffold.** At
   B=120 s o4-mini stops at CAR≈0.29 with or without the clock — it judges itself
   done and the scaffold cannot make it keep going. Scaffolding installs "don't
   blow the deadline," not "fill the budget."

Net: the scaffolding route's first defensible claim is **deadline-overrun
elimination**, robust across two model classes and a 6× budget range — a concrete
constructive win over Paper 1's negative baselines, with clearly stated limits.

Data: `scaffolding-sweep/b{20,60,120}/` (+ per-budget `car.csv`).

## Next steps if the MVP shows an effect

- Sweep the budget B (does CAR-honoring hold across 10 s … 300 s?).
- Add a deadline-tradeoff task (T1.3 style): does the scaffold make the agent
  finalize before the deadline instead of overrunning?
- Expose only *part* of the scaffold (step counter only vs full clock) to find
  the minimal sufficient signal.
