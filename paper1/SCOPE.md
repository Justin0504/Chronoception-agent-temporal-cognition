# Paper 1 — Scope

**Working title**: *The Augustine Problem: Evaluating Whether LLM Agents Can Perceive Their Own Time*
**Project**: Chronoception — Agent Temporal Cognition
**Status**: v0 (2026-05-29)
**Parent**: [`../FRAMING.md`](../FRAMING.md) v1.2

This document defines the scope, claims, and epistemic register of **Paper 1**, the empirical diagnostic paper of the project. It is a strict subset of the research programme defined in the root `FRAMING.md`, with claim strength reduced where evidence is not yet present and with components that depend on Paper 2 explicitly deferred.

The goal of this scope document is to make Paper 1 a **focused empirical contribution**, not a research programme manifesto. The full programme remains available to readers in the position note and root `FRAMING.md`.

---

## 1. What Paper 1 Claims

Paper 1 makes four contributions, with the following claim strengths:

1. **A formal ontology**: agent trajectories admit three ontologically distinct projections of time — wall-clock time $\tau_{\text{wall}}$, step time $\tau_{\text{step}}$, and self-narrated time $\tau_{\text{self}}$ — linked by an implicit identity that a chronoceptively grounded agent ought to enforce.

2. **The Augustine Problem**: foundation-model agents do not, in general, enforce this identity. We define the problem formally, motivate it with examples, and present evidence that the three projections drift independently in current frontier and open-source agents.

3. **ChronoBench**: a diagnostic benchmark of ~4000 instances across nine sub-capabilities (three per axis), evaluated on ≥25 frontier and open-source models under two settings (no-injection and with-injection). All data, code, and results are released openly.

4. **The chronoceptive calibration error $\varepsilon$**: a single weighted aggregate of the three axes that supports cross-model comparison. We report $\varepsilon$ for every model in the panel.

The paper's primary empirical findings are:

- **L2 (Step-Clock Conflation)**: when given wall-clock budgets, frontier agents silently terminate after a model-specific step count $N_A$ rather than honoring the wall-clock; the Clock-Adherence Ratio CAR$(B) \to 0$ as $B$ grows. **Stable across models and budgets**; this is Paper 1's load-bearing result.

- **L3 (Temporal Confabulation)**: across code-generation, document-authoring, and presentation tasks, frontier agents over-report their own work duration; the confabulation ratio $\rho$ is positive in expectation, with reasoning-tuned models exhibiting larger $\rho$ than matched non-reasoning baselines. **Stable across families**; this is Paper 1's second primary result.

- **Injection Tell** (empirical): wall-clock injection raises clock-awareness pass rate to high levels but leaves the execution and self-narration sub-capabilities (T1.3, T2.3, T3.1) effectively unchanged. Information about time, supplied at the prompt, does not constitute a representation of time.

## 2. What Paper 1 Does Not Claim

The following components of the research programme are **deferred**:

- **The Chronoception Upstream Hypothesis (CUH)** — that $\varepsilon$ is *causally* upstream of long-horizon task success. Paper 1 reports the *correlation* on $\geq 3$ long-horizon benchmarks (Prediction P4). The causal claim is forwarded to Paper 2, which provides the matched-baseline intervention required to test it.

- **ChronoStack** — the four-component training and inference-time framework for closing $\varepsilon$. Entire scope of Paper 2.

- **The Augustine threshold $\varepsilon^* = 0.20$** as a qualifying line. Paper 1 reports $\varepsilon$ for each model without categorizing models as "chronoceptively grounded" or "blind." The threshold is discussed in the appendix as one possible operationalization of $\varepsilon$ for downstream use, contingent on empirical distribution observed.

- **In-principle insufficiency of token-loss training**. Paper 1 presents this as a *hypothesis* motivated by the absence of wall-clock signal in standard losses, not as a theorem or impossibility result. The full structural argument remains in the position note and the research programme document.

- **The Reverse-Scaling Theorem**. Paper 1 reports the empirical observation that $\rho$ is non-decreasing in the reasoning budget on the model families tested, and offers a structural explanation in the discussion. It is not labeled a theorem.

## 3. L1 — Demoted to Phenomenon

The research programme treats **Agentic Parkinson's Law** (L1) as a named law on par with L2 and L3. In Paper 1, L1 is **demoted to a hypothesis-level phenomenon** for the following reasons:

- L1's predicted range $\alpha \in [0.5, 0.9]$ is the most empirically uncertain of the three. Anecdotal reports suggest both budget-filling and early-termination behaviors depending on the task and budget regime.
- L1 and L2 describe complementary regimes (sub-transition vs super-transition $B^*$), which adds theoretical complexity to a paper whose primary contribution is empirical.
- Demoting L1 in Paper 1 does not weaken the framework — L2 and L3 alone constitute a rigorous empirical case for the Augustine Problem.

**Paper 1's treatment of L1**:

- Refer to the phenomenon as *budget inflation* or *Parkinson-like behavior*, not as a Law (lowercase).
- Report $\alpha$ as a measured quantity, alongside CAR and $\rho$, without elevating it.
- Include a regime-analysis subsection (the $B^*$ transition) as a supplementary finding rather than a structural pillar.
- Reserve the term *Agentic Parkinson's Law* for the position note and root framing, where the full programmatic claim is made.

## 4. Epistemic Register

Paper 1 uses the following register conventions throughout:

| In root FRAMING.md (programme) | In Paper 1 (empirical paper) |
|---|---|
| "Chronoception cannot be learned; it must be installed." | "We hypothesize, on the basis of the absence of wall-clock signal in current training losses, that chronoception is unlikely to emerge from token-only training. We do not attempt to prove this; we report the failure mode and forward the structural argument to the position note." |
| "Decisive non-experimental evidence." | "Suggestive evidence consistent with the framework." |
| "Reverse-Scaling Theorem (informal)." | "We observe non-decreasing $\rho$ in reasoning-tuned models; we offer a structural explanation in §X." |
| "Structural causal claim grounded in single-turn observability." | "We test the correlation between $\varepsilon$ and long-horizon success; the causal direction is addressed in the companion work." |
| "Augustine threshold $\varepsilon^* = 0.20$; no current agent satisfies it." | "We report $\varepsilon$ for each model; in the discussion we explore one operationalization of a threshold for downstream use." |

These are not concessions of correctness; they are register adjustments appropriate to a paper that reports empirical measurements without a controlled intervention.

## 5. The $\tau_{\text{self}}$ Parser — Annotation Protocol

L3 depends on the parser $\Pi$ that extracts self-reported durations from agent outputs. Paper 1 includes a full annotation protocol, separately documented in [`annotation-protocol.md`](annotation-protocol.md):

- Operational definitions of *prospective* (forward-looking) vs *retrospective* (backward-looking) duration claims, with only retrospective claims feeding $\tau_{\text{self}}$ in L3.
- The parser stack (regex pre-filter + LLM-as-judge ensemble), with majority-vote ensembling reported.
- A human-annotated validation subset (≥200 trajectories) with precision, recall, and inter-annotator agreement (Cohen's $\kappa$) reported.
- An ablation comparing regex-only, LLM-only, ensemble, and human-only parsers, with $\rho$ measured under each — to demonstrate that L3's main finding does not depend on parser choice.

Without this protocol, L3 is contestable on measurement grounds. With it, L3 stands on the same evidential basis as the rest of the paper.

## 6. Predictions Carried Into Paper 1

From the six pre-registered predictions in root `FRAMING.md` §9, Paper 1 commits to the following subset:

| Programme ID | Paper 1 statement |
|---|---|
| **P1a** | Setting B raises T1.1 pass rate to $\geq 95\%$ while Setting A leaves it below $40\%$ for the same model panel. |
| **P1b** | Setting B leaves T1.3, T2.3, T3.1 statistically unchanged from Setting A (within $\pm 5$ pp on pass rate, $\pm 0.05$ on the corresponding metric). |
| **P2** | Reasoning-tuned models exhibit $\rho > 0$ strictly larger than matched non-reasoning baselines, in $\geq 3$ task families. |
| **P4** | $\varepsilon(A)$ correlates with $L(A)$ at Pearson $r \leq -0.5$ over a model panel of $\geq 25$, across $\geq 3$ long-horizon benchmarks. |

Predictions P2′ (Reverse-Scaling on future methods), P3 (ChronoStack-induced $L$ gain), and P5 (Augustine threshold null result) **do not** appear as Paper 1 predictions. P2′ is reported as a structural explanation in the discussion; P3 is the subject of Paper 2; P5 is treated as a downstream-use illustration in the appendix.

## 7. Outline of Paper 1's Argument

The paper is structured around three claims:

1. **Definitional**: the three times exist as distinct, measurable projections, and frontier agents fail to enforce their implicit identity. (§3 of paper)
2. **Empirical, primary**: L2 and L3 hold across a $\geq 25$ model panel, with quantitative magnitudes reported. (§5–§6 of paper)
3. **Diagnostic of the gap**: wall-clock injection closes the most superficial sub-capability and leaves the load-bearing ones unchanged. (§7 of paper, supporting P1)

These three claims are sufficient to establish the Augustine Problem as a measurable phenomenon worth the field's attention, **without** requiring the full structural argument or the causal upstream claim, both of which depend on companion work.

## 8. Document Rules

1. Edits to Paper 1's claim set must preserve the strict-subset relationship with `../FRAMING.md`. Paper 1 may *quote* programme claims with softened register but may not *contradict* them.
2. New terminology may not be introduced in Paper 1 without first updating `../FRAMING.md` §11.
3. If Paper 1's empirical results contradict a programme claim, the programme document is revised (with a changelog entry), not the paper.

## Changelog

- **v0 (2026-05-29)** — Initial scope document. Establishes the four contributions, the L1 demotion, the deferral of CUH and the Augustine threshold, the epistemic register conventions, and the link to the annotation protocol.
