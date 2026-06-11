# Onboarding — Chronoception Project

Welcome. Justin is offline for six days starting 2026-06-10. This document gets you up to speed on what the project is, where things live, and what is open.

If you only read one section: read **§1 (TL;DR)** + **§2 (Where things are)** + **§7 (What is open right now)**.

---

## 1. TL;DR

Three-paper research arc on **chronoception in LLM agents** — whether agents can perceive their own wall-clock time. The named central claim is the **Augustine Problem**: agents speak fluently about durations they cannot perceive, because the standard token-only training loss has no wall-clock signal in its support.

- **Paper 1**: *The Augustine Problem in Agents*. Hybrid position/theory/benchmark paper. **Status: complete draft, 34 pages**, builds clean with `tectonic`. Two theorems with proofs (CIT, Reverse-Scaling). Five empirical findings on 10 agent configurations (~4{,}000 trajectories). A toy positive control (A.1) demonstrates CIT's converse on Qwen2.5-1.5B + 7B. Frozen PDF at `paper1/augustine_problem_v8_dual_scale.pdf`. Ready for arXiv when Justin returns.
- **Paper 2**: *ChronoStack*. Constructive routes to install chronoception. **Status: scoped only.** No drafts yet.
- **Paper 3**: *The Agentic Frontier*. Spatiotemporal generalisation. **Status: scoped only**, full sketch in `PAPER3_SCOPE.md` and in Paper 1 Appendix E.

---

## 2. Where things are

```
chronoception/
├── ONBOARDING.md            (this file — start here)
├── PROJECT_STATUS.md        (current state of everything in detail)
├── HANDOFF.md               (six-day handoff: pending items + safe-to-touch list)
├── README.md                (public-facing project README)
├── FRAMING.md               (framework v2.5 — source of truth; ~115 KB)
├── REPRODUCIBILITY.md       (Docker + 3-tier reproduction guide)
├── PAPER3_SCOPE.md          (Paper 3 scope lock)
├── OSF_PREREGISTRATION.md   (locked pre-registration document)
├── notation.tex             (shared LaTeX macros)
├── pyproject.toml           (pip-installable Python package metadata)
│
├── paper1/                  (Paper 1 — the Augustine Problem)
│   ├── arxiv-v0/            (LaTeX source: main.tex + sections/ + figures/ + bib/)
│   ├── augustine_problem_v8_dual_scale.pdf    (latest frozen PDF — use this)
│   ├── augustine_overleaf.zip                 (self-contained Overleaf upload)
│   └── augustine_problem_v[1-8]_*.pdf         (historical snapshots)
│
├── paper2/                  (legacy stub — ignore for now)
├── paper2_chronostack/      (Paper 2 working dir)
│   └── toy_a1/              (A.1 toy positive control — scripts + results)
│
├── chronoception/           (Python package `chronoception` — pip-installable)
│   └── bench/               (ChronoBench: tasks, metrics, parsers, agent backends)
│
├── scripts/                 (figure generators, eval scripts, analysis)
├── tests/                   (pytest)
│
├── pilot-results/           (1,440 traj — original 8-agent pilot, T1.1/T2.3/T3.1)
├── e1-results/              (2,520 traj — 6 new sub-capabilities)
├── e2-results/              (120 traj — o4-mini × 3 reasoning_effort)
├── e3-results/              (60 traj — Sonnet 4.6 ± thinking)
├── e5-results/              (180 traj — DeepSeek-R1-Distill-14B × 3 budget)
│
└── leaderboard/  position-note/  (older artifacts)
```

The framework, definitions, all theorems, all predictions, and the changelog live in **`FRAMING.md`** (v2.5). When in doubt, that file is the source of truth.

The current paper's structure lives in **`paper1/arxiv-v0/main.tex`** with one `\input{sections/…tex}` per section.

---

## 3. The framework in 90 seconds

LLM agents are trained on token sequences (next-token CE / SFT / RLHF / RLVR / reasoning supervision) and deployed in wall-clock time. None of those losses contains wall-clock time in its support, so the policy gradient carries no signal aligning wall-clock with any internal representation. We call the resulting gap the **Augustine Problem**.

