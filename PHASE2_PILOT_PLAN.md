# Phase 2 — Pilot Plan and Work Split

**Status**: v1 (2026-05-29, optimized)
**Owners**: Justin (USC) + collaborator (TBD)
**Parent**: [`FRAMING.md`](FRAMING.md) v1.5 · [`paper1/SCOPE.md`](paper1/SCOPE.md) · [`RELATED_WORK.md`](RELATED_WORK.md)
**Goal**: Stake the framing on arXiv within 3 weeks (v0 release) and reach a publication-quality empirical pilot within 6 weeks (v1 release).

This document is the working coordination document between Justin and the collaborator. Updates are pushed to `main` as plans evolve. v1 supersedes v0 by introducing a staged release strategy, cost-aware execution sequencing, prediction-priority ordering, and explicit prediction-failure responses.

---

## 0. Strategic Decision — Staged Release

The v0 plan targeted a single 6-week arXiv submission. v1 splits this into two releases. The reason is **concurrent-paper urgency**: Garikaparthi (2604.00010) is one experiment away from claiming the L3 reasoning wedge, and the framework's naming priority depends on arXiv submission, not on the completeness of any specific empirical result.

### v0 arXiv release (Week 3 target — **flag-planting**)

A focused 6-page preprint anchored on:

- The full FRAMING (Three Times, Augustine Problem, Three Laws, ε, Injection Tell, CIT, CUH).
- **Atlas v0**: $\geq 10$ closed-lab harnesses audited (Role B can finish this in Week 1).
- **Pilot v0**: 3 cheap-tier models × 3 capabilities × 2 settings × 30 instances = 540 trajectories on the headline laws — sufficient to draw Figures 2 (L2), 3 (L3 baseline), and 4 (Injection-Tell bar chart).
- Predictions P1a, P1b, P6 reported. P2 reasoning wedge deferred to v1.

**Outcome**: names locked publicly with timestamped arXiv ID. Subsequent concurrent work must cite.

### v1 arXiv release (Week 6 target — **full pilot**)

A 10-page expanded preprint replacing v0, anchored on:

- The full v0 contents.
- **Pilot v1**: adds 2 reasoning models (o3, DeepSeek-V3.2) on T3.1 only — supplies the P2 reasoning-confabulation wedge against Garikaparthi.
- **Parser validation**: 200-trajectory human-annotated subset with target Cohen's $\kappa \geq 0.75$.
- **Parser ablation**: 4-config table (R-only, J-only, Ensemble, Human).
- Predictions P2 added. P4 (long-horizon correlation) noted as future work for ICLR submission.

**Outcome**: ready submission to ICLR 2027 (deadline 2026-09-25) with empirical anchoring.

---

## 1. Pilot Scope (Optimized)

The full pilot still delivers two empirical contributions. The optimization is in **execution sequence**, not in the artifacts themselves.

### Contribution A — ChronoBench Pilot Run

| Tier | Models | Capabilities | Settings | Instances | Trajectories | Cost band |
|---|---|---|---|---|---|---|
| **Cheap-tier** (v0) | GPT-4o, Claude 4.6 Sonnet, Gemini 2.5 Flash | T1.1, T2.3, T3.1 | A, B | 30 | 540 | ~$30 |
| **Frontier-tier** (v0 → v1) | GPT-5.1, Claude 4.7 Opus, Gemini 2.5 Pro | T1.1, T2.3, T3.1 | A, B | 50 | 900 | ~$100 |
| **Reasoning wedge** (v1) | o3, DeepSeek-V3.2 | T3.1 only | A, B | 100 | 400 | ~$80 |

**Total trajectories at v1 completion**: 1,840.
**Total API budget estimate**: ~$210 (well under the $500 cap).

**Rationale for the tiering**:
- Cheap-tier models are run **first** because Setting A vs Setting B on T1.1 should produce the Injection-Tell figure (Fig. 4) within Week 2 — that's the pilot's most visceral diagram.
- Reasoning models are run **only on T3.1** because P2 lives on the τ_self axis; running reasoning models on T1.1 and T2.3 burns API budget on capabilities where the reasoning wedge has no theoretical claim.
- Reasoning models get **100 instances** (not 50) on T3.1 because the asymmetry split (retrospective vs prospective per §5.6) doubles the analysis surface.

### Contribution B — Closed-Lab Injection Audit (Injection Atlas)

