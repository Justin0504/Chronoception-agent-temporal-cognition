# Chronoception — Agent Temporal Cognition

LLM agents inhabit *token-time* but act in *wall-clock time*. They speak fluently about time — "this will take 30 minutes", "I'll work for 3 hours" — without knowing what time is, how long they have worked, or how long anything takes. We call this representational gap **the Augustine Problem**, after Augustine's observation that one knows time until asked to explain it.

This repository hosts the formal framework, diagnostic benchmark, and training stack of a two-paper arc on temporal cognition in LLM agents.

## Differentiation from Concurrent Work

Three concurrent papers operate in the same neighborhood; each touches one axis of our framework. We are the first work to unify the three. Details in [`RELATED_WORK.md`](RELATED_WORK.md); summary:

- **Garikaparthi (2026)** measures duration self-reports on **non-reasoning** models. We extend to reasoning-tuned models and find that reasoning training makes self-temporal honesty *worse*.
- **Ma et al. (2026, *Timely Machine*)** decouples wall-clock from generation length to *enable* time-aware test-time scaling. We invert the framing: the same decoupling is the diagnostic signature of *Agentic Parkinson's Law*.
- **Cheng et al. (2025, *Temporally Blind*)** note harness time-injection informally. We elevate this to the **Injection Tell** and supply a Closed-Lab Injection Atlas auditing wall-clock injection across ≥10 frontier harnesses.
- **Goel et al. (2025, *Chronocept*)** use *chronoception* for the temporal validity of facts. We use it in its original cognitive-science sense (perception of one's own work duration).

## The Framework

The gap is structural, not engineering. Foundation models are optimized under losses that are functionals of token sequences alone; the wall-clock duration over which each token is generated is not in the support of any of these losses. Wall-clock chronoception cannot emerge from token-only training, regardless of scale. **It must be installed.**

Three ontologically distinct times that agents systematically conflate:

| Symbol | Name | What it measures |
|---|---|---|
| τ_wall | Wall-clock time | External physical duration |
| τ_step | Step time | Agent's iteration / action count |
| τ_self | Self-narrated time | Agent's reported duration of its own work |

Three named empirical laws, one per axis:

- **L1 — Agentic Parkinson's Law** — agents inflate work to fill the wall-clock budget given to them (coefficient α).
- **L2 — Step-Clock Conflation** — agents silently translate wall-clock budgets into step-count terminators (Clock-Adherence Ratio CAR → 0 as budget grows). L1 and L2 are reconciled via the *regime transition* B*: L1-dominant below, L2-dominant above.
- **L3 — Temporal Confabulation** — agents systematically over-report the duration of their own work by 10–100× (ratio ρ ≈ +1.5). The **Reverse-Scaling Theorem** (§5.4): any token-only expansion of test-time compute monotonically increases ρ — reasoning training, by construction, makes self-temporal honesty strictly worse.

A single scalar **ε** aggregates the three failure modes. Agents satisfying ε < ε* = 0.20 are *chronoceptively grounded*; we pre-register that no foundation-model agent released as of 2026-05 satisfies this threshold.

The full formal specification — including the central **Chronoception Upstream Hypothesis** (∂L/∂ε < 0, causally — a structural claim grounded in the single-turn observability of ε), the Reverse-Scaling Theorem, the regime transition B*, the model invariant N_A, the Augustine threshold ε*, and six pre-registered predictions — lives in [`FRAMING.md`](FRAMING.md). All downstream work derives from that document.

## The Two Papers

### Paper 1 — ChronoBench

*The Augustine Problem: Why LLM Agents Cannot Tell Time.*

A diagnostic benchmark across the three axes, ~4000 instances, ≥25 frontier and open-source models. Quantifies L1, L2, L3 with their associated metrics; tests the four predictions of `FRAMING.md` §9; establishes the cross-model scaling of ε. Lives under [`bench/`](bench/) (forthcoming).

### Paper 2 — ChronoStack

*Bridging Token-Time and Wall-Clock: Solving the Augustine Problem with ChronoStack.*

A four-component training and inference-time framework: temporal pretraining corpus, wall-clock self-reflection SFT, time-efficient RL, inference-time wall-clock critic. Evaluates ε reduction on ChronoBench and L gains on SWE-Bench Verified / WebArena / GAIA under fixed wall-clock budgets. Lives under [`stack/`](stack/) (forthcoming).

## Repository Layout

```
.
├── FRAMING.md              Source of truth — research programme definitions, laws, predictions
├── RELATED_WORK.md         Concurrent-work survey and differentiation rationale
├── notation.tex            LaTeX macros mirroring FRAMING §11
├── pyproject.toml          Python package metadata
├── chronoception/          Python package (import chronoception)
│   ├── bench/              Paper 1 — ChronoBench (metrics, trajectories, task schema)
│   └── stack/              Paper 2 — ChronoStack (placeholder in v0.0.1)
├── position-note/          Phase 1 arXiv position note draft
├── paper1/                 Paper 1 scope, abstract, outline, annotation protocol
├── tests/                  Unit tests for metrics and registry
├── leaderboard/            Cross-model results, public submission interface
└── paper2/                 Paper 2 LaTeX sources (forthcoming)
```

## Install (development)

```bash
git clone https://github.com/Justin0504/Chronoception-agent-temporal-cognition
cd Chronoception-agent-temporal-cognition
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
```

## Status

- 2026-05-28 — Framework v1.0 locked (`FRAMING.md`).
- In progress — Paper 1 position note; ChronoBench v0 scaffolding.

## Citation

A citation entry will be added when the position note is on arXiv. In the interim, please reference this repository and `FRAMING.md` v1.0.
