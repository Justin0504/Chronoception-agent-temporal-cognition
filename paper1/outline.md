# Paper 1 — Section Outline (v0)

**Working title**: *The Augustine Problem: Evaluating Whether LLM Agents Can Perceive Their Own Time*

**Target venue**: ICLR 2027 (deadline ~2026-09-25). Backup: COLM 2027, NeurIPS 2027 D&B.

**Parent scope**: [`SCOPE.md`](SCOPE.md) v0
**Research programme**: [`../FRAMING.md`](../FRAMING.md) v1.2

---

## Document structure

| § | Section | Pages | Source |
|---|---|---|---|
| 1 | Introduction (incl. **Concurrent Work** paragraph) | 1.0 | this file §1 |
| 2 | The Three Times | 0.75 | `../FRAMING.md` §2 |
| 3 | The Augustine Problem | 0.5 | `../FRAMING.md` §3 (softened) |
| 4 | ChronoBench: Tasks, Metrics, Settings | 1.5 | new + `../FRAMING.md` §5 + parser |
| 5 | L2 — Step-Clock Conflation (primary result) | 1.25 | new |
| 6 | L3 — Temporal Confabulation (primary result) | 1.5 | new — **reasoning-model extension foregrounded** |
| 7 | The Injection Tell (empirical) + **the Injection Atlas** | 1.25 | new — §5.5 of `../FRAMING.md` |
| 8 | The Calibration Error $\varepsilon$ and Long-Horizon Correlation | 0.75 | `../FRAMING.md` §4 + new |
| 9 | Discussion | 0.75 | this file §9 |
| 10 | Related Work | 0.75 | `../RELATED_WORK.md` + this file §10 |
| 11 | Limitations | 0.25 | this file §11 |
| 12 | Conclusion | 0.25 | — |

Total target: ~10.5 pages plus references and appendix.

---

## §1 — Introduction (1.0 page)

Opens with a single observation: a frontier agent given a three-hour wall-clock budget for a five-minute task ignores the wall-clock entirely and terminates after four self-reflection rounds. Asked at minute 40 how long it has been working, it answers "a few minutes."

We ask whether this is a pattern, and if so, what its structure is.

**Framing claim**: agent task evaluation has so far measured *whether* tasks complete and *what fraction* of a reference solution is recovered. It has not measured whether agents perceive their own time. We argue that this is a missing axis.

**Concurrent Work paragraph** (∼6 sentences, **before** contributions, to foreground differentiation):

> "Recent work has approached agent temporal behavior from three disconnected angles: (a) wall-clock-aware test-time scaling (Ma et al., 2026 — *Timely Machine*), (b) tool-use temporal blindness (Cheng et al., 2025 — *Temporally Blind*), and (c) duration self-estimation on non-reasoning models (Garikaparthi, 2026). We unify these into a single ontology — the **Three Times** — identify three named laws governing how each axis fails, and supply a quantitative audit of closed-lab harness injection patterns that grounds the Injection Tell argument as a measured industry footprint. The term *chronoception* has recently appeared in a separate LLM context for the temporal validity of facts in retrieval-augmented generation (Goel et al., 2025); we use it in its original sense — perception of one's own work duration — throughout."

**Contributions** (mirrors `SCOPE.md` §1):

1. A three-times ontology distinguishing $\tau_{\text{wall}}, \tau_{\text{step}}, \tau_{\text{self}}$, **unified for the first time including $\tau_{\text{self}}$**.
2. The Augustine Problem: a formal definition of agent failure to enforce the identity linking the three.
3. ChronoBench: a 4000-instance, nine-sub-capability, $\geq 25$-model diagnostic benchmark — **including reasoning-tuned models** — released openly.
4. The chronoceptive calibration error $\varepsilon$ — the first aggregated single-scalar calibration metric across the three axes.
5. The **Closed-Lab Injection Atlas**: a systematic empirical audit of wall-clock injection mechanisms across $\geq 10$ frontier harnesses.

**Primary empirical findings preview**:

- L2: agents conflate wall-clock budgets with step-count termination (inverting the Ma et al. framing).
- L3: agents over-report the duration of their own work, **more so as reasoning budget grows** (extending Garikaparthi).
- Wall-clock injection closes clock-awareness but leaves execution and self-narration failure modes effectively unchanged.
- $\geq 80\%$ of frontier closed-lab harnesses surveyed inject wall-clock time — the Injection Tell as a measured industry footprint.

---

## §2 — The Three Times (0.75 page)

Formal definitions of $\tau_{\text{wall}}, \tau_{\text{step}}, \tau_{\text{self}}$ from `../FRAMING.md` §2, with the implicit identity stated as the chronoceptive constraint. One figure illustrating the three projections of a single trajectory.

---

## §3 — The Augustine Problem (0.5 page)