| Tier | Harnesses | When | Owner |
|---|---|---|---|
| **Atlas v0** (for arXiv v0) | 10 harnesses, full M1/M2/M3 audit | Week 1 | Role B |
| **Atlas v1** (for arXiv v1) | +4 harnesses (Atlas v0 = 14 total), drift re-audit | Weeks 4–5 | Role B |

Template, methodology, 14 pre-populated harness rows, evidence-directory skeleton already shipped: [`paper1/injection-atlas.md`](paper1/injection-atlas.md).

---

## 2. Optimized Timeline

**Total: 6 weeks**, with arXiv v0 at end of W3, full v1 at end of W6, and 5-day buffer.

### Week 1 (2026-05-30 → 2026-06-05) — *Foundation already done; execute v0 Atlas*

Most W1 infrastructure work in v0 is already in repo:

- ✅ Task instance generators (T1.1, T2.3, T3.1 × 50) — [`chronoception/bench/tasks/instances.py`](chronoception/bench/tasks/instances.py)
- ✅ Runner with Setting A/B (FRAMING §3.1) — [`chronoception/bench/eval/runner.py`](chronoception/bench/eval/runner.py)
- ✅ OpenAI / Anthropic / Google backends — [`chronoception/bench/eval/agents/`](chronoception/bench/eval/agents/)
- ✅ Pilot runner CLI with resume — [`scripts/run_pilot.py`](scripts/run_pilot.py)
- ✅ τ_self Stage 1 regex parser — [`chronoception/bench/parsers/tau_self.py`](chronoception/bench/parsers/tau_self.py)
- ✅ Atlas template — [`paper1/injection-atlas.md`](paper1/injection-atlas.md)

**W1 active work**:
- Role B: complete Atlas v0 (audit 10 harnesses) — full M1/M2/M3 ratings + evidence transcripts.
- Role A: set up API keys, smoke-test each backend with `scripts/run_pilot.py --backend X --count 1`, build `scripts/compute_metrics.py` (read pilot-results/, compute α/CAR/ρ/ε per model/setting, output CSV).

**W1 sync goal**: by Sunday 2026-06-05, both workstreams ready for production pilot runs.

### Week 2 (2026-06-06 → 2026-06-12) — *Cheap-tier pilot for arXiv v0*

- Role A: run cheap-tier (GPT-4o, Claude 4.6 Sonnet, Gemini 2.5 Flash) × 3 capabilities × 2 settings × 30 instances = **540 trajectories**, total ~30 minutes wall-clock per model, total ~$30 budget.
- Role A: generate **Figures 2, 3, 4** from cheap-tier results. These are the arXiv v0 figures.
- Role B: τ_self LLM-judge ensemble (Stage 2 parser) implemented — needed to validate the Stage 1 parser used in T3.1 runs.

**W2 sync goal**: by Sunday 2026-06-12, three figures committed under `paper1/figures/` and at least one preliminary observation for each of P1a, P1b.

### Week 3 (2026-06-13 → 2026-06-19) — *arXiv v0 draft + submit*

- Joint: draft Section 1 (Intro), Section 5 (L2 with cheap-tier), Section 6 (L3 with cheap-tier), Section 7 (Injection Tell + Atlas v0).
- Joint: assemble 6-page preprint LaTeX. Source: [`paper1/section-1-introduction.md`](position-note/section-1-introduction.md) → LaTeX. Co-authorship + ordering decided.
- Joint: arXiv submission Friday 2026-06-19.

**W3 sync goal**: arXiv preprint live by EOD 2026-06-19. Names locked publicly.

### Week 4 (2026-06-20 → 2026-06-26) — *Frontier-tier expansion*

- Role A: run frontier-tier (GPT-5.1, Claude 4.7 Opus, Gemini 2.5 Pro) × 3 capabilities × 2 settings × 50 instances = **900 trajectories**, total ~$100 budget.
- Role B: human validation subset preparation — sample 200 trajectories from cheap-tier + frontier-tier T3.1 runs; recruit second annotator.
- Role B: extend Atlas to 14 harnesses (drift-check + 4 new).

**W4 sync goal**: by Sunday 2026-06-26, all frontier-tier figures regenerated with the expanded data and human-validation underway.

### Week 5 (2026-06-27 → 2026-07-03) — *Reasoning wedge + parser validation*

