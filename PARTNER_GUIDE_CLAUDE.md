# Partner Guide — Running Claude Models on ChronoBench Pilot

**Status**: v1 (2026-05-30)
**For**: Justin's research collaborator
**Owner**: Role B on the Claude slice
**Time to first result**: ~10 minutes
**Total time commitment**: ~3 hours interactive + ~2 hours waiting for API runs

You will run the same ChronoBench experiments Justin is running on OpenAI, but using Anthropic Claude models. This document is the complete recipe — clone the repo, set your API key, run four commands, push the results. Justin's `compute_metrics.py` will then merge your Claude data with his OpenAI data into a single panel.

---

## 1. What you're testing

The project tests whether LLM agents perceive their own time. Concretely, you'll run each Claude model through three sub-capabilities × two settings:

| Sub-capability | What it tests |
|---|---|
| **T1.1 Clock awareness** | Agent reports the current date/time. Tests P1a: does wall-clock injection close clock-awareness? |
| **T2.3 Wall-budget execution** | Agent told "work for B seconds". Tests L2: does the agent honor the wall-clock budget or stop early? |
| **T3.1 Retrospective duration** | Agent completes a task, then reports how long it took. Tests L3: does the agent over-report its duration? |

| Setting | What it does |
|---|---|
| **A — no_injection** | System prompt = "You are a helpful assistant." (no time information) |
| **B — with_injection** | System prompt prepended with `Current date and time: <ISO timestamp>` |

For the full framing, see [`FRAMING.md`](FRAMING.md). For Justin's first results (180 trajectories on GPT-4o-mini), see [`pilot-results/metrics.csv`](pilot-results/metrics.csv).

---

## 2. Setup (5–10 minutes)

```bash
# 1. Clone the repo
git clone https://github.com/Justin0504/Chronoception-agent-temporal-cognition.git chronoception
cd chronoception

# 2. Create venv (Python 3.10+) and install with the Anthropic extra
python3 -m venv .venv
.venv/bin/pip install -e ".[anthropic]"

# 3. Set your Anthropic API key (copy template, fill in)
cp .env.example .env
# Open .env in your editor and put your real key on the ANTHROPIC_API_KEY line.
# DO NOT commit .env — it is .gitignored.

chmod 600 .env

# 4. Verify by sourcing and running a 1-trajectory smoke test (~$0.001)
set -a; source .env; set +a
.venv/bin/python scripts/run_pilot.py \
    --backend anthropic --model claude-haiku-4-5 \
    --capability T1.1 --setting no_injection \
    --count 1 \
    --output-dir /tmp/smoke-test/

# Inspect the result
cat /tmp/smoke-test/anthropic_claude-haiku-4-5/T1.1/no_injection/T1.1.000.json
```

If you see a JSON file with a non-empty `steps` array and a Claude response, the setup is working. Proceed to §3.

---

## 3. Models to run

Four runs total. Each uses the same `scripts/run_pilot.py` command with a different `--model`. Run them in the order below; you can skip the extended-thinking run if you want to economize.

| # | Model | Model ID for `--model` | Why |
|---|---|---|---|
| 1 | Claude Haiku 4.5 | `claude-haiku-4-5` | Cheap baseline; matches GPT-4o-mini tier |
| 2 | Claude Sonnet 4.6 | `claude-sonnet-4-6` | Mid-tier; matches GPT-4o tier |
| 3 | Claude Opus 4.7 | `claude-opus-4-7` | Frontier closed-source non-reasoning |
| 4 | Claude Opus 4.7 + Extended Thinking | `claude-opus-4-7` with `--extra-body '{"thinking":{"type":"enabled","budget_tokens":16000}}'` | Reasoning wedge for the P2 prediction |

The first three confirm the framework's failure pattern at three Claude capability tiers. The fourth is the most valuable single experiment for the paper — it tests the framework's **Reverse-Scaling Theorem** by comparing the same Claude Opus model with and without extended thinking on the L3 (self-narration) axis.

---

## 4. Run commands (full)

### 4.1 Claude Haiku 4.5 — full cheap-tier (≈ $0.50, ≈ 15 min wall-clock)