Augustine epigraph. Formal Definition 3.1 from `../FRAMING.md` §3, softened register: "we say an agent exhibits the Augustine Problem if its policy does not, in measurement, enforce the three-times identity." Explicit acknowledgement that we leave the structural diagnosis (token-time vs wall-clock impedance) to the position note; this paper is empirical.

---

## §4 — ChronoBench (1.5 pages)

- §4.1 Nine sub-capabilities across three axes. Table from `chronoception/bench/tasks/registry.py` plus rationale per cell.
- §4.2 Task construction: prompt templates, $\tau_{\min}$ specification, ground-truth verifier.
- §4.3 Metrics — $\alpha$, CAR, $\rho$, $\varepsilon$ with formulas (from `../FRAMING.md` §4 and §5).
- §4.4 Settings — Setting A (no-injection) and Setting B (with-injection) per `../FRAMING.md` §3.1; how injection is operationalized.
- §4.5 The $\tau_{\text{self}}$ parser — short statement, forward-reference to Appendix A (annotation protocol).

---

## §5 — L2: Step-Clock Conflation (primary result, 1.5 pages)

The paper's load-bearing empirical finding.

- §5.1 Setup: T2.3 — wall-budget execution. Budgets $B \in \{15 \text{min}, 1 \text{h}, 3 \text{h}, 12 \text{h}\}$. 25 models. 5 task families.
- §5.2 **Figure 2** (probably the paper's most important diagram): CAR$(B)$ curves per model, showing the decoupling signature — actual wall-clock $\tau_{\text{wall}}^*$ saturates at a model-specific $N_A \cdot \langle \Delta t \rangle$ regardless of $B$.
- §5.3 $N_A$ table — per-model step-count terminator, stable across task families. Hypothesis-form statement: "$N_A$ is interpretable as a model invariant of step-bound termination behavior."
- §5.4 Setting A vs Setting B for T2.3 — injection does not move CAR meaningfully. Supports the framework's prediction.
- §5.5 Regime analysis — small budgets ($B$ < some threshold) admit budget-filling behavior (L1-like); large budgets admit step-decoupling (L2). Reported as a supplementary finding, not a structural pillar.

---

## §6 — L3: Temporal Confabulation (primary result, 1.5 pages)

- §6.1 Setup: T3.1 — retrospective self-action duration. Tasks where ground-truth $\tau_{\text{wall}}$ is observable to the harness.
- §6.2 **Figure 3**: $\rho$ histogram per model. Frontier models cluster around $\rho \approx +1.5$.
- §6.3 Decomposition by task family — code, document, presentation, query, debugging. Over-reporting is consistent across families though magnitude varies.
- §6.4 **Reasoning models exhibit larger $\rho$** (P2 confirmation, if it holds). Compare matched parameter pairs: o-series vs GPT-4o-class non-reasoning, R1 vs base, etc. Plot $\rho$ as a function of reasoning-budget setting where available.
- §6.5 Setting A vs Setting B for T3.1 — injection does not move $\rho$ meaningfully. Information about time does not constitute honest self-narration.

---

## §7 — The Injection Tell and the Injection Atlas (1.25 pages)

- §7.1 Motivating observation: closed-lab agents appear to know the time because their harnesses inject it. We test whether the model itself benefits from this.
- §7.2 **Figure 4** — headline injection-tell bar chart. Pass rate per model per setting per sub-capability. T1.1 jumps from <40% to >95% under injection; T1.3, T2.3, T3.1 do not move. Visualizes P1a and P1b directly.
- §7.3 **The Injection Atlas (the Closed-Lab Injection Audit)** — a new empirical contribution. Table of $\geq 10$ frontier closed-lab harnesses surveyed for: (a) system-prompt time injection, (b) auto-invoked `get_current_time` tool, (c) browser-tool timestamp surfacing. Granularity and format columns. Methodology: minimal-prompt elicitation protocol with reproducible queries. **Figure 5**: stacked bar chart of injection-mechanism distribution across harnesses.
- §7.4 Differentiation from Cheng et al. (2025): they note harness injection informally as a setup detail; the Injection Atlas formalizes it as a measured industry footprint and elevates the observation to the Injection Tell as an evidential argument.
- §7.5 Discussion: framing-level read of the joint result (Figure 4 + Figure 5) — wall-clock as an input does not constitute wall-clock as a representation, and the universality of injection in industry is implicit acknowledgement of this. The structural argument is in the position note; the intervention is in Paper 2.

---

## §8 — Calibration Error $\varepsilon$ and Long-Horizon Correlation (0.75 page)

- §8.1 Definition of $\varepsilon$ as the aggregated three-axis error.
- §8.2 Per-model $\varepsilon$ on the panel. Distribution and ranking.
- §8.3 **Long-horizon correlation** — Pearson $r$ between $\varepsilon$ and per-model success rate on SWE-Bench Verified, WebArena, GAIA. Report $r$, CI, and scatter plot. Frame as *correlational* finding; the causal claim is addressed in Paper 2.

---

## §9 — Discussion (1.0 page)

- §9.1 Implications for agent evaluation: the field's silence on temporal cognition systematically under-reports failure.
- §9.2 Implications for agent training: reasoning training operates in token-time, which the L3 result suggests is the wrong substrate.
- §9.3 The structural explanation (forward-reference to position note): a brief paragraph naming the impedance-mismatch reading, without claiming it here.
- §9.4 Toward a calibration threshold — one possible operationalization $\varepsilon^* = 0.20$ partitions the panel into two groups; we report the partition for completeness while noting that the choice of threshold is empirical and revisable. (Reads as appendix-grade material.)

---

## §10 — Related Work (0.75 page)

Drawn directly from [`../RELATED_WORK.md`](../RELATED_WORK.md), organized into three subsections.

**§10.1 Concurrent work** (≥3 sentences each, naming the three threats explicitly):

- Garikaparthi (2026) measures duration self-reporting on non-reasoning models. Our $\tau_{\text{self}}$ axis subsumes this; we extend to reasoning-tuned models and find reverse scaling.
- Ma et al. (2026, *Timely Machine*) decouples wall-clock from generation length as an engineering signal. We invert the framing into Agentic Parkinson's Law.
- Cheng et al. (2025, *Temporally Blind*) note harness injection informally; we elevate it to the Injection Tell and supply the Injection Atlas.

**§10.2 Name disambiguation**: Goel et al. (2025, *Chronocept*) use *chronoception* for the temporal validity of facts in RAG; we use it for agent perception of own work duration.

**§10.3 Foundational background**: textual temporal reasoning (TimeBench, TempReason, TimeQA); agent benchmarks (AgentBench, WebArena, SWE-Bench, GAIA, OSWorld) — silent on time; cognitive-science chronoception (Wittmann, Eagleman); Parkinson (1955); METR HCAST (Kwa et al., 2025) — outer envelope vs our internal calibration; inverse-scaling and over-reasoning literature for the Reverse-Scaling Theorem motif.

---

## §11 — Limitations (0.25 page)

- $\tau_{\min}$ ground truth: hand-annotated for ChronoBench tasks; harder to obtain in production agent settings.
- Parser dependence: $\tau_{\text{self}}$ depends on $\Pi$; we report parser ablation in Appendix A.
- Model coverage: closed-lab harness state changes between API versions; we report results at a specific date.
- Setting B operationalization: we choose one canonical injection mechanism per setting; real-world harnesses combine several.

---

## §12 — Conclusion (0.25 page)

Frontier LLM agents do not perceive their own time. The failure is measurable, decomposable, and present even when the harness injects wall-clock information at the prompt. ChronoBench supplies a calibrated diagnostic. Paper 2 supplies a candidate intervention.

---

## Appendices

- **A. The $\tau_{\text{self}}$ Annotation Protocol** — see [`annotation-protocol.md`](annotation-protocol.md).
- **B. Per-model $\alpha$ and $N_A$ tables**.
- **C. Task templates per sub-capability**.
- **D. Setting B operationalization details**.
- **E. Long-horizon benchmark setup**.

---

## Figures

1. Three Times projections (concept diagram).
2. **CAR$(B)$ decoupling curves** (L2 primary).
3. **$\rho$ histograms with reasoning vs non-reasoning split** (L3 primary; **explicit reasoning-model extension over Garikaparthi**).
4. **Injection-Tell bar chart** (T1.1 jumps, T1.3/T2.3/T3.1 do not).
5. **Injection Atlas — closed-lab harness injection mechanism distribution** (new; converts Injection Tell into a measured industry footprint).
6. Per-model $\varepsilon$ ranking and long-horizon correlation scatter.

---

## Resolution of root critiques (cross-reference)

| Critique (from review) | Resolution in this outline |
|---|---|
| Claim too strong (in-principle, decisive, theorem) | All such language deferred to position note; outline uses hypothesis/observation register throughout |
| Paper 1 / Paper 2 boundary unclear | CUH and ChronoStack referenced only in §8.3 and §9 as forward pointers; §10 and §12 explicit about scope |
| L1 risk | L1 demoted to §5.5 regime analysis; not in abstract, not in headline figures, not called a Law |
| $\tau_{\text{self}}$ parser rigor | Full protocol in Appendix A; ablation in main text §6.5 |
| $\varepsilon^*$ threshold too early | Moved to §9.4 with reversibility note; not in abstract |
| **Concurrent-work overlap (Garikaparthi, Timely Machine, Temporally Blind)** | **§1 Concurrent Work paragraph foregrounds differentiation; §10.1 Related Work walks through each by name; reasoning-model extension and Injection Atlas as explicit novelty levers** |
| **Chronocept name collision (Goel et al., 2025)** | **§10.2 disambiguation; introduction footnote at first mention of *chronoception*** |