We decompose any agent trajectory into three projections of time — **wall-clock $\tau_{\mathrm{wall}}$**, **step time $\tau_{\mathrm{step}}$** (policy invocation count), and **self-narrated time $\tau_{\mathrm{self}}$**. A chronoceptively grounded policy enforces $\tau_{\mathrm{wall}} \approx \tau_{\mathrm{step}} \cdot \langle\Delta t\rangle \approx \tau_{\mathrm{self}}$. The Augustine Problem is the failure to enforce this identity.

We measure the failure via **ChronoBench** (9 sub-capabilities, 3 per axis) on 10 agent configurations from 3 providers (OpenAI / Anthropic / open-source vLLM). Findings on roughly 4{,}000 trajectories:

1. **L2 Step-Clock Conflation**: every panel agent uses $< 5\%$ of wall-clock budgets given to it.
2. Median $|\rho| = |\log_{10}(\tau_{\mathrm{self}}/\tau_{\mathrm{wall}})|$ closes 94\% across 5 non-reasoning frontier generations, while $\mathrm{CAR}$ does not — narrative-axis is text-trainable; action-axis is not.
3. **Reverse-Scaling Theorem**: under CIT, $|\rho|$ is monotone non-decreasing in reasoning-token expansion. Confirmed intra-model on o4-mini and cross-model on Claude Sonnet 4.6 with vs without extended thinking.
4. **Calibration Catastrophe**: every panel agent's nominally $90\%$ confidence interval on self-duration achieves $\leq 50\%$ coverage; GPT-4o achieves $0\%$.
5. **Injection Tell**: $3/3$ consumer web-chat products inject today's date into system prompts (verbatim leaked-system-prompt evidence); $0/3$ developer tools do.

A **toy positive control** (A.1) demonstrates CIT's converse: wall-clock-supported LoRA SFT on Qwen2.5-1.5B crosses the Augustine threshold $\varepsilon^* = 0.20$ on T3.1 in 60 seconds of training. The 7B variant reduces $|\rho|$ 46\% but does not cross — a calibrated reminder that larger models need richer interventions.

The deployment bound is the **Agentic Timeline Hypothesis**: $T_{\max}(A) \propto 1/\varepsilon(A)$, qualitatively supported by 14{,}709 public METR HCAST runs (reasoning models decay $20\%$ faster than non-reasoning at matched short-horizon success).

The framework generalises along its natural other axis to the **Cartographic Problem** (spatial), the **Spatiotemporal Impossibility Theorem (SIT)**, and the **Agentic Frontier** $T_{\max}(A) \cdot S_{\max}(A) \leq C / \varepsilon_{ST}(A)$ — Paper 3 scope.

---

## 4. Reading Paper 1

The latest compiled PDF is **`paper1/augustine_problem_v8_dual_scale.pdf`** (34 pages, 478 KB).

Section guide:

| § | Topic | Read if you want to understand |
|---|---|---|
| 1 | Introduction | The whole story in 1.5 pages + the framework spine figure |
| 2 | The Three Times | The ontology |
| 3 | The Augustine Problem | Definition 2, Theorem 1 (CIT) with proof |
| 4 | ChronoBench | The benchmark, panel, settings |
| 5 | L2 Step-Clock Conflation | Primary action-axis finding |
| 6 | L3 Temporal Confabulation | Primary narrative-axis finding, four sub-failures, Reverse-Scaling, Calibration Catastrophe, A.1 positive control, honest negative on cross-trajectory drift |
| 7 | The Injection Tell | Cross-vendor natural experiment |
| 8 | Chronoceptive Calibration Error $\varepsilon$ | The single scalar; panel ranking |
| 9 | Agentic Timeline Hypothesis | Deployment bound + HCAST evidence |
| 10 | Related Work | Concurrent papers + historical positioning |
| 11 | What We Are and Are Not Claiming | Anticipated objections + 4 falsification criteria |
| 12 | Future Work — Spatiotemporal Generalisation | Theorem 3 (SIT) + Cartographic Problem + Agentic Frontier |
| 13 | Conclusion | Three-layer argument summary |
| A–F | Appendices | Annotation protocol, full panel tables, atlas evidence, L3 detail, spatiotemporal full sketch, operational audit checklist |

The eight figures: theorem arc (§1), Three Times (§2), Reverse-Scaling (§6.2), Calibration Catastrophe (§6.3), A.1 positive control (§6.4), epsilon panel (§8), HCAST scatter (§9), Agentic Frontier (§12).

---

## 5. Editing the paper

Local build (one command, no LaTeX system needed):

