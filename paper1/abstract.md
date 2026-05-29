# Paper 1 — Abstract (v0)

**Working title**: *The Augustine Problem: Evaluating Whether LLM Agents Can Perceive Their Own Time*

**Parent scope**: [`SCOPE.md`](SCOPE.md) v0
**Research programme**: [`../FRAMING.md`](../FRAMING.md) v1.2

---

## Primary abstract (≈210 words)

Large language model agents are trained on token sequences but act in wall-clock time. We ask, empirically, whether they perceive their own time. We formalize a three-times ontology — wall-clock time $\tau_{\text{wall}}$, step time $\tau_{\text{step}}$, and self-narrated time $\tau_{\text{self}}$ — define the **Augustine Problem** as the failure of an agent's policy to enforce the identity that links them, and introduce **ChronoBench**, a ~4000-instance diagnostic benchmark organized as nine sub-capabilities across the three axes, evaluated on ≥25 frontier and open-source models under both no-injection and with-injection settings. We report two main empirical findings. **Step-Clock Conflation (L2)**: under wall-clock budgets, frontier agents silently terminate at a model-specific step count rather than honoring the wall-clock, with the Clock-Adherence Ratio CAR$(B) \to 0$ as the budget grows. **Temporal Confabulation (L3)**: agents over-report the duration of their own work by 10–100×, with reasoning-tuned models exhibiting larger confabulation than matched non-reasoning baselines. Wall-clock injection raises clock-awareness pass rate to >95% but leaves execution and self-narration sub-capabilities effectively unchanged. We propose the chronoceptive calibration error $\varepsilon$ as a single scalar summarizing the three failure modes and release the benchmark, model traces, and a `pip`-installable evaluation package.

---

## Short abstract (≈110 words, for arXiv tagline)

LLM agents act in wall-clock time but are trained in token-time. We ask whether they perceive their own time. We define the three-times ontology, the Augustine Problem, and ChronoBench — a diagnostic benchmark across nine sub-capabilities and ≥25 models. We find that frontier agents silently degrade wall-clock budgets into step-count terminators (L2: Step-Clock Conflation), and over-report their own work duration by 10–100×, more so as reasoning budget grows (L3: Temporal Confabulation). Wall-clock injection raises clock awareness above 95% but leaves the load-bearing failure modes unchanged. We release ChronoBench and a single chronoceptive calibration scalar $\varepsilon$.

---

## Notes

- Title from `SCOPE.md` §1; abstract reflects the four contributions of `SCOPE.md` §1 and the softened register of `SCOPE.md` §4.
- L2 and L3 are the headline results; L1 (budget inflation) is not advertised in the abstract.
- The Augustine threshold $\varepsilon^*$ does not appear in the abstract.
- The Chronoception Upstream Hypothesis does not appear in the abstract.
- The phrase "in-principle excluded" is not used; the abstract states only the observed measurement.
- The Injection Tell appears as an empirical finding ("raises clock-awareness >95% but leaves … unchanged"), not as a rhetorical move.