- Role A: run reasoning wedge (o3, DeepSeek-V3.2) on T3.1 only × 2 settings × 100 instances = **400 trajectories**, total ~$80 budget. Headline result: P2 reasoning vs non-reasoning ρ contrast.
- Role B: human validation completion — compute precision, recall, Pearson, Cohen's κ. Target $\kappa \geq 0.75$.
- Role B: parser ablation — run all four configurations on the 200-trajectory subset; report mean ρ per config.

**W5 sync goal**: by Sunday 2026-07-03, P2 figure exists, parser validation metrics meet protocol targets, all artifacts ready for v1 write-up.

### Week 6 (2026-07-04 → 2026-07-10) — *v1 expansion + submit*

- Joint: extend the arXiv v0 preprint to 10 pages with the v1 results (reasoning wedge, parser validation, asymmetry analysis).
- Joint: arXiv v1 replacing v0 by EOD 2026-07-10.

**W6 sync goal**: arXiv v1 live.

### Buffer (2026-07-11 → 2026-07-15) — *5-day slip protection*

If any week ran long, this is where slip is absorbed. If everything is on time, this week is used for ICLR submission preparation (paper1/SCOPE.md scope).

---

## 3. Work Split (Optimized)

### Role A — ChronoBench Workstream

**Owner**: TBD
**Estimated hours**: ~70 across 6 weeks (~12/week with W3 + W6 heavier)

Compared to v0 of this document, hours rose from 60 to 70 because (a) the staged release adds two figure-generation passes (W2 cheap-tier + W4 frontier-tier) and (b) the v1 reasoning wedge adds a third run cycle. The W1 infrastructure work moved into the "already done" column.

**W1**: smoke-test backends; build [`scripts/compute_metrics.py`](scripts/compute_metrics.py) (new); verify Stage 1 parser works on a few echo-generated T3.1 trajectories.

**W2**: cheap-tier pilot (540 trajectories). Generate Figures 2/3/4. Write a 2-page internal observation log.

**W3**: draft Paper 1 §5 (L2) and §6 (L3) prose based on cheap-tier data; co-write the arXiv v0 preprint.

**W4**: frontier-tier pilot (900 trajectories). Re-generate Figures 2/3/4 with expanded data.

**W5**: reasoning wedge pilot (400 trajectories on T3.1 only). Generate Figure 3' (reasoning vs non-reasoning split, the P2 headline).

**W6**: extend Paper 1 §5/§6 prose with v1 data. Co-write the arXiv v1 expansion.

### Role B — Parser + Injection Atlas Workstream

**Owner**: TBD
**Estimated hours**: ~55 across 6 weeks (~9/week with W1 + W5 heavier)

**W1**: Atlas v0 — audit 10 harnesses (M1/M2/M3 + evidence). Commit to [`paper1/injection-atlas.md`](paper1/injection-atlas.md) row-by-row.

**W2**: τ_self LLM-judge ensemble (Stage 2 parser) implementation. Three judges (GPT-4o, Claude 4.6 Sonnet, Gemini 2.5 Flash) with majority-vote.

**W3**: draft Paper 1 §7 (Injection Tell + Atlas v0) prose; co-write the arXiv v0 preprint.

**W4**: prepare 200-trajectory human validation subset; recruit second annotator; pilot the annotation interface.

**W5**: human validation execution (Role B + recruited annotator). Compute κ, precision, recall, Pearson. If $\kappa < 0.75$, revise protocol and re-annotate; otherwise proceed. Parser ablation — 4 configurations on the subset.

**W6**: extend Paper 1 §7 prose with Atlas v1 (14 harnesses) and parser ablation results; co-write the arXiv v1 expansion.

---

## 4. Shared Infrastructure (unchanged from v0)

Same as v0; see git log for the v0 version. Three columns: component / owner / notes.

---

## 5. Compute and Budget (Optimized)

**Total API budget estimate**: ~$210 (target). $500 cap unchanged.

| Tier | Approx cost | When |
|---|---|---|
| Smoke tests | <$5 | W1 |
| Cheap-tier pilot | ~$30 | W2 |
| Frontier-tier pilot | ~$100 | W4 |
| Reasoning wedge | ~$80 | W5 |
| Parser stage 2 ensemble | ~$30 | W2 ongoing + W5 validation |