```bash
set -a; source .env; set +a
.venv/bin/python scripts/run_pilot.py \
    --backend anthropic --model claude-haiku-4-5 \
    --capability T1.1,T2.3,T3.1 \
    --setting no_injection,with_injection \
    --count 30 \
    --output-dir pilot-results/
```

Produces 180 trajectory JSONs under `pilot-results/anthropic_claude-haiku-4-5/`.

### 4.2 Claude Sonnet 4.6 — mid-tier (≈ $3, ≈ 20 min)

```bash
set -a; source .env; set +a
.venv/bin/python scripts/run_pilot.py \
    --backend anthropic --model claude-sonnet-4-6 \
    --capability T1.1,T2.3,T3.1 \
    --setting no_injection,with_injection \
    --count 30 \
    --output-dir pilot-results/
```

180 trajectories under `pilot-results/anthropic_claude-sonnet-4-6/`.

### 4.3 Claude Opus 4.7 — frontier non-reasoning (≈ $15, ≈ 30 min)

```bash
set -a; source .env; set +a
.venv/bin/python scripts/run_pilot.py \
    --backend anthropic --model claude-opus-4-7 \
    --capability T1.1,T2.3,T3.1 \
    --setting no_injection,with_injection \
    --count 30 \
    --output-dir pilot-results/
```

180 trajectories under `pilot-results/anthropic_claude-opus-4-7/`.

### 4.4 Claude Opus 4.7 + Extended Thinking — reasoning wedge (≈ $25, ≈ 45 min)

This is the **most important single experiment** in your slice. Note the special `--extra-body` argument that enables Claude's extended thinking mode. Run on **T3.1 only** (the L3 axis) because the P2 prediction lives there.

```bash
set -a; source .env; set +a
.venv/bin/python scripts/run_pilot.py \
    --backend anthropic --model claude-opus-4-7 \
    --capability T3.1 \
    --setting no_injection,with_injection \
    --count 30 \
    --extra-body '{"thinking":{"type":"enabled","budget_tokens":16000}}' \
    --output-dir pilot-results/anthropic_claude-opus-4-7-thinking/
```

60 trajectories under `pilot-results/anthropic_claude-opus-4-7-thinking/`. Use the custom `--output-dir` to keep the thinking variant separate from the non-thinking baseline (Section 4.3).

---

## 5. After each run — verify

After every model finishes, run the metrics script:

```bash
.venv/bin/python scripts/compute_metrics.py \
    --input-dir pilot-results/ \
    --output-csv pilot-results/metrics.csv \
    --epsilon-csv pilot-results/epsilon.csv
```

Inspect the table. For each Claude model you should see:

| Metric | Expected range (per FRAMING.md v1.6) |
|---|---|
| **T1.1 pass_rate, Setting A** | < 40% (model refuses; mentions training cutoff) |
| **T1.1 pass_rate, Setting B** | ≥ 95% (model quotes the injected timestamp) |
| **T2.3 median CAR, both settings** | < 0.1 (agent uses <10% of budget — confirms L2) |
| **T2.3 median α, both settings** | ≈ 0 (no Parkinson behavior — confirms v1.6 correction) |
| **T3.1 median ρ, both settings** | between +0.5 and +1.8 (10× to 60× over-report — confirms L3) |
| **Aggregate ε, both settings** | > 0.20 (above Augustine threshold — chronoceptively blind) |

For the **extended-thinking variant** (4.4), the framework predicts that **ρ is strictly larger than the non-thinking Opus baseline**. This is the P2 wedge — the headline finding the framework predicts about reasoning models. If you observe it, flag Justin immediately.

---

## 6. Coordination — push results

After each model finishes and the metrics look reasonable, commit and push:

```bash
git pull
git add pilot-results/anthropic_claude-haiku-4-5/  # or whatever model you just finished
git add pilot-results/metrics.csv pilot-results/epsilon.csv
git commit -m "pilot/B: Claude Haiku 4.5 cheap-tier complete (180 trajectories)"
git push
```

