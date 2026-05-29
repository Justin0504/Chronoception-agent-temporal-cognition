# Position Note — Abstract (v0)

**Working title**: *The Augustine Problem: A Position on Temporal Cognition in LLM Agents*

**Target length**: 6–8 pages (ICML position track / COLM short / arXiv)

**Source of truth**: `../FRAMING.md` v1.0

---

## Abstract (≈220 words)

Large language model agents act in wall-clock time but are trained in token-time, and no current foundation-model training stage provides gradient signal that bridges the two. We call the resulting representational gap **the Augustine Problem**, after Augustine's remark that one knows time until asked to explain it: agents speak fluently about durations they cannot perceive, budgets they cannot honor, and elapsed time they cannot track. The fact that every major closed lab independently engineered an external wall-clock injection mechanism — the **Injection Tell** — is itself implicit industry acknowledgement of the gap. We formalize the problem as the failure of an agent's policy to enforce an implicit identity over three ontologically distinct projections of a trajectory — wall-clock time τ_wall, step time τ_step, and self-narrated time τ_self — and we collapse the failure into a single chronoceptive calibration error ε. We commit to three named empirical laws, one per projection axis: **Agentic Parkinson's Law** (work inflates to fill the wall-clock budget given to the agent), **Step-Clock Conflation** (wall-clock budgets are silently degraded into step-count terminators), and **Temporal Confabulation** (agents over-report their own work duration by 10–100×, more so as reasoning budget grows). We argue, and pre-register the prediction, that ε is causally upstream of long-horizon agent failure, and that injection closes only the most superficial sub-capability while leaving the load-bearing ones untouched. Motivating pilot evidence across five frontier and open-source models, under both no-injection and with-injection settings, and four falsifiable predictions accompany the position.

---

## Abstract variants

### A. Punchy (≈110 words, for tweet / arXiv subtitle)

LLM agents inhabit token-time but act in wall-clock time, and they have no learned representation that bridges the two. We call this the Augustine Problem: agents that speak fluently about time but cannot tell what time it is, how long they have worked, or how long anything takes. We formalize the gap as a categorical confusion between three distinct times — wall-clock, step, and self-narrated — collapse it into a single chronoceptive calibration error ε, and commit to three named empirical laws and four falsifiable predictions. We argue ε is causally upstream of long-horizon agent failure.

### B. Long (≈350 words, for grant / proposal)

The recent agentic turn in foundation-model deployment has obscured a structural defect: large language models are trained on next-token loss in a discrete, sequence-indexed regime we call token-time, while their deployments as agents take place in continuous wall-clock time, where consequences unfold in seconds and budgets are measured in hours. No mainstream training stage — pre-training, supervised fine-tuning, RLHF, RL with verifiable rewards, or recent reasoning training — provides gradient signal that grounds token-time into wall-clock time. We call the resulting representational gap the Augustine Problem, after Augustine's observation that one knows time until asked to explain it. We formalize the gap as the failure of an agent's policy to enforce an implicit identity over three ontologically distinct projections of any trajectory: external wall-clock duration τ_wall, the agent's own action count τ_step, and the agent's self-narrated work duration τ_self. We collapse the resulting three-axis failure into a single chronoceptive calibration error ε, an analogue of perplexity or FID for agent temporal cognition, and we name three empirical laws — one per axis — that quantify it: Agentic Parkinson's Law, Step-Clock Conflation, and Temporal Confabulation. The most counter-intuitive prediction we pre-register is that reasoning-tuned models, the field's principal lever for improving agent capability, exhibit strictly worse temporal confabulation than matched non-reasoning baselines, because reasoning expansion remains confined to token-time. We commit to a Chronoception Upstream Hypothesis: that ε is causally upstream of long-horizon agent failure, and that closing the gap is a prerequisite for serious agency rather than an evaluation refinement. We present motivating pilot evidence on five frontier and open-source models and four falsifiable predictions; the full diagnostic benchmark, ChronoBench, and the training framework, ChronoStack, are forthcoming companion works.

---

## Notes on the choice of abstract

- The primary 220-word abstract is the canonical version for arXiv submission.
- The 110-word version is for arXiv comments, blog posts, and Twitter.
- The 350-word version is for grant applications and Yue Zhao's lab page.
- All three derive from `FRAMING.md` §3 (Augustine Problem), §4 (ε), §5 (Three Laws), §6 (CUH), §9 (Predictions).
- No new terminology introduced beyond `FRAMING.md` §11.
