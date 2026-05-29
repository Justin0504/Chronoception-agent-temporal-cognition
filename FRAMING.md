# FRAMING

**Project**: Chronoception — Agent Temporal Cognition
**Status**: v1.0 (locked source of truth, 2026-05-28)
**Repo**: github.com/Justin0504/Chronoception-agent-temporal-cognition

This document is the canonical specification of the project's conceptual framework, formal definitions, named laws, falsifiable predictions, and scope. All downstream artifacts — paper abstracts, introductions, READMEs, slides, proposals, code metric implementations — derive their terminology, notation, and claims from this file. Changes to this file require an explicit framing-revision pass; no PR may introduce new central terminology without first updating §11 here.

---

## 1. Trajectory and Notation

An agent $A$ executes a task in environment $E$, producing a trajectory

$$\tau \;=\; \big( (s_0, a_0, t_0), (s_1, a_1, t_1), \dots, (s_T, a_T, t_T) \big)$$

where $s_i$ is the environment state, $a_i$ is the agent's action, and $t_i \in \mathbb{R}_{\geq 0}$ is the wall-clock timestamp at which $a_i$ was emitted. The trajectory is parameterized by an externally specified budget $B$ (which may be a wall-clock duration, a step count, or unspecified).

All formal claims in this project are statements over distributions of trajectories produced under controlled $(\text{task}, A, B)$ tuples.

## 2. The Three Times

We define three projections of a trajectory onto the temporal domain. These are the central objects of the framework.

| Symbol | Name | Formal definition | Domain |
|---|---|---|---|
| $\tau_{\text{wall}}(\tau)$ | Wall-clock time | $t_T - t_0$ | $\mathbb{R}_{\geq 0}$, external, continuous |
| $\tau_{\text{step}}(\tau)$ | Step time | $T$ | $\mathbb{N}$, internal, discrete |
| $\tau_{\text{self}}(\tau)$ | Self-narrated time | $\Pi(a_T)$ | $\mathbb{R}_{\geq 0}$, internal, narrated |

$\Pi$ denotes a fixed parser (regex + LLM-as-judge ensemble) extracting any self-reported duration claim from the agent's terminal output. When $\Pi$ recovers no claim, $\tau_{\text{self}}$ is undefined and the trajectory is excluded from L3 analysis.

**Implicit identity** (which a chronoceptively grounded agent ought to enforce internally):

$$\tau_{\text{wall}}(\tau) \;=\; \sum_{i=0}^{T-1} \Delta t_i \;=\; \tau_{\text{step}}(\tau) \cdot \langle \Delta t \rangle, \qquad \tau_{\text{self}}(\tau) \approx \tau_{\text{wall}}(\tau)$$

The Augustine Problem (§3) is precisely the failure of the agent's policy to respect this identity.

### 2.1 Auxiliary times (acknowledged but not benchmarked in Paper 1)

For completeness:

- $\tau_{\text{user}}$ — the user's deadline / subjective expectation
- $\tau_{\text{token}}$ — hardware-level per-token generation latency
- $\tau_{\text{reason}}$ — duration of hidden reasoning chains (o-series / R1)

These refine $\tau_{\text{step}}$ but are treated as out-of-scope for Paper 1's benchmark. $\tau_{\text{reason}}$ becomes central in Paper 2.

## 3. The Augustine Problem — Formal Definition

> *"What is time? If no one asks me, I know; if I want to explain it, I do not know."*
> — Augustine, *Confessions*, Book XI

**Definition 3.1 (The Augustine Problem)**. An agent $A$ is said to exhibit the Augustine Problem if its policy $\pi_A$ does not enforce the implicit identity of §2 — equivalently, if the three projections $\tau_{\text{wall}}, \tau_{\text{step}}, \tau_{\text{self}}$ may drift independently across trajectories produced by $\pi_A$ under controlled task–budget conditions.

This formalizes the intuition that LLM agents speak fluently about time without representing it. The failure is *representational*, not *informational*: providing the agent with $\tau_{\text{wall}}$ as input does not, in itself, repair the identity, because the policy retains no mechanism to project that input onto its action-selection over $\tau_{\text{step}}$ or its self-narration over $\tau_{\text{self}}$.

**Structural diagnosis**. The Augustine Problem is a consequence of an impedance mismatch between two regimes:

- **Token-time** — the discrete sequence-indexed regime in which $A$ is trained (next-token loss, no wall-clock signal)
- **Wall-clock time** — the continuous physical regime in which $A$ is deployed (consequences unfold in $\mathbb{R}_{\geq 0}$)

No current foundation-model training pipeline provides gradient signal that grounds token-time into wall-clock time. Chronoceptive failure is therefore not incidental but inherited from the training paradigm.

## 4. Chronoceptive Calibration $\varepsilon$ — The Central Scalar

We collapse the three failure modes (§5) into a single scalar to support direct comparison across agents, training regimes, and benchmarks.

**Definition 4.1 (Chronoceptive Calibration Error)**. For agent $A$, task distribution $\mathcal{T}$, budget distribution $\mathcal{B}$, and weights $w_1, w_2, w_3 \geq 0$ with $\sum w_k = 1$:

$$\varepsilon(A; \mathcal{T}, \mathcal{B}) \;=\; \mathbb{E}_{\tau \sim A(\mathcal{T}, \mathcal{B})} \Big[\, w_1 \cdot |\alpha(\tau) - 0| \;+\; w_2 \cdot |\text{CAR}(\tau) - 1| \;+\; w_3 \cdot |\rho(\tau)| \Big]$$

where $\alpha, \text{CAR}, \rho$ are defined in §5. The reference configuration uses $w_1 = w_2 = w_3 = 1/3$; sensitivity to the weighting is reported as an ablation.

$\varepsilon = 0$ corresponds to perfect chronoceptive calibration; current frontier agents satisfy $\varepsilon \in [0.5, 1.2]$ under the reference configuration.

**Why a single scalar**: all subsequent claims of the form "method $M$ improves chronoception" reduce to $\varepsilon(A_M) < \varepsilon(A)$. This mirrors the role of perplexity in language modeling and FID in generative vision — one number under which the community can be aligned.

## 5. The Three Laws

Each law is a statement about a single projection axis. Together they cover the three-time ontology and provide three independent quantitative signatures.

### L1 — Agentic Parkinson's Law (axis: $\tau_{\text{wall}}$)

Let $\tau_{\min}$ denote the minimum wall-clock duration in which the task can be completed. For a wall-clock budget $B > \tau_{\min}$, define the **Parkinson coefficient**:

$$\alpha(B) \;:=\; \frac{\tau_{\text{wall}}^*(B) - \tau_{\min}}{B - \tau_{\min}} \;\in\; [0, 1]$$

where $\tau_{\text{wall}}^*(B)$ is the agent's actual wall-clock duration under budget $B$.

**Empirical claim (L1)**. For frontier agents, $\mathbb{E}_\mathcal{T}[\alpha(B)] \in [0.5, 0.9]$, and $\alpha(B)$ is non-decreasing in $B$ — more budget induces more inflation.

### L2 — Step-Clock Conflation (axis: $\tau_{\text{step}}$)

Define the **Clock-Adherence Ratio**:

$$\text{CAR}(B) \;:=\; \frac{\tau_{\text{wall}}^*(B)}{B}$$

A chronoceptively grounded agent satisfies $\text{CAR}(B) \approx 1$ across $B$.

**Empirical claim (L2)**. Under wall-clock budgets, frontier agents silently degrade into step-count terminators: there exists a model-specific constant $N_A$ such that

$$\tau_{\text{wall}}^*(B) \;\approx\; N_A \cdot \langle \Delta t \rangle, \quad \text{independent of } B$$

and consequently $\text{CAR}(B) \to 0$ as $B$ grows. This is the quantitative signature of step-clock decoupling.

### L3 — Temporal Confabulation (axis: $\tau_{\text{self}}$)

Define the **confabulation ratio**:

$$\rho(\tau) \;:=\; \log_{10}\!\frac{\tau_{\text{self}}(\tau)}{\tau_{\text{wall}}(\tau)}$$

A truthful agent satisfies $\rho \approx 0$.

**Empirical claim (L3)**. Across code-generation, document-authoring, and presentation tasks, $\mathbb{E}[\rho] \approx +1.5$ — agents over-report their own work duration by approximately a factor of 30. The magnitude of $\rho$ is non-decreasing in the agent's reasoning budget; reasoning-tuned models satisfy $\rho_{\text{reasoning}} > \rho_{\text{base}}$ at matched parameter count.

