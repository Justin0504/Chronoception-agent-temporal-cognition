# Project Status — 2026-06-10

Snapshot of every component in the chronoception research programme. For the high-level story, read `ONBOARDING.md`. For the six-day handoff specifics, read `HANDOFF.md`.

---

## Paper 1 — *The Augustine Problem in Agents*

**Status: complete draft, ready for arXiv.** 34 pages, ~478 KB PDF.

- LaTeX source: `paper1/arxiv-v0/`
- Latest frozen PDF: `paper1/augustine_problem_v8_dual_scale.pdf`
- Overleaf upload package: `paper1/augustine_overleaf.zip`
- Build: `cd paper1/arxiv-v0 && tectonic main.tex` (one command, ~30 s)

### Content checklist

- [x] Abstract (one paragraph, structural synthesis style)
- [x] §1 Introduction with theorem-arc figure
- [x] §2 The Three Times + ontology figure
- [x] §3 Augustine Problem definition + Theorem 1 (CIT) with proof sketch
- [x] §4 ChronoBench with 9-capability table + 10-agent panel
- [x] §5 L2 Step-Clock Conflation with CAR table
- [x] §6 L3 Temporal Confabulation in four subsections (retro, Reverse-Scaling Theorem with proof, Calibration Catastrophe, positive control) + honest negative on cross-trajectory drift
- [x] §7 The Injection Tell with 4-tier Atlas
- [x] §8 Aggregate $\varepsilon$ + panel ranking figure
- [x] §9 Agentic Timeline Hypothesis + P12 supportive evidence on METR HCAST
- [x] §10 Related Work (concurrent + historical positioning)
- [x] §11 What We Are and Are Not Claiming + 4 falsification criteria (F1–F4)
- [x] §12 Future Work — Spatiotemporal Generalisation + Theorem 3 (SIT) + Agentic Frontier figure
- [x] §13 Conclusion
- [x] Appendix A annotation protocol
- [x] Appendix B full panel tables
- [x] Appendix C atlas evidence (verbatim leaked-prompt excerpts)
- [x] Appendix D L3 sub-failure detail
- [x] Appendix E spatiotemporal generalisation full sketch
- [x] Appendix F operational chronoception audit checklist

### Theorems

- **Theorem 1 (CIT, §3)** — token-only loss has no wall-clock gradient. Proved (closed-form).
- **Theorem 2 (Reverse-Scaling, §6.2)** — under CIT, $|\rho|$ is monotone non-decreasing in reasoning-token expansion. Proved (closed-form). Confirmed empirically intra-model (o4-mini × 3 effort) and cross-model (Sonnet 4.6 ± thinking).
- **Theorem 3 (SIT, §12)** — CIT generalised to any external metric (time or space). Proved (sketch).

### Figures

| # | File | Section |
|---|---|---|
| 1 | `figures/theorem_arc.pdf` | §1 |
| 2 | `figures/three_times.pdf` | §2 |
| 3 | `figures/reverse_scaling.pdf` | §6.2 |
| 4 | `figures/calibration_catastrophe.pdf` | §6.3 |
| 5 | `figures/a1_positive_control.pdf` | §6.4 |
| 6 | `figures/epsilon_panel.pdf` | §8 |
| 7 | `figures/p12_hcast.pdf` | §9 |
| 8 | `figures/agentic_frontier.pdf` | §12 |

### Empirical inventory

| Dataset | Trajectories | Used for |
|---|---|---|
| `pilot-results/` | 1{,}440 | 8-agent pilot on T1.1 / T2.3 / T3.1 |
| `e1-results/` | 2{,}520 | 6 new sub-capabilities × 7 agents |
| `e2-results/` | 120 | o4-mini × 3 reasoning_effort (Reverse-Scaling intra-model) |
| `e3-results/` | 60 | Sonnet 4.6 ± extended thinking (Reverse-Scaling cross-model) |
| `e5-results/` | 180 | DeepSeek-R1-Distill-14B × 3 token budget |
| **Total** | **~4{,}320** | |

External: METR HCAST (14{,}709 runs, public) — supports P12 qualitatively.

### Pre-registered predictions

12 predictions logged in `OSF_PREREGISTRATION.md`. 9 confirmed, 1 cross-trajectory proxy refuted, 2 deferred. 4 explicit falsification criteria in Paper 1 §11.

### A.1 toy positive control

The construction: 500 SFT pairs of (T3.1 prompt, base response + accurate self-duration), LoRA fine-tune (rank 16, 3 epochs), evaluate on 30 held-out T3.1 instances.

| Model | Baseline $|\rho|$ | Fine-tuned $|\rho|$ | T3.1 score | Crosses $\varepsilon^*$? |
|---|---|---|---|---|
| Qwen2.5-1.5B-Instruct | 1.373 | 0.302 | 0.151 | **yes** |
| Qwen2.5-7B-Instruct | 0.932 | 0.505 | 0.252 | no (partial reduction) |

Files: `paper2_chronostack/toy_a1/` — scripts, summary JSONs, per-trajectory rows.

---

## Paper 2 — *ChronoStack*

**Status: scoped only. No drafts.**

The constructive program: routes to install chronoception. Sketched in `paper2_chronostack/` (mostly empty), referenced from Paper 1 throughout.

### Four installation routes (paper-2 design)

| Route | Idea | First proof point |
|---|---|---|
| **Loss extension** | Wall-clock-supported SFT or RL reward | A.1 toy positive control (SFT only) demonstrates direction |
| **Tool interface** | Learned policy over `get_current_time()` etc. | None yet |
| **Scaffolding** | Harness exposes $\tau_{\mathrm{step}}$ counter, deadline, budget remaining | None yet |
| **Architectural primitive** | New input modality that takes wall-clock as argument | None yet |

