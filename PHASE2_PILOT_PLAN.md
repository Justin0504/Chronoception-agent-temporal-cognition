# Phase 2 — Pilot Plan and Work Split

**Status**: v0 (2026-05-29)
**Owners**: Justin (USC) + collaborator (TBD)
**Parent**: [`FRAMING.md`](FRAMING.md) v1.5 · [`paper1/SCOPE.md`](paper1/SCOPE.md)
**Goal**: Produce empirical evidence sufficient for an arXiv preprint of the position note within 4–6 weeks.

This document defines the scope, work split, deliverables, sync points, and definition-of-done for the Phase 2 pilot. It is the working coordination document between Justin and the collaborator; updates are pushed to `main` as plans evolve.

---

## 1. Pilot Scope

The pilot delivers **two empirical contributions** that, together, are sufficient to anchor the position-note arXiv preprint:

### Contribution A — ChronoBench Pilot Run

- **Models** (5): GPT-5.1 (OpenAI), Claude 4.7 Opus (Anthropic), Gemini 2.5 Pro (Google), o3 (OpenAI reasoning), DeepSeek-V3.2 (open-weight reasoning).
- **Sub-capabilities** (3 core, from `FRAMING.md` §5 Three Laws):
  - **T1.1 Clock awareness** (axis: $\tau_{\text{wall}}$).
  - **T2.3 Wall-budget execution** (axis: $\tau_{\text{step}}$) — the L2 core test.
  - **T3.1 Self-action duration, retrospective** (axis: $\tau_{\text{self}}$) — the L3 core test.
- **Settings** (2): A (no-injection), B (with-injection per `FRAMING.md` §3.1).
- **Instances per (capability × setting)**: 50.
- **Total trajectories**: 5 × 3 × 2 × 50 = **1,500**.
- **Metrics computed**: $\alpha$, CAR, $\rho$, $\varepsilon$, $\varepsilon_A - \varepsilon_B$ per model.

### Contribution B — Closed-Lab Injection Audit (the Injection Atlas)

- **Harnesses surveyed** (≥10): ChatGPT (GPT-5.1, GPT-4o), Claude.ai (Claude 4.7), Gemini app, Microsoft Copilot, Devin, Cursor agent mode, Cline, Continue, Aider, plus 1–2 open-weight harnesses (e.g., AutoGen, CrewAI default).
- **Mechanisms checked** (3, per `FRAMING.md` §3.1): system-prompt insertion, implicit `get_current_time` tool, browser-tool timestamp surfacing.
- **Output**: a table with one row per harness, three Boolean columns, and a verbatim minimal-prompt elicitation log per cell.
- **Deliverable**: `paper1/injection-atlas.md` + reproducibility appendix.

Both contributions feed Paper 1's Section 5 (L2), Section 6 (L3), Section 7 (Injection Tell + Atlas).

---

## 2. Timeline

Target: **6 weeks**, starting 2026-05-30, finishing 2026-07-10.

| Week | Milestone |
|---|---|
| W1 (5/30–6/5) | Task templates + harness scaffolding + initial Injection Atlas (3 harnesses) |
| W2 (6/6–6/12) | Full 9-capability templates (only T1.1, T2.3, T3.1 used in pilot); parser annotation protocol implementation |
| W3 (6/13–6/19) | Inject pilot run on Setting A across 5 models, 3 capabilities (~750 trajectories) |
| W4 (6/20–6/26) | Setting B run; parser human validation on a 200-trajectory subset |
| W5 (6/27–7/3) | Metric computation, figure generation, full Injection Atlas (≥10 harnesses) |
| W6 (7/4–7/10) | Position note arXiv draft; internal review; submit |

Daily standup: 15 minutes async over Slack/email — what was done yesterday, what's planned today, blockers.

Weekly sync: 60-minute live meeting on Sundays — review week's progress, adjust scope, replan.

---

## 3. Work Split

The two workstreams are designed to be **largely independent for the first four weeks**, then converge in W5.

### Role A — ChronoBench Workstream