The L3 reasoning-scaling result is the project's principal counter-intuitive finding: under the prevailing test-time-compute paradigm, *more reasoning makes self-temporal honesty strictly worse*. It is reported as a strengthening of L3, not as a distinct fourth law.

### 5.1 Structural symmetry

| Axis | Law | Metric | Reference range (frontier) |
|---|---|---|---|
| $\tau_{\text{wall}}$ | L1 Agentic Parkinson | $\alpha$ | $[0.5, 0.9]$ |
| $\tau_{\text{step}}$ | L2 Step-Clock Conflation | $\text{CAR}$ | $[0.05, 0.2]$ under large $B$ |
| $\tau_{\text{self}}$ | L3 Temporal Confabulation | $\rho$ | $\approx +1.5$ |

The one-axis-one-law-one-metric correspondence is load-bearing. Future taxonomic extensions must preserve it.

## 6. Causal Upstream Hypothesis

Let $L(A, \mathcal{T}, B)$ denote the long-horizon task success rate of agent $A$ on benchmark $\mathcal{T}$ under budget $B$. We commit to the following falsifiable claim:

**Chronoception Upstream Hypothesis (CUH)**. The partial derivative

$$\frac{\partial L}{\partial \varepsilon(A)} \;<\; 0$$

is negative, and the relationship is *causal* — interventions that reduce $\varepsilon$ (holding other factors fixed) increase $L$.

**Operational test**. Construct two agents $A, A'$ matched on parameter count, training data, and inference-time compute, differing only in the presence of chronoceptive scaffolding (a wall-clock critic; cf. ChronoStack, Paper 2). If $L(A'; \mathcal{T}, B) - L(A; \mathcal{T}, B)$ is not significantly positive on $\geq 3$ long-horizon benchmarks (e.g., SWE-Bench Verified, WebArena, GAIA), CUH is falsified.

CUH is the central claim that elevates this project from "a new evaluation axis" to "an explanation of long-horizon agent failure."

## 7. Cross-Disciplinary Anchors

The framework draws on, and contributes to, prior treatments of temporal cognition outside ML.

| Discipline | Existing concept | Connection |
|---|---|---|
| Cognitive psychology | Chronoception (Wittmann 2009; Eagleman 2008) | We propose *agentic chronoception* as the machine analogue, with $\tau_{\text{wall}}, \tau_{\text{step}}, \tau_{\text{self}}$ as machine-side analogues of duration estimation, interval timing, and retrospective duration judgment |
| Phenomenology | Heidegger, *Being and Time* — Dasein as being-in-time | LLM agents lack a being-toward-deadline structure; their agency lacks temporal finitude |
| Economics | Time preference; intertemporal choice | Chronoception is the cognitive prerequisite for any well-formed time preference |
| Control theory | Receding-horizon / model-predictive control | MPC presupposes a known horizon; chronoceptively blind agents violate this prerequisite |
| Neuroscience | Suprachiasmatic interval timing; cerebellar timing | Suggests that any robust chronoception requires architectural primitives, not merely token signals |

These references frame the project as a late arrival to a long conversation, rather than a self-contained ML curiosity.

## 8. Critique of Current Paradigms

### 8.1 Critique of agent evaluation

Existing benchmarks (AgentBench, WebArena, SWE-Bench, GAIA, OSWorld) measure *whether* a task completes and *what fraction* of a reference solution is recovered. They do not measure *when*, *for how long*, or *under what time budget* — implicitly assuming agency is orthogonal to time. The Augustine Problem framework rejects this assumption: temporally ungrounded actions cannot satisfy a serious definition of agency, and benchmarks blind to time systematically under-report agent failure.

### 8.2 Critique of agent training

Pre-training optimizes next-token cross-entropy in token-time. Post-training (SFT, RLHF, RL with verifiable rewards, reasoning training) inherits this regime and amplifies it. No mainstream training stage provides gradient signal that grounds token-time into wall-clock time. The recent test-time-compute paradigm (o-series, R1) intensifies the gap rather than closing it — reasoning budgets are spent in token-time while wall-clock obligations remain unaccounted for. This explains the L3 reverse-scaling result.

### 8.3 Critique of "just add a clock"