The work needed: design each route, build a minimum-viable implementation, evaluate on ChronoBench, report $\varepsilon$ reduction across all 9 sub-capabilities, contrast against Paper 1's negative-result baselines.

---

## Paper 3 — *The Agentic Frontier*

**Status: scoped only.** Full scope lock in `PAPER3_SCOPE.md`. Forward-referenced from Paper 1 §12 and Appendix E.

### Theoretical claims

- Three Spaces ontology ($\sigma_{\mathrm{world}}, \sigma_{\mathrm{visit}}, \sigma_{\mathrm{self}}$)
- Theorem 3 (SIT) — already in Paper 1
- Three spatial laws SL1 / SL2 / SL3 mirroring L1 / L2 / L3
- Agentic Frontier hypothesis: $T_{\max}(A) \cdot S_{\max}(A) \leq C / \varepsilon_{ST}(A)$
- Cartographic Problem as the spatial face of the Augustine Problem

### Five proposed experiments

| Experiment | What it tests | Estimated cost |
|---|---|---|
| **E6** Spatial-CAR on SWE-Bench Lite | SL2 (visit-step conflation) | ~$430 + 30 GPU-h |
| **E7** Joint $(T, S)$ budgets | Whether agents respect both, one, or neither | ~$300 |
| **E8** Within-trajectory drift on long horizons | P8 / P9 measurement | ~$200 |
| **E9** The Cartographic Tell | Closed-lab harnesses inject spatial context | $0 (audit) |
| **E10** Agentic Frontier mapping | Constant-success contour on $(T, S)$ grid | ~$500 |
| **Total** | | **~$1{,}430 + 30 GPU-h** |

None run yet.

---

## ChronoBench — the benchmark

**Status: production.** Pip-installable Python package, 9 sub-capabilities, 3 backends.

```
chronoception/
├── bench/
│   ├── tasks/
│   │   ├── registry.py        9 sub-capability declarations
│   │   ├── instances.py       deterministic generators (seed=0)
│   │   └── schema.py
│   ├── metrics.py             α, CAR, ρ, ε implementations
│   ├── parsers/
│   │   └── tau_self.py        two-stage regex + LLM-judge
│   ├── trajectory.py
│   └── eval/
│       ├── runner.py
│       ├── settings.py        EvalSetting.{NO_INJECTION, WITH_INJECTION}
│       └── agents/
│           ├── openai_backend.py
│           ├── anthropic_backend.py
│           ├── google_backend.py    (stub)
│           └── echo.py              (testing)
```

### Capabilities

| Code | Axis | Tests |
|---|---|---|
| T1.1 | $\tau_{\mathrm{wall}}$ | Clock awareness |
| T1.2 | $\tau_{\mathrm{wall}}$ | Elapsed-time tracking |
| T1.3 | $\tau_{\mathrm{wall}}$ | Deadline-aware tradeoff |
| T2.1 | $\tau_{\mathrm{step}}$ | Step-budget honoring |
| T2.2 | $\tau_{\mathrm{step}}$ | Step-to-wall translation |
| T2.3 | $\tau_{\mathrm{step}}$ | Wall-budget execution (L2 core) |
| T3.1 | $\tau_{\mathrm{self}}$ | Retrospective $\rho$ |
| T3.2 | $\tau_{\mathrm{self}}$ | Prospective $\rho$ |
| T3.3 | $\tau_{\mathrm{self}}$ | 90% CI calibration |

### Tests

`pytest tests/ -q` — passes locally.

---

## Reproducibility

Docker-based reproduction in `Dockerfile`. Tiered guide in `REPRODUCIBILITY.md`:

- **Tier A** — re-render all figures + metrics from committed trajectories. No API, no GPU, ~5 min in Docker or local venv.
- **Tier B** — re-run a single agent end-to-end on the OpenAI or Anthropic API. ~$10, ~30 min.
- **Tier C** — full panel re-sweep. ~$50, 1–2 days.

OSF pre-registration in `OSF_PREREGISTRATION.md` locked at commit `a6f20c3`.

---

## Server / infrastructure

- **Yue Zhao lab cluster** — `haiyuez@10.136.20.188`, 8× RTX 6000 Ada (48 GB each). Credentials not in repo. Used for vLLM serving and A.1 LoRA training.
- **A.1 training environment** — separate venv at `/data/haiyuez/a1venv` (transformers 4.46, peft 0.13, trl 0.12) to avoid breaking the vLLM env (transformers pinned to 4.45.2).
- **A.1 working directories** — `/data/haiyuez/chronoception-a1/` (1.5B) and `/data/haiyuez/chronoception-a1-7b/` (7B). Contains scripts + data + checkpoints + logs.

---

## Git state

```
main branch
├── 56 commits since project start
├── ~4{,}320 trajectory JSONs committed (~600 MB)
├── 8 figure PDFs + 8 PNGs committed
├── 8 frozen PDF snapshots (v2.5 through v8_dual_scale)
└── No open PRs
```

Latest commits:

```
fa3bdcd A.1 dual-scale: Qwen2.5-7B partial reduction added alongside 1.5B crossing
e913d74 Add honest negative finding in §6: cross-trajectory drift refutes P8 direction
dae177b Add 3 polish figures: theorem arc (§1), A.1 positive control (§6.4), Agentic Frontier (§12)
4785f5d Title: The Augustine Problem in Agents
f8068ba A.1 POSITIVE CONTROL ACHIEVED — CIT's converse demonstrated
```

GitHub remote: `https://github.com/Justin0504/Chronoception-agent-temporal-cognition`.