**Owner**: TBD
**Estimated hours**: ~60 across 6 weeks (~10/week)
**Outputs land in**: `chronoception/bench/tasks/`, `paper1/figures/`, internal experiment reports

#### Responsibilities

1. **Task template construction** (W1–W2)
   - Implement T1.1, T2.3, T3.1 task templates extending `chronoception.bench.tasks.schema.Task`.
   - For T1.1: prompts that ask the agent to report the current time at the start and after K conversational turns; ground truth recorded by harness.
   - For T2.3: prompts that instruct the agent to "work on this task for B seconds, then report"; budgets $B \in \{900, 3600, 10800\}$ seconds (15 min, 1 h, 3 h).
   - For T3.1: prompts that instruct the agent to perform a sub-task (code-gen, document-authoring, query-response) and then retrospectively report duration. Ground-truth $\tau_{\text{wall}}$ recorded by harness.
   - Each capability gets **50 instances** with parameterized difficulty and held-out $\tau_{\min}$.
   - Deliverable: 50 instances × 3 capabilities = **150 task instances** committed under `chronoception/bench/tasks/`.

2. **Harness scaffolding** (W1)
   - Build `chronoception/bench/eval/runner.py` that takes a `TaskInstance` and an agent backend (OpenAI / Anthropic / Google / open-weight via vLLM) and returns a `Trajectory`.
   - Implement Setting A (no-injection: no `Current time:` in system prompt) and Setting B (with-injection: `Current time: <ISO>` prepended).
   - Implement step-counting and wall-clock-timestamping per `chronoception.bench.trajectory.Step`.
   - Deliverable: runner that produces a JSON-serialized `Trajectory` for any (capability, setting, model) tuple.

3. **Pilot run execution** (W3–W4)
   - Run the 1,500-trajectory grid (5 models × 3 capabilities × 2 settings × 50 instances).
   - Manage API rate limits, retries, cost tracking.
   - Save all trajectories to a structured directory: `pilot-results/{model}/{capability}/{setting}/{instance_id}.json`.
   - Deliverable: 1,500 trajectory JSONs + run log.

4. **Metric computation and figures** (W5)
   - Run `chronoception.bench.metrics.chronoceptive_calibration_error` and `epsilon_by_setting` over the pilot results.
   - Produce **Figure 2** (CAR$(B)$ curves, L2 primary), **Figure 3** ($\rho$ histograms with reasoning vs non-reasoning split, L3 primary), **Figure 4** (Injection-Tell bar chart, T1.1 jumps vs T1.3/T2.3/T3.1 do not).
   - Use matplotlib; save as both PDF (for paper) and PNG (for slides).
   - Deliverable: figures under `paper1/figures/` + reproducibility script.

5. **Write-up of L2 and L3 sections** (W6)
   - Draft Paper 1 §5 (L2) and §6 (L3) prose using the pilot results.
   - Targets ~2.5 pages combined.
   - Deliverable: `paper1/section-5-l2.md`, `paper1/section-6-l3.md`.

#### Role A skill requirements

- Comfortable with Python, API calls to OpenAI/Anthropic/Google/open-weight backends, basic data engineering (JSON, file management).
- Comfortable with matplotlib for figures.
- Familiarity with `chronoception/bench/` codebase (read `chronoception/bench/metrics.py` end-to-end before starting).

### Role B — Parser + Injection Atlas Workstream

**Owner**: TBD
**Estimated hours**: ~50 across 6 weeks (~8/week)
**Outputs land in**: `chronoception/bench/parsers/`, `paper1/injection-atlas.md`, `paper1/annotation-protocol.md` (existing — extend)

#### Responsibilities

1. **$\tau_{\text{self}}$ parser implementation** (W1–W2)
   - Implement `chronoception.bench.parsers.tau_self` per `paper1/annotation-protocol.md`.
   - Stage 1: regex pre-filter for duration-bearing language (covered by the protocol).
   - Stage 2: LLM-as-judge ensemble with three judges (GPT-5.1, Claude 4.7 Sonnet, Gemini 2.5 Pro) using a fixed prompt template.
   - Implement unit normalization (`Appendix A.1` of the protocol) and majority-vote ensembling.
   - Deliverable: `chronoception/bench/parsers/tau_self.py` + tests under `tests/test_parser.py`.