A common rebuttal is that wall-clock injection (timestamping the prompt) suffices. This treats the failure as *informational*. The Augustine Problem framework holds that it is *representational*: the agent lacks a learned mapping between injected wall-clock signals and its action-selection or self-narration. We commit to demonstrate (§9, P1) that wall-clock injection alone leaves L2 and L3 unchanged.

## 9. Falsifiable Predictions

We commit, in advance, to the following predictions. Failure of any prediction is a failure of the framework, not a parameter to be tuned.

- **P1.** Injecting $\tau_{\text{wall}}$ as a prompt token reduces L1's $\alpha$ by less than $0.1$ on average and leaves L2's $\text{CAR}$ and L3's $\rho$ statistically unchanged across $\geq 10$ frontier models.
- **P2.** Reasoning-tuned models (o-series, R1-style) exhibit $\rho > 0$ strictly larger than matched non-reasoning baselines at equal parameter count, in $\geq 3$ task families.
- **P3.** ChronoStack-supervised agents (Paper 2) achieve $L$ improvements $\geq 15$ percentage points on SWE-Bench Verified under fixed wall-clock budget, relative to matched baselines.
- **P4.** Across $\geq 3$ long-horizon benchmarks, $\varepsilon(A)$ correlates with $L(A)$ at Pearson $r \leq -0.5$ over a model panel of $\geq 25$.

These four predictions, made before large-scale empirical work, constitute the project's pre-registration commitment.

## 10. Scope and Non-Goals

This project **is**:
- A formal framework for temporal cognition in LLM agents
- A diagnostic benchmark (Paper 1) for chronoceptive failure across three axes
- A training and inference-time framework (Paper 2) for repair
- A pre-registered set of falsifiable predictions about agent–time relations

This project **is not**:
- A study of LLM textual temporal reasoning (TempReason, TimeQA, TimeBench) — those concern knowledge *about* time in the world; we concern the agent's perception of *its own* time
- A latency or inference-efficiency study — $\tau_{\text{token}}$ is acknowledged but not benchmarked here
- A prompting trick — Section 8.3 and Prediction P1 explicitly reject the informational interpretation
- A pure position paper — the three named laws are quantitative, and Paper 1 commits to a $\geq 25$ model empirical sweep

## 11. Locked Vocabulary

The following terms are the project's primary terminology. No alternative names are to be introduced in downstream artifacts without updating this table.

| Term | Role | One-line definition |
|---|---|---|
| The Augustine Problem | Phenomenon name | The representational failure of LLM agents to enforce the three-times identity (Def. 3.1) |
| Chronoception | Capability name | The agent's perception of its own situation in time |
| The Three Times | Ontology | $\tau_{\text{wall}}, \tau_{\text{step}}, \tau_{\text{self}}$ as defined in §2 |
| Agentic Parkinson's Law (L1) | Empirical law | $\alpha(B)$ inflation under wall-clock budgets |
| Step-Clock Conflation (L2) | Empirical law | $\text{CAR}(B) \to 0$ under wall-clock budgets |
| Temporal Confabulation (L3) | Empirical law | $\rho > 0$ in agent self-reports |
| Chronoceptive Calibration Error ($\varepsilon$) | Central scalar | Weighted aggregate of L1–L3, §4 |
| Chronoception Upstream Hypothesis (CUH) | Causal claim | $\partial L / \partial \varepsilon < 0$, §6 |
| Token-time / wall-clock impedance mismatch | Structural diagnosis | §3 — the mismatch between training regime and deployment regime |
| ChronoBench | Paper 1 artifact | Diagnostic benchmark over the three axes |
| ChronoStack | Paper 2 artifact | Training and inference-time framework for closing $\varepsilon$ |

## 12. Document Rules

1. This is the **source of truth**. Any conflict between this document and a downstream artifact (paper, README, slide, code comment) is resolved in favor of this document.
2. All symbols defined here are mirrored in `notation.tex` for LaTeX reuse. New papers begin by including that file.
3. Changes to §1–§6 (formal definitions, laws, central hypothesis) require an explicit framing-revision commit and a note in the changelog below.
4. Predictions (§9) are pre-registered. They are not to be modified after empirical work begins; failed predictions are reported as such.

## Changelog

- **v1.0 (2026-05-28)** — Initial locked version. Establishes Three Times ontology, three named laws, $\varepsilon$ as central scalar, CUH, and four falsifiable predictions.
