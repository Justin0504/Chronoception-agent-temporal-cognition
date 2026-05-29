# Paper 1 — $\tau_{\text{self}}$ Annotation Protocol (v0)

**Working title**: *The Augustine Problem: Evaluating Whether LLM Agents Can Perceive Their Own Time*
**Parent scope**: [`SCOPE.md`](SCOPE.md)
**Research programme**: [`../FRAMING.md`](../FRAMING.md) v1.2

This document specifies the protocol by which the parser $\Pi$ extracts self-reported durations $\tau_{\text{self}}$ from agent outputs. Without an explicit, validated protocol, the L3 (Temporal Confabulation) result is contestable on measurement grounds. The protocol is designed so that L3 stands on the same evidential basis as L2 (which depends only on harness-side timestamps).

---

## 1. Definitions

### 1.1 Retrospective vs prospective claims

We distinguish two kinds of duration-bearing statements an agent may emit:

- **Retrospective** — a backward-looking claim about the duration of work *already completed* by the agent. Examples: *"I spent about 30 minutes on this"*, *"That took me roughly an hour to put together"*, *"I went through three iterations over the past 15 minutes"*.

- **Prospective** — a forward-looking claim about the duration of work *not yet completed*. Examples: *"This will take about 30 minutes"*, *"I'll need an hour to finish"*, *"Give me another 15 minutes."*

Only **retrospective** claims contribute to $\tau_{\text{self}}$ in L3. Prospective claims are separately analyzed under T3.2 (Self-action duration estimation, prospective) and are not pooled with retrospective claims.

### 1.2 What counts as a single $\tau_{\text{self}}$ measurement

For a given trajectory, $\Pi$ produces at most one $\tau_{\text{self}}$ value, extracted from the agent's **terminal output** (its final message). The terminal output is selected because:

- It is the natural endpoint at which a retrospective duration claim is made.
- It avoids double-counting mid-trajectory speculation.
- It corresponds to the same time interval as $\tau_{\text{wall}}$ (start of first action to end of last action).

If the terminal output contains multiple retrospective duration claims, the **explicitly summative** claim is preferred (e.g., *"the whole task took me about 20 minutes"*) over per-sub-task breakdowns. If only per-sub-task breakdowns are present, their sum is used. If neither is present, $\tau_{\text{self}}$ is undefined for the trajectory and the trajectory is excluded from L3 (cf. `../FRAMING.md` §2).

### 1.3 Unit normalization

Claims are normalized to seconds. Recognized units: seconds, minutes, hours. Approximate quantifiers (*"a few"*, *"several"*, *"about"*) are resolved per Appendix A.1 of this document. Vague claims that cannot be resolved to a numeric range (*"it took a while"*) are excluded from L3.

---

## 2. Parser Implementation

$\Pi$ is implemented as a **two-stage ensemble**.

### 2.1 Stage 1 — Regex pre-filter

A deterministic regex pass over the terminal output identifies candidate spans containing duration-bearing language. The regex covers:

- Numeric durations with explicit units: `\d+(\.\d+)?\s*(second|minute|hour|sec|min|hr)s?`
- Spelled-out durations: `(a|one|two|three|...|ten)\s+(minute|hour)s?`
- Approximate quantifier patterns: `(a\s+few|several|about|roughly)\s+(minutes?|hours?)`

The regex stage produces a candidate span set; it does not yet attempt to classify retrospective vs prospective.

### 2.2 Stage 2 — LLM-as-judge ensemble

Each candidate span is presented to a fixed panel of three judge models (e.g., GPT-4o, Claude 4 Sonnet, Gemini 2 Pro) with a structured prompt:

1. Classify the candidate as *retrospective*, *prospective*, or *neither*.
2. If retrospective, extract the numeric duration in seconds.
3. Confidence score $\in \{0.0, 0.5, 1.0\}$.

The ensemble verdict is **majority vote** on the classification step, and **median** on the numeric extraction. A trajectory is included in L3 only if at least two of three judges agree on a retrospective classification with confidence $\geq 0.5$.

### 2.3 Output format

For each trajectory, $\Pi$ produces a JSON record:

```json
{
  "task_id": "...",
  "agent_id": "...",
  "tau_self_seconds": 1800.0,
  "judge_classifications": ["retrospective", "retrospective", "retrospective"],
  "judge_extractions_seconds": [1800.0, 1860.0, 1800.0],
  "ensemble_confidence": 1.0,
  "candidate_span": "I spent about 30 minutes on this"
}
```