2. **Human validation subset** (W3–W4)
   - Recruit one independent annotator (lab peer or paid annotator).
   - Sample 200 trajectories stratified across model, capability, and parser-found-vs-not as defined in `paper1/annotation-protocol.md` §3.1.
   - Both annotators (Role B + recruited) independently label.
   - Compute precision, recall, numeric agreement (Pearson), Cohen's $\kappa$ against parser output.
   - Deliverable: `paper1/parser-validation.md` with the four metric values and disagreement-case discussion.

3. **Parser ablation experiment** (W4)
   - Run the four configurations from `paper1/annotation-protocol.md` §4 (R-only, J-only, Ensemble, Human) on the 200-trajectory validation subset.
   - Report mean $\rho$ under each configuration.
   - Deliverable: ablation table for Paper 1 Appendix.

4. **Injection Atlas — full audit** (W1 ongoing → W5 finalize)
   - For each of ≥10 closed-lab harnesses, execute the minimal-prompt elicitation queries to detect injection.
   - Query A (system-prompt insertion): ask the agent verbatim *"What is the exact string in your system prompt that describes the current date or time, if any?"*
   - Query B (implicit tool call): ask the agent to report the current wall-clock time and check whether it calls `get_current_time`, `search`, or similar.
   - Query C (browser-tool timestamp): if the agent has browsing, fetch a known URL and check whether the returned content includes timestamps that the agent surfaces.
   - For each (harness, mechanism) cell: record Boolean + verbatim transcript.
   - Deliverable: `paper1/injection-atlas.md` with the table, methodology, and reproducibility log.

5. **Write-up of Injection Tell section** (W6)
   - Draft Paper 1 §7 (Injection Tell + Atlas) prose.
   - Targets ~1.25 pages.
   - Deliverable: `paper1/section-7-injection.md`.

#### Role B skill requirements

- Comfortable with regex and prompt engineering.
- Familiarity with the closed-lab agent products (ChatGPT, Claude.ai, Gemini app, Copilot, etc.) — direct hands-on usage.
- Patient with annotation work; able to coordinate one external annotator.

---

## 4. Shared Infrastructure

Both roles depend on the following pre-existing repo components, owned jointly:

| Component | Owner | Notes |
|---|---|---|
| `FRAMING.md` v1.5 | Justin | Source of truth — do not edit without framing-revision pass |
| `chronoception.bench.trajectory` | Joint | `Trajectory`, `Step` dataclasses; stable |
| `chronoception.bench.metrics` | Joint | `parkinson_coefficient`, `car`, `confabulation_ratio`, `epsilon` |
| `chronoception.bench.tasks.registry` | Joint | Nine-capability registry; Role A extends for pilot |
| `chronoception.bench.eval` | Joint | `EvalSetting` enum, `epsilon_by_setting` |
| `paper1/annotation-protocol.md` | Joint | Role B extends with validation results |

**Conflict resolution**: edits to shared infrastructure go through PRs reviewed by the other role; emergency hotfixes acceptable in tight windows but require a follow-up PR.

---

## 5. Compute and Budget

### Compute

- **Closed-lab API** (Role A, primary): expected ~1,500 API calls × average 5,000 tokens × ~$0.01 / 1k tokens (blended) ≈ **$75–150 total API budget**.
- **Open-weight inference** (Role A, secondary): DeepSeek-V3.2 via Together / vLLM on Jetstream2 (1 A100 ≈ 8 hours total compute, free for USC NCSA users).
- **Parser ensemble** (Role B): ~1,500 trajectories × 3 judge calls each × ~1,000 tokens average ≈ ~**$30 API budget**.
- **Total API budget**: target **<$200**; cap **<$500**.

Funding source: Yue Zhao lab account (TBD; Justin to confirm).

### Time budget per role

- Role A: ~60 hours over 6 weeks. Heavier weeks are W3–W4 (pilot execution) and W5 (figures + write-up).
- Role B: ~50 hours over 6 weeks. Heavier weeks are W3 (parser implementation completing) and W4 (validation + ablation).