Justin will see your push and merge it into his analysis. **Push after each model, not at the end** — this lets Justin start drafting figures with your data as it arrives.

If you hit a problem (rate limit, API error, unexpected metric), commit anyway with a `WIP` prefix and tag Justin:

```bash
git commit -m "WIP pilot/B: Claude Haiku 4.5 partial — rate limit at instance 50"
```

---

## 7. Total cost estimate

| Run | Trajectories | Estimated $ |
|---|---|---|
| Haiku 4.5 full | 180 | $0.50 |
| Sonnet 4.6 full | 180 | $3 |
| Opus 4.7 full | 180 | $15 |
| Opus 4.7 + thinking | 60 | $25 |
| **Total** | **600** | **~$43** |

If you can only spend $5, do Haiku 4.5 + Sonnet 4.6. If you can spend $20, add Opus 4.7. The extended-thinking variant is the most expensive but also the most valuable single experiment in your slice.

You can use Claude.ai's free web tier to look at responses qualitatively, but **the pilot needs the API** because we measure wall-clock and parse exact responses programmatically. Free web tier cannot substitute for the API runs.

---

## 8. Failure modes — what to do

| If you see this | Do this |
|---|---|
| `ANTHROPIC_API_KEY is not set` | `set -a; source .env; set +a` (sources the env vars into the current shell) |
| `anthropic` package missing | `.venv/bin/pip install -e ".[anthropic]"` |
| Rate limit retries take >1 minute | Reduce `--count` to 10 and run multiple times; Justin had a 14-hour retry on GPT-4o-mini that he later excluded as an outlier |
| `extra_body` JSON parse error | Make sure the JSON is single-quoted in shell: `--extra-body '{"thinking":...}'` not `--extra-body "{\"thinking\":...}"` |
| Trajectory file shows empty response content | Check `metadata.stop_reason` — Claude may have refused; that's still valid data, just lower T1.1 pass rate |
| Unexpectedly low ρ (close to 0) | This is interesting! Could be the agent honoring duration. Flag Justin immediately — it would be evidence against L3 for that Claude model. |

---

## 9. Reference — files you'll touch

| File | What it is |
|---|---|
| [`.env`](.env) | Your API key (you create this from `.env.example`); never committed |
| [`scripts/run_pilot.py`](scripts/run_pilot.py) | The runner CLI — you call this for each model |
| [`scripts/compute_metrics.py`](scripts/compute_metrics.py) | Reads `pilot-results/` and computes ε, CAR, ρ, α tables |
| [`pilot-results/`](pilot-results/) | Where trajectories live; you push your Claude trajectories here |
| [`pilot-results/metrics.csv`](pilot-results/metrics.csv) | Joint metric table — yours and Justin's pooled |
| [`FRAMING.md`](FRAMING.md) | The full theoretical framework — read if curious; not required for the runs |
| [`PHASE2_PILOT_PLAN.md`](PHASE2_PILOT_PLAN.md) | The 6-week project plan; you're executing the Claude slice of W2/W4/W5 |

---

## 10. Quick checklist

```
[ ] Cloned repo
[ ] Created venv, installed with [anthropic] extra
[ ] Set ANTHROPIC_API_KEY in .env (file chmod 600)
[ ] Smoke test produced a valid trajectory JSON
[ ] Run 4.1 Haiku 4.5 → verified → pushed
[ ] Run 4.2 Sonnet 4.6 → verified → pushed
[ ] Run 4.3 Opus 4.7 → verified → pushed
[ ] Run 4.4 Opus 4.7 + Extended Thinking → verified → pushed
[ ] Ran compute_metrics.py after each push
[ ] Tagged Justin if any unexpected results
```

---

## 11. Questions

If anything in this document is unclear or any step fails in a way the table in §8 doesn't cover, ping Justin and we'll update the document. Each Claude model's data joins his OpenAI panel directly — the project's headline figures cannot be drawn without your runs.

---

## Changelog

- **v1 (2026-05-30)** — Initial partner onboarding document. Four runs (Haiku → Sonnet → Opus → Opus+Thinking), unified output directory convention, metric verification per run, git-push coordination protocol, total cost ~$43.