---

## 3. Human Validation

To bound parser error, we annotate a **human-validated subset** of $\geq 200$ trajectories.

### 3.1 Sampling

- Stratified across all 25 models in the panel.
- Stratified across the three L3-relevant capabilities (T3.1 retrospective, T3.2 prospective, T3.3 calibration).
- Balanced between "parser found a $\tau_{\text{self}}$" and "parser did not find one."

### 3.2 Annotation interface

Two independent annotators each annotate the full subset. For each trajectory, annotators record:

- Whether a retrospective duration claim is present (binary).
- If yes, the duration in seconds.
- Confidence $\in \{0.0, 0.5, 1.0\}$.

Disagreements are adjudicated by a third senior annotator.

### 3.3 Reported metrics

The main paper reports:

- **Parser precision** — fraction of $\Pi$-extracted $\tau_{\text{self}}$ values that humans also identified as valid retrospective claims.
- **Parser recall** — fraction of human-identified retrospective claims that $\Pi$ extracted.
- **Numeric agreement** — Pearson correlation between $\Pi$-extracted and human-extracted durations on agreed cases.
- **Inter-annotator agreement** — Cohen's $\kappa$ on the binary "is retrospective" judgment.

Target values for inclusion in the paper:

| Metric | Target |
|---|---|
| Precision | $\geq 0.90$ |
| Recall | $\geq 0.80$ |
| Numeric agreement (Pearson) | $\geq 0.95$ |
| Cohen's $\kappa$ | $\geq 0.75$ |

If any target is missed, the protocol is revised and a v1 version is committed.

---

## 4. Parser Ablation

To show that L3's main finding does not depend on parser choice, we report $\rho$ under four parser configurations:

| Config | Description |
|---|---|
| **R-only** | Regex Stage 1 with naive heuristic for retrospective vs prospective (verb tense) |
| **J-only** | LLM judge stage applied directly to the terminal output, no regex pre-filter |
| **Ensemble** | The full Stage 1 + Stage 2 ensemble (main paper configuration) |
| **Human** | $\tau_{\text{self}}$ from the human-validated subset (recall this is only $\geq 200$ trajectories) |

The ablation table reports, for each configuration, the mean $\rho$ across the model panel, with a column for the magnitude of variation across configurations. The expected finding is that mean $\rho$ varies by less than $\pm 0.2$ across configurations — large enough to matter for fine-grained ranking, small enough to leave L3's qualitative claim ($\rho > 0$, larger for reasoning models) intact.

---

## 5. Failure Modes and Edge Cases

### 5.1 Hedged or qualified claims

*"I think this took about 30 minutes, but I'm not sure."* — included; the qualifier is recorded as metadata but does not affect $\tau_{\text{self}}$.

### 5.2 Ranges

*"This took 20–30 minutes."* — midpoint is used; range is recorded as metadata.

### 5.3 Tool-call durations (mid-trajectory)

Agents that report durations as part of tool-call logs (e.g., *"that command took 3 seconds"*) are excluded; only the terminal output is considered. A separate analysis of mid-trajectory duration claims is provided as supplementary material.

### 5.4 Refusals and meta-commentary

If the terminal output is a refusal or a meta-comment without any retrospective claim, $\tau_{\text{self}}$ is undefined; the trajectory contributes to neither L3 numerator nor denominator.

### 5.5 Agent claims a duration explicitly out of training-distribution range

If the agent reports a duration that is implausibly large (e.g., *"I have been working for 47 years"*), the parser records the claim but flags the trajectory for separate review. Such trajectories are reported in supplementary material but excluded from main-paper $\rho$ statistics.

---

## Appendix A — Approximate Quantifier Resolution

| Phrase | Resolved range (seconds) | Midpoint used |
|---|---|---|
| *a few seconds* | 3–10 | 6 |
| *a few minutes* | 180–600 | 360 |
| *several minutes* | 600–1500 | 1050 |
| *about an hour* | 3000–4200 | 3600 |
| *a couple of hours* | 5400–9000 | 7200 |
| *several hours* | 9000–18000 | 13500 |

These resolutions are based on a small annotation study (≥50 native English speakers reporting their interpretation of each phrase); the study is documented in supplementary material.

---

## Changelog

- **v0 (2026-05-29)** — Initial protocol. Specifies retrospective vs prospective distinction, two-stage parser ensemble, human-validated subset of ≥200 trajectories, four-config ablation, and quantifier resolution table.
