# Position Note — Section Outline (v0)

**Working title**: *The Augustine Problem: A Position on Temporal Cognition in LLM Agents*

**Target**: 6–8 pages, ICML position track / COLM short / arXiv preprint

**Source of truth**: `../FRAMING.md` v1.0 (all definitions, laws, predictions derived from there)

---

## Document structure

| § | Section | Pages | Source |
|---|---|---|---|
| 1 | Introduction | 1.0 | this file §1 |
| 2 | Token-Time vs Wall-Clock: A Structural Diagnosis | 1.0 | FRAMING §3 |
| 3 | The Three Times | 1.0 | FRAMING §2 |
| 4 | Three Laws of Agentic Temporal Failure | 1.5 | FRAMING §5 |
| 5 | The Chronoception Upstream Hypothesis | 0.5 | FRAMING §6 |
| 6 | Motivating Pilot Evidence | 1.0 | new, 5-model pilot |
| 7 | Pre-registered Predictions | 0.5 | FRAMING §9 |
| 8 | Implications for Evaluation, Training, and Agency | 0.75 | FRAMING §8 |
| 9 | Related Work | 0.5 | FRAMING §7 |
| 10 | Conclusion | 0.25 | — |

Total target: ~8 pages plus references.

---

## §1 — Introduction (1.0 page)

**Opening anecdote (1 paragraph)**. A frontier agent given a three-hour budget for a five-minute task does NOT use the three hours — it terminates after four iterations of self-reflection within minutes. Asked retrospectively how long that took, it reports "about an hour" — over-reporting the duration of work that actually completed in minutes. Two failures appear on a single trajectory: the budget went unspent (L2 Step-Clock Conflation) and the duration was misrepresented (L3 Temporal Confabulation). Together they sketch a phenomenon the field has overlooked.

**The structural claim (1 paragraph)**. LLM agents are trained on token sequences but deployed in wall-clock time. No current training stage provides gradient signal that grounds the former into the latter. The agentic turn has therefore inherited a representational gap from the language-modeling era.

**Naming (1 paragraph)**. We call this gap *the Augustine Problem*, after Augustine: "If no one asks me, I know; if I want to explain it, I do not know." LLM agents speak fluently about time without knowing what it is.

**Framework preview (1 paragraph)**. We decompose the failure into three ontologically distinct projections of a trajectory — wall-clock time τ_wall, step time τ_step, and self-narrated time τ_self — and we collapse the three resulting failure modes into a single chronoceptive calibration error ε. We name three empirical laws, one per axis: Agentic Parkinson's Law, Step-Clock Conflation, and Temporal Confabulation.

**Position (1 paragraph)**. We argue that ε is causally upstream of long-horizon agent failure — that the field's current preoccupation with reasoning and test-time compute, *which expand token-time without grounding wall-clock time*, is fighting the wrong battle. We pre-register four falsifiable predictions.

**Contributions list (bulleted)**.
- A formal framework for agent temporal cognition (FRAMING §1–§4).
- Three named empirical laws with quantitative metrics (L1: α, L2: CAR, L3: ρ).
- A single scalar ε aggregating chronoceptive failure.
- The Chronoception Upstream Hypothesis as a falsifiable causal claim.
- Four pre-registered predictions, including the reasoning-models-confabulate-more counter-intuitive bet.

---

## §2 — Token-Time vs Wall-Clock: A Structural Diagnosis (1.0 page)

- The two regimes (training vs deployment) defined explicitly.
- Table mapping training-time properties to deployment-time obligations (a refined version of the table in FRAMING §3).
- Why every current training stage (pre-train, SFT, RLHF, RLVR, reasoning training) operates in token-time.
- Why test-time compute *amplifies* the gap rather than closing it.
- The "just inject a clock" rebuttal and why it fails (forward reference to Prediction P1).

---

## §3 — The Three Times (1.0 page)

- Formal definitions of τ_wall, τ_step, τ_self (from FRAMING §2).
- The implicit identity a chronoceptively grounded agent ought to enforce.
- Why three (not two, not five): each axis has an independent epistemic source.
- Figure 1: the three projections diagrammed as orthogonal axes; the implicit identity as a constraint surface; chronoceptive failure as drift away from the surface.
- Auxiliary times (τ_user, τ_token, τ_reason) and why Paper 1 brackets them.

---

## §4 — Three Laws of Agentic Temporal Failure (1.5 pages)

For each law:
- Definition of the metric (α, CAR, ρ).
- The empirical claim, stated as a quantitative bet.
- A motivating example from the pilot.
- Visualization sketch.

End with §4.4 — the central scalar ε and its analogy to perplexity / FID.

End with §4.5 — the structural symmetry table (three axes × three laws × three metrics) as the framework's aesthetic anchor.

---

## §5 — The Chronoception Upstream Hypothesis (0.5 page)