```bash
cd ~/chronoception/paper1/arxiv-v0
brew install tectonic            # one-time, if not installed
tectonic main.tex                # builds main.pdf in ~30s
```

Overleaf alternative: upload `paper1/augustine_overleaf.zip` as a new project. The package is self-contained (notation.tex copied in, paths flattened). Compiler: pdfLaTeX. Main document: `main.tex`.

For section edits, work inside `paper1/arxiv-v0/sections/`. Each section is a separate `.tex` file. The macros are in `notation.tex` (at repo root, copied into the Overleaf package).

The author block in `paper1/arxiv-v0/main.tex` currently lists Aojie (Justin) Yuan and Yue Zhao. Add yourself if appropriate.

---

## 6. Running ChronoBench

The Python package is pip-installable from this repo:

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q                  # unit tests pass
```

Re-render all paper figures from committed trajectories (no API needed):

```bash
.venv/bin/python scripts/make_three_times_figure.py
.venv/bin/python scripts/make_killer_figure.py
.venv/bin/python scripts/make_calibration_figure.py
.venv/bin/python scripts/make_epsilon_panel_figure.py
.venv/bin/python scripts/make_hcast_p12_figure.py
.venv/bin/python scripts/make_a1_positive_figure.py
.venv/bin/python scripts/make_agentic_frontier_figure.py
.venv/bin/python scripts/make_theorem_arc_figure.py
```

Re-run a single agent on ChronoBench (requires an `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`):

```bash
.venv/bin/python scripts/run_pilot.py \
    --backend openai --model gpt-5.1 \
    --capability T1.1,T2.3,T3.1 \
    --setting no_injection,with_injection \
    --count 30 --output-dir my-results