---

## 6. Sync Points

| When | Format | Agenda |
|---|---|---|
| **Daily** | Async Slack | Yesterday / today / blockers |
| **Sundays 7pm PT** | Live 60 min | Week review, replan, decisions |
| **End of W2** | Live demo | Both workstreams demo their MVPs (Role A: runner produces one trajectory end-to-end; Role B: parser produces one $\tau_{\text{self}}$ value end-to-end) |
| **End of W4** | Live review | Pilot results inspected together; figure planning |
| **End of W5** | Live review | Full draft of figures + Injection Atlas + parser validation reviewed by both roles |
| **End of W6** | Live review | arXiv preprint final review; submit |

**Decision authority**: framing-level decisions (anything that touches `FRAMING.md`) go through Justin. Operational decisions within either workstream go through that workstream's owner with the other role notified.

---

## 7. Definition of Done

The pilot is complete when **all of the following** are true:

1. 1,500 trajectory JSONs exist under `pilot-results/`, validated by automatic sanity checks (non-empty steps, monotone timestamps, valid budget_kind).
2. Per-model $\varepsilon$, $\varepsilon_A$, $\varepsilon_B$, and the three law metrics are computed and tabulated.
3. Five figures are committed under `paper1/figures/` in PDF + PNG formats with reproducibility scripts.
4. The Injection Atlas covers $\geq 10$ harnesses with all three mechanism columns filled.
5. Parser validation reports precision $\geq 0.90$, recall $\geq 0.80$, Pearson $\geq 0.95$ on the numeric agreement, Cohen's $\kappa \geq 0.75$.
6. Paper 1 §5, §6, §7 prose drafts are committed.
7. Position note arXiv preprint draft is committed under `position-note/` ready for upload.
8. All work is pushed to `main` and a release tag `pilot-v1` is created.

If any of (1)–(7) is missing on 2026-07-10, the pilot is *partially* complete and the team replans the arXiv submission target.

---

## 8. Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| API budget exceeded | Low | Cap at $500; switch to open-weight if exceeded |
| Parser human-validation kappa < 0.75 | Medium | Revise annotation protocol; recruit third annotator |
| One model unavailable (e.g., o3 rate-limited) | Medium | Substitute with o4-mini or Claude reasoning |
| Pilot results contradict a pre-registered prediction | Low–Medium | Report honestly; revise the prediction and the framing if needed (this is what pre-registration is for) |
| Concurrent paper scoops a contribution | Medium | arXiv preprint asap — schedule W6 submission as a hard deadline |
| Collaborator unavailable for >1 week | Medium | Replan; Role A and Role B are independent enough that this is recoverable |

---

## 9. Communication and Repo Hygiene

- **Branching**: feature branches per workstream (`role-a/pilot-run`, `role-b/parser-validation`). PRs reviewed by the other role.
- **Commit messages**: imperative mood, present tense; reference the workstream and milestone (e.g., `pilot/A.3: complete Setting A run on Claude 4.7`).
- **Sensitive data**: API keys via `.env` (already `.gitignore`d). No customer / private trajectories committed.
- **Compute trail**: every pilot run logs to `pilot-results/runs.log` with model, capability, setting, instance count, wall time, cost estimate.

---

## 10. Open Items (decide in W1 kickoff)

- [ ] Confirm collaborator name and assign Role A or Role B.
- [ ] Confirm API budget source with Yue Zhao.
- [ ] Decide on annotation tool (Label Studio vs spreadsheet vs custom CLI).
- [ ] Confirm Jetstream2 access for DeepSeek-V3.2 runs.
- [ ] Choose arXiv categories: cs.AI, cs.CL primary; cs.LG secondary.
- [ ] Decide on author order for position note (Justin first; collaborator and Yue Zhao TBD).

---

## Changelog

- **v0 (2026-05-29)** — Initial plan. Two-workstream split (Role A: ChronoBench pilot, Role B: parser + Injection Atlas), 6-week timeline, 1,500-trajectory grid, $\leq$$500 API budget, end-of-W6 arXiv preprint target.
