# Chronoception — Agent Temporal Cognition

LLM agents inhabit *token-time* but act in *wall-clock time*. They speak fluently about time — "this will take 30 minutes", "I'll work for 3 hours" — without knowing what time is, how long they have worked, or how long anything takes. We call this representational gap **the Augustine Problem**, after Augustine's observation that one knows time until asked to explain it.

This repository hosts the formal framework, diagnostic benchmark, and training stack of a two-paper arc on temporal cognition in LLM agents.

## The Framework

Three ontologically distinct times that agents systematically conflate:

| Symbol | Name | What it measures |
|---|---|---|
| τ_wall | Wall-clock time | External physical duration |
| τ_step | Step time | Agent's iteration / action count |
| τ_self | Self-narrated time | Agent's reported duration of its own work |

Three named empirical laws, one per axis:

- **L1 — Agentic Parkinson's Law** — agents inflate work to fill the wall-clock budget given to them (coefficient α).
- **L2 — Step-Clock Conflation** — agents silently translate wall-clock budgets into step-count terminators (Clock-Adherence Ratio CAR → 0 as budget grows).
- **L3 — Temporal Confabulation** — agents systematically over-report the duration of their own work by 10–100× (ratio ρ ≈ +1.5); reasoning-tuned models exhibit *more* confabulation, not less.

A single scalar **ε** aggregates the three failure modes into a chronoceptive calibration error.

The full formal specification — including the central **Chronoception Upstream Hypothesis** (∂L/∂ε < 0, causally) and four pre-registered falsifiable predictions — lives in [`FRAMING.md`](FRAMING.md). All downstream work derives from that document.

## The Two Papers

### Paper 1 — ChronoBench

*The Augustine Problem: Why LLM Agents Cannot Tell Time.*

A diagnostic benchmark across the three axes, ~4000 instances, ≥25 frontier and open-source models. Quantifies L1, L2, L3 with their associated metrics; tests the four predictions of `FRAMING.md` §9; establishes the cross-model scaling of ε. Lives under [`bench/`](bench/) (forthcoming).

### Paper 2 — ChronoStack

*Bridging Token-Time and Wall-Clock: Solving the Augustine Problem with ChronoStack.*

A four-component training and inference-time framework: temporal pretraining corpus, wall-clock self-reflection SFT, time-efficient RL, inference-time wall-clock critic. Evaluates ε reduction on ChronoBench and L gains on SWE-Bench Verified / WebArena / GAIA under fixed wall-clock budgets. Lives under [`stack/`](stack/) (forthcoming).

## Repository Layout

```
chronoception/
├── FRAMING.md         Source of truth — definitions, laws, predictions
├── notation.tex       LaTeX macros mirroring FRAMING §11
├── bench/             Paper 1 — ChronoBench (tasks, metrics, eval harness)
├── stack/             Paper 2 — ChronoStack (data, training, inference critic)
├── leaderboard/       Cross-model results, public submission interface
└── paper1/, paper2/   LaTeX sources
```

## Status

- 2026-05-28 — Framework v1.0 locked (`FRAMING.md`).
- In progress — Paper 1 position note; ChronoBench v0 scaffolding.

## Citation

A citation entry will be added when the position note is on arXiv. In the interim, please reference this repository and `FRAMING.md` v1.0.