**Optimization vs v0**: cheap-tier-first sequencing means the Week 2 figure-generation cost is only ~$30, allowing rapid iteration. Reasoning models — the most expensive per token — are confined to T3.1 only, where they're theoretically necessary for the P2 wedge.

Open-weight DeepSeek-V3.2 inference runs on Jetstream2 (free for USC NCSA users); see [`memory/project_usc_ncsa_delta.md`](https://github.com/Justin0504/Chronoception-agent-temporal-cognition) for credentials.

---

## 6. Sync Points (Optimized — concrete agendas)

| When | Format | Concrete agenda |
|---|---|---|
| **Daily** | Async Slack | Yesterday / today / blockers (≤3 sentences each) |
| **Sun W1 EOD** | Live 60 min | Decide: arXiv co-authors, co-author order, target arXiv categories. Verify all backends running. Verify Atlas v0 has 10 harnesses queued. |
| **Sun W2 EOD** | Live 60 min | Review Figures 2/3/4 cheap-tier. Decide: are findings strong enough for arXiv v0? If yes, lock the framing for v0 write-up. If no, identify what needs more data before submission. |
| **Sun W3 EOD** | Live 60 min | arXiv submission. Public sharing: X thread, Hacker News submission, direct email to Garikaparthi / Ma et al. / Cheng et al. with the preprint. |
| **Sun W4 EOD** | Live 60 min | Review frontier-tier figures. Decide: any data anomalies blocking v1 expansion? Atlas v1 progress check. |
| **Sun W5 EOD** | Live 60 min | Review reasoning wedge P2 figure. Review human validation metrics. Decide: any prediction failures requiring framing revision per §8 below? |
| **Sun W6 EOD** | Live 60 min | arXiv v1 submission. Begin ICLR 2027 plan if v1 results are strong; else replan. |

---

## 7. Definition of Done (Staged)

### v0 Definition of Done (Week 3)

1. Atlas v0: $\geq 10$ harnesses audited with all three mechanism columns filled and evidence transcripts committed.
2. Cheap-tier pilot: 540 trajectory JSONs exist under `pilot-results/`, validated by sanity checks.
3. Per-model $\varepsilon$, $\varepsilon_A$, $\varepsilon_B$, and the three law metrics computed and tabulated for the three cheap-tier models.
4. Figures 2, 3, 4 committed under `paper1/figures/` in PDF + PNG.
5. arXiv preprint v0 (6 pages) live on arXiv with a citable ID.
6. Paper 1 §1, §5, §6, §7 prose drafts committed.

### v1 Definition of Done (Week 6)

All v0 criteria, plus:

7. Frontier-tier pilot: 900 trajectory JSONs validated and metrics regenerated.
8. Reasoning wedge: 400 trajectory JSONs validated; P2 figure (reasoning vs non-reasoning ρ) committed.
9. Parser validation: precision $\geq 0.90$, recall $\geq 0.80$, Pearson $\geq 0.95$, Cohen's $\kappa \geq 0.75$ on the 200-trajectory subset.
10. Parser ablation: 4-config table committed.
11. Atlas v1: 14 harnesses; drift re-audit on the original 10.
12. arXiv preprint v1 (10 pages) replacing v0.
13. Release tag `pilot-v1` created.

---

## 8. Prediction-Failure Responses

If a pre-registered prediction lands outside the predicted range, the response is **pre-decided** rather than improvised. This is the value of pre-registration.

| Prediction | Pass criterion | If fails | Framing revision needed |
|---|---|---|---|
| **P1a** (T1.1 jumps to ≥95% under Setting B) | Setting B − Setting A ≥ 0.55 on T1.1 pass rate | Re-examine Setting B operationalization; maybe injection format too weak. Re-run with stronger injection mechanism. | No (likely operational issue) |
| **P1b** (T1.3/T2.3/T3.1 unchanged under injection) | |Setting B − Setting A| ≤ 0.05 on the three metrics | If T2.3 or T3.1 *also* improves >0.1 with injection, the framework's representational claim weakens. Report honestly. | **Yes** — §3.1 Injection Tell weakens; §3 representational argument needs nuance |
| **P2** (reasoning ρ > non-reasoning ρ at matched scale) | Reasoning ρ − non-reasoning ρ ≥ 0.3 on at least 2 model-pair tests | If reasoning models confabulate *less* (P2 reversed), §5.4 Reverse-Scaling Theorem fails. Largest framework hit. | **Yes** — §5.4 Reverse-Scaling Theorem retracted; §5.7 mechanism revised |
| **P4** (ε correlates with L at r ≤ −0.5) | Not tested in pilot; ICLR submission only | N/A in pilot | — |
| **P5** (no agent crosses ε* = 0.20) | Median ε > 0.20 across panel | If some agent crosses, the threshold needs raising or methodology reviewed. | Threshold revisable per §6.1 |
| **P6** (≥80% of harnesses inject wall-clock) | $|\{h : \exists m, M_m(h) = \text{YES}\}|/|H| \geq 0.80$ | If <80%, Injection Tell weakens; check for missed mechanisms before concluding. | Possibly — §3.1 and §5.5 may need to soften from "decisive" |

**Decision authority for revisions**: Justin (framing owner). The collaborator may flag a revision but does not edit FRAMING.md without joint discussion.

---

## 9. Risk Register (Updated)

| Risk | Likelihood | Mitigation |
|---|---|---|
| API budget exceeded | Low (target $210, cap $500) | Cheap-tier first; if over budget, drop one frontier model |
| Parser human-validation κ < 0.75 | Medium | Revise annotation protocol mid-W5; recruit third annotator |
| One model unavailable | Medium | Substitute equivalents (o4-mini ↔ o3; R1 ↔ DeepSeek-V3.2; Sonnet ↔ Haiku) |
| Pilot results contradict P1a/P1b | Low | Report honestly; revise §3.1 Injection Tell strength |
| Pilot results contradict P2 (reasoning wedge) | Low–Medium | Most damaging; report honestly; retract §5.4 Reverse-Scaling Theorem |
| **Garikaparthi v2 with reasoning models drops** | **Medium** | **Mitigation by design**: arXiv v0 by W3 locks names before any concurrent extension |
| Collaborator unavailable >1 week | Medium | Role A and Role B are parallel; recoverable. Justin may take Role B work if needed. |
| Concurrent paper from Anthropic / OpenAI safety teams | Medium | Track recent arXiv listings weekly; if scoop appears, replan |

---

## 10. Communication and Repo Hygiene (unchanged from v0)

Same as v0; see git log for details. Branching, commit messages, sensitive-data handling all unchanged.

---

## 11. Open Items (Updated)

Decide these in W1 kickoff:

- [ ] Confirm collaborator name and assign Role A or Role B.
- [ ] Confirm API budget source with Yue Zhao ($210 target, $500 cap).
- [ ] **Decide arXiv co-author order and acknowledgement of Yue Zhao** (he probably gets author-2 or acknowledgement section; depends on his time investment).
- [ ] Decide annotation tool (Label Studio vs spreadsheet vs custom CLI).
- [ ] Confirm Jetstream2 access for DeepSeek-V3.2 runs.
- [ ] Choose arXiv categories: cs.AI, cs.CL primary; cs.LG secondary.
- [ ] Decide whether to email Garikaparthi / Ma et al. / Cheng et al. with the v0 preprint (likely yes — courtesy + citation insurance).
- [ ] Decide on the title for v0 preprint: shorter punchy ("The Augustine Problem") vs full ("The Augustine Problem: Evaluating Whether LLM Agents Can Perceive Their Own Time")?

---

## Changelog

- **v1 (2026-05-29)** — Optimized. (a) Strategic decision: staged release at W3 (arXiv v0 flag-planting) and W6 (full v1 expansion). (b) Cost-aware execution sequencing: cheap-tier first for headline figures, frontier-tier in W4, reasoning models only on T3.1 in W5. (c) Total API budget reduced from "<$500" to "~$210 target". (d) Sync points have concrete agendas instead of "review and replan". (e) Section 8 Prediction-Failure Responses pre-decides framework revisions per prediction. (f) Risk Register adds the Garikaparthi-v2 concurrent-paper risk and its by-design mitigation. (g) Definition of Done split into v0 (6 criteria, Week 3) and v1 (13 criteria, Week 6). (h) Work hours adjusted (Role A: 60 → 70; Role B: 50 → 55) to reflect two release passes. (i) Open Items list expanded with title selection, courtesy emails, and acknowledgement scope.
- **v0 (2026-05-29)** — Initial plan. Two-workstream split, 6-week timeline, 1,500-trajectory grid, $\leq$$500 API budget, end-of-W6 arXiv preprint target.