```

For the lab GPU work (vLLM, Qwen, DeepSeek-R1, A.1 LoRA training): the SSH details are in `OPEN_SOURCE_SERVER_RUNBOOK.md`. **Server credentials are not committed to git.** Ask Justin when he returns or check with Yue Zhao.

---

## 7. What is open right now

Everything Paper 1 needs to ship to arXiv is **done**. The state below is what is open in the broader programme.

- [ ] **arXiv submission of Paper 1.** Justin will do this on return. If a co-author wants to submit earlier, the upload package is `paper1/augustine_overleaf.zip` (PDF version `paper1/augustine_problem_v8_dual_scale.pdf`). arXiv categories: `cs.AI` primary, `cs.LG` secondary, `cs.CL` tertiary.
- [ ] **Paper 2 (ChronoStack) draft.** Not started. Scope: constructive installation routes — loss extensions, wall-clock tools, scaffolding, architectural primitives. The A.1 toy positive control (in `paper2_chronostack/toy_a1/`) is the first proof of concept.
- [ ] **Paper 3 (Agentic Frontier) experiments E6–E10.** Scoped in `PAPER3_SCOPE.md` and in Paper 1 Appendix E. None run yet. Estimated cost ~$1{,}430 + 30 GPU-hours total.
- [ ] **Reviewer-anticipated experiments** (none are blocking Paper 1):
  - Paraphrase robustness on T3.1 (~$20 API)
  - Cross-language T3.1 on the self-hosted Qwen (no API)
  - Spatial pilot E6 mini on SWE-Bench Lite (~$80 API)
  - Human baseline on ChronoBench ($200 + IRB; deferred indefinitely)
- [ ] **Within-trajectory drift measurement (P8/P9).** Our single-step protocol cannot measure within-trajectory drift directly; a multi-step harness is on the Paper 3 instrumentation list (E8). The cross-trajectory proxy is reported as an honest negative in §6 of Paper 1.

---

## 8. The framework's pre-registered predictions

Twelve predictions, all logged in `OSF_PREREGISTRATION.md` and locked to commit `a6f20c3`:

| ID | Status |
|---|---|
| P1a / P1b-T1.1 / P1b-T2.3 / P1b-T3.1 | confirmed |
| P2 reasoning heterogeneity | confirmed (3 reasoning models) |
| P3 native $\alpha \approx 0$ | confirmed |
| P4 CAR$(B)$ saturation | confirmed |
| P5 prospective L3 | confirmed |
| P6$'$ tier-stratified injection | confirmed |
| P7 Sonnet 4.6 lowest $\varepsilon$ | confirmed |
| P8 within-trajectory drift | deferred (cross-trajectory proxy refutes the direction; honest negative reported) |
| P9 within-trajectory CAR decline | deferred |
| P10 CUH causal direction | Paper 2 |
| P11 Calibration Catastrophe | confirmed |
| P12 Agentic Timeline slope | qualitatively confirmed on METR HCAST |
| P13 Agentic Frontier | Paper 3 |

Four falsification criteria (F1–F4) are written into Paper 1 §11.

---

## 9. The data

About 4{,}000 committed trajectory JSONs across `pilot-results/`, `e1-results/`, `e2-results/`, `e3-results/`, `e5-results/`. Each JSON has the system prompt, user prompt, per-step LLM responses with timestamps, response metadata (model id, token counts, finish reason), and parser outputs. Total dataset ~600 MB.

Aggregate metrics: `pilot-results/metrics.csv`, `pilot-results/epsilon.csv`, `e1-results/e1-metrics.csv`, `e2-results/metrics.csv`, `e3-results/metrics.csv`, `e5-results/metrics.csv`.

A.1 toy positive control results: `paper2_chronostack/toy_a1/a1_summary.json` (1.5B) and `a1_7b_summary.json` (7B), plus per-trajectory `rows.jsonl`.

---

## 10. Who to ask

- **Justin (Aojie Yuan)** — primary author, back in 6 days. Most context lives in his head. Reach via USC email `aojieyua@usc.edu`.
- **Yue Zhao** — advisor at USC, paper co-author. Has high-level context on the framework but not on the day-to-day experimental detail.
- **The lab server** — `haiyuez@10.136.20.188`. Yue Zhao's lab cluster. Used for OSS model serving (vLLM Qwen / DeepSeek-R1) and for the A.1 LoRA training. **Credentials not in this repo.** Ask Justin or Yue Zhao.

---

## 11. House style

- Voice in the paper: declarative, terse, no AI tics. No "Furthermore", "Moreover", "It is important to note", "we observe that" etc. Each section ends with a sentence that earns the close.
- Math: macros in `notation.tex`. Use `\twall, \tstep, \tself, \parkinson, \CAR, \confab, \cce, \ccestar` etc.
- Cites: full author lists in `paper1/arxiv-v0/bib/refs.bib`. Concurrent work is `garikaparthi2026canllmstime`, `ma2026timelymachine`, `cheng2025temporallyblind`, `goel2025chronocept`, `kwa2025metrhorizons`.
- Commit messages: descriptive multi-line with section-by-section breakdown when changing the paper. Sign off with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` if Claude Code assisted.

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **Augustine Problem** | The policy's failure to enforce the implicit identity linking the Three Times. |
| **Three Times** | $\tau_{\mathrm{wall}}$ (external), $\tau_{\mathrm{step}}$ (internal), $\tau_{\mathrm{self}}$ (narrated). |
| **CIT (Theorem 1)** | Chronoception Impossibility Theorem: token-only loss has no wall-clock gradient. |
| **Reverse-Scaling Theorem (Theorem 2)** | Under CIT, $\|\rho\|$ is monotone non-decreasing in reasoning-token expansion. |
| **SIT (Theorem 3)** | Spatiotemporal Impossibility Theorem: CIT generalised to any external metric. |
| **L1 / L2 / L3** | Three named empirical laws on the $\tau_{\mathrm{wall}}, \tau_{\mathrm{step}}, \tau_{\mathrm{self}}$ axes. |
| **CAR** | Clock-Adherence Ratio $= \tau_{\mathrm{wall}}^* / B$. |
| **$\rho$** | Confabulation ratio $= \log_{10}(\tau_{\mathrm{self}}/\tau_{\mathrm{wall}})$. |
| **$\varepsilon$** | Aggregate chronoceptive calibration error. Augustine threshold $\varepsilon^* = 0.20$. |
| **Injection Tell** | Closed-lab harnesses inject wall-clock into the system prompt; we audit the practice across 11 harnesses. |
| **Agentic Timeline / Frontier** | The deployment bound: $T_{\max} \propto 1/\varepsilon$; joint $(T,S)$ generalisation is $T_{\max} \cdot S_{\max} \leq C/\varepsilon_{ST}$. |
| **ChronoStack** | Paper 2: constructive routes to install chronoception. |
| **A.1 toy positive control** | The 60-second LoRA SFT existence proof of CIT's converse on T3.1. |

Welcome aboard.