- Formal statement: ∂L/∂ε < 0, causally.
- Operational test: matched-baseline intervention with chronoceptive scaffolding.
- Why this is the load-bearing claim that distinguishes a position paper from a vocabulary contribution.
- Forward reference to ChronoStack (Paper 2) as the intervention vehicle.

---

## §6 — Motivating Pilot Evidence (1.0 page)

The pilot is structured to make the Injection Tell (FRAMING §3.1) the section's organizing principle. Every chart pairs **Setting A (no-injection)** and **Setting B (with-injection)** for the same model panel and the same task. The reader's takeaway is not "models fail at time" but the much sharper "injection closes T1.1 and leaves everything else untouched."

- Pilot setup: 5 models (GPT-4o, Claude 4 Sonnet, Gemini 2 Pro, o3-mini, Qwen2.5-7B), 4 sub-capabilities (T1.1, T1.3, T2.3, T3.1), ~50 instances per sub-capability, run twice — once per setting.
- **Figure 2 (the headline)** — A grouped bar chart of pass rate per model per setting per sub-capability. The shape we predict and expect to see: T1.1 jumps from low to ~95% under injection; T1.3, T2.3, T3.1 do not move. The chart visualizes Prediction P1a / P1b directly.
- **Figure 3 — Agentic Parkinson's Law (L1)** — α as a function of wall-clock budget B ∈ {15 min, 1 h, 3 h, 12 h}, shown twice (Setting A vs B). Hypothesis: identical curves.
- **Figure 4 — Step-Clock decoupling (L2)** — CAR(B) curves, two settings overlaid. Hypothesis: identical, both trending to 0.
- **Figure 5 — Temporal Confabulation (L3)** — ρ histograms for base vs reasoning models, both settings. Hypothesis: reasoning shifts ρ rightward independently of injection.
- Caveat: pilot is illustrative, not the full empirical sweep (which appears in the companion ChronoBench paper).

Figure 2 is the single most important diagram in the position note: it converts a structural claim into a visible bar chart. A reader who only sees Figure 2 should still get the position.

---

## §7 — Pre-registered Predictions (0.5 page)

Verbatim from FRAMING §9: P1, P2, P3, P4.

Single sentence at the top: "We commit to the following predictions before large-scale empirical work; failures will be reported."

---

## §8 — Implications for Evaluation, Training, and Agency (0.75 page)

Three short sub-sections:
- §8.1 Evaluation — current benchmarks systematically under-report agent failure by being blind to time.
- §8.2 Training — chronoception requires a training-stage intervention, not a prompting one (forward to ChronoStack).
- §8.3 Agency — temporally ungrounded actions cannot satisfy a serious definition of agency. We borrow the Heideggerian framing (FRAMING §7) to make the philosophical case briefly.

---

## §9 — Related Work (0.5 page)

Four buckets:
- Textual temporal reasoning (TempReason, TimeQA, TimeBench) — different problem.
- Agent benchmarks (AgentBench, WebArena, SWE-Bench, GAIA, OSWorld) — silent on time.
- Test-time compute and reasoning training (o-series, R1, DeepSeek-V3) — relevant but in token-time; we argue they exacerbate L3.
- Human chronoception (Wittmann, Eagleman) — conceptual ancestor; we borrow vocabulary.

---

## §10 — Conclusion (0.25 page)

The Augustine Problem is not a curiosity to be patched. It is a structural condition of training language models on tokens and deploying them as agents in time. We have named the gap, decomposed it, predicted four empirical signatures of it, and committed to a causal claim about its consequences. The companion works — ChronoBench (diagnosis at scale) and ChronoStack (a training framework for repair) — operationalize the position.

---

## Figures (to be produced in Phase 2)

1. **Three Times diagram** — orthogonal axes, implicit identity surface, frontier-agent drift.
2. **Injection Tell bar chart (headline)** — pass rate per model per setting per sub-capability; T1.1 lifts, the rest do not.
3. **Parkinson curve** — α vs B, per model, two settings overlaid.
4. **Step-clock decoupling** — CAR(B), two settings overlaid; both trending to 0.
5. **Confabulation histogram** — ρ distribution, base vs reasoning models, two settings overlaid.
6. **Reverse-scaling on L3** — ρ as function of reasoning-budget setting, single model family.

---

## Open writing-time decisions (resolve before drafting prose)

1. Submit as ICML 2026 position track (deadline late Jan 2027 — too late for this cycle, hence COLM 2026 or arXiv-only) OR as arXiv preprint only with eventual rollup into the Paper 1 ChronoBench submission. **Recommendation**: arXiv-only Phase 1, fold into Paper 1 later.
2. Include §6 pilot evidence (recommended; raises position note above pure speculation) OR keep position-only (faster). **Recommendation**: include 5-model pilot; ~2 weeks of work.
3. Single-author or co-author with Yue Zhao on the position note? Separate decision; consult Yue.
