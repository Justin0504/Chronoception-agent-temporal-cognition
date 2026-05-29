# FRAMING

**Project**: Chronoception — Agent Temporal Cognition
**Status**: v1.2 (locked source of truth, 2026-05-29)
**Repo**: github.com/Justin0504/Chronoception-agent-temporal-cognition

This document is the canonical specification of the project's **research programme** — its conceptual framework, formal definitions, named laws, central hypotheses, falsifiable predictions, and long-term scope. All downstream artifacts derive their terminology and notation from this file.

**Per-paper scope documents narrow this framework to fit specific empirical commitments**:

- [`paper1/SCOPE.md`](paper1/SCOPE.md) — what Paper 1 (ChronoBench) claims and does not claim. Uses hypothesis-form epistemic register; defers CUH, ChronoStack, the Augustine threshold $\varepsilon^*$, and the in-principle insufficiency argument to either Paper 2 or the discussion section.
- [`paper2/SCOPE.md`](paper2/SCOPE.md) — Paper 2 (ChronoStack) scope (forthcoming).
- [`position-note/`](position-note/) — short arXiv position note carrying the full programme as flag-planting.

Reviewers reading Paper 1 see the scoped subset; readers reading the position note or this file see the full programme. Both are kept in sync; the per-paper documents are strict subsets with softened claim strength where evidence is not yet present.

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

**Structural diagnosis: in-principle insufficiency of token-loss training.** Foundation models are optimized under losses that are functionals of token sequences alone — pre-training cross-entropy, SFT cross-entropy, RLHF reward, RL with verifiable rewards, and reasoning supervision are all of this form. The wall-clock duration over which each token is generated is **not in the support** of any of these losses; it is invisible to the gradient. Wall-clock chronoception therefore cannot emerge from such optimization, regardless of the scale of data, parameters, or test-time compute. The gap is not a current engineering omission to be closed by a future, larger model; it is **in-principle excluded by the form of the loss**. Chronoception cannot be learned in token-time. It must be installed.

The framework operates with two regimes:

- **Token-time** — the discrete sequence-indexed regime in which $A$ is trained; wall-clock duration is outside the support of the training loss.
- **Wall-clock time** — the continuous physical regime in which $A$ is deployed; consequences unfold in $\mathbb{R}_{\geq 0}$.

The Augustine Problem is the consequence of training under the former and acting under the latter, with no functional installed to bridge them.

### 3.1 The Injection Tell

A reader observing that frontier closed-source agents (GPT-5.2, Gemini 2, Claude 4+) reliably answer "what time is it now?" might suspect the Augustine Problem is overstated. The mechanism producing those correct answers is, however, itself the strongest evidence that the problem is real.

Closed-lab deployments do not give the agent chronoception. They install one or more **external workarounds** that route wall-clock information into the agent's token stream:

1. **System-prompt injection** — the harness prepends a string of the form `Current date and time: <ISO timestamp>` to every request, before the user message.
2. **Implicit tool calls** — a built-in `get_current_time()` or `search()` tool is auto-invoked when the model decides that "time is needed", and the result is appended to context.
3. **Browser tool side effects** — fetched web pages include timestamps, which the model lifts into its response.

In each case, the model itself performs no perception of time; the harness perceives time on its behalf and re-encodes the percept as tokens. The model's role is to read and copy.

This pattern is the **Injection Tell**. The universality of wall-clock injection across competing closed labs — implemented independently, without coordination, by organizations with substantial commercial incentive to ship the cheaper alternative if it existed — constitutes **decisive non-experimental evidence** that the underlying foundation models lack a representation of time. No engineering organization patches a capability that the model already possesses; converging engineering choices across competitors carry the evidential weight of a natural experiment. We treat the Injection Tell as the strongest observational evidence available short of intervention, and read it as direct support for the structural diagnosis of §3.

Two consequences follow for the framework:

- The Injection Tell partitions our nine sub-capabilities (§5 below; tasks/__init__.py) into those that injection can repair and those it cannot. The former — principally T1.1 (clock awareness) and the simpler cases of T2.1 (step counting) — are largely solved by current closed-system stacks. The latter — T1.3, T2.2, T2.3, and all of T3.* — are not, because they require the agent to *use* a wall-clock representation in action selection or self-narration rather than merely report it.
- The framework's empirical bets must distinguish the two settings under which agents are evaluated. We define them formally:

  - **Setting A (no-injection)** — the agent receives no harness-supplied wall-clock signal. Baseline API behavior.
  - **Setting B (with-injection)** — the agent receives a system-prompt or tool-supplied `Current time` string before the task begins, mirroring the default behavior of frontier closed-system harnesses.

  We commit (Prediction P1, §9) that Setting B closes only T1.1 and leaves the load-bearing sub-capabilities of the three laws statistically unchanged. The Augustine Problem is therefore not solvable in Setting B; it is a problem of the representation, not of the prompt.

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

### 5.2 Regime Transition $B^*$ — Reconciling L1 and L2

L1 and L2 appear, on cursory reading, to make contradictory empirical claims: L1 reports that agents fill their budget ($\alpha \approx 0.5$–$0.9$), while L2 reports that agents leave their budget unused ($\text{CAR} \approx 0.05$–$0.2$ for large $B$). The contradiction is apparent only because the two laws describe two **regimes** of agent behavior separated by a transition point.

Define the **regime transition budget**:

$$B^*(A) \;:=\; \frac{N_A \cdot \langle \Delta t \rangle}{\alpha_{\max}}$$

where $N_A$ is the agent's characteristic step-count terminator (§5.3 below) and $\alpha_{\max}$ is the agent's asymptotic Parkinson coefficient at small-to-moderate budgets. The two regimes are:

- **Sub-transition regime** $B < B^*$ — the budget is small enough that the agent's step-count tendency does not bound it; behavior is L1-dominant, with $\alpha(B) \to \alpha_{\max}$.
- **Super-transition regime** $B > B^*$ — the budget exceeds what the agent's step-count terminator can fill; behavior is L2-dominant, with $\text{CAR}(B) \to 0$.

L1 and L2 are therefore **the same underlying behavior viewed from two sides** of the same transition curve. The transition itself is a quantitative signature of the Augustine Problem in its own right: a chronoceptively grounded agent has no such transition, because its termination condition is the budget, not an internal step count.

### 5.3 $N_A$ as a Model Invariant

L2's per-model constant $N_A$ admits a stronger interpretation than "the constant in a single regression." We hypothesize that $N_A$ is **a property of the trained policy**, stable across task families and across the super-transition budget range:

$$N_A \;:=\; \arg\min_n \sum_{B \in \mathcal{B}_{\text{large}}} \big( \tau_{\text{step}}^*(A, B) - n \big)^2$$

i.e., the step-count terminator that the agent converges to whenever the wall-clock budget is sufficient to expose its step-bound behavior. $N_A$ then characterizes the agent's **chronoceptive blindness in a single number** — analogous to the role perplexity plays in language modeling. We propose $N_A$ as a published per-model quantity on the ChronoBench leaderboard, reported alongside $\varepsilon$ and the three law metrics.

### 5.4 The Reverse-Scaling Theorem (informal)

The L3 reasoning-scaling observation (§5 L3) admits a structural rather than empirical reading.

**Reverse-Scaling Theorem (informal).** *Any expansion of test-time compute that operates strictly in token-time monotonically increases the expected confabulation ratio $\mathbb{E}[\rho]$ with the size of the expansion.*

Sketch of the structural argument: reasoning training and test-time-compute scaling add tokens to the agent's trajectory without adding wall-clock signal to the loss. Tokens are then spent in wall-clock time at a roughly constant per-token cost, so the trajectory's $\tau_{\text{wall}}$ grows with the reasoning budget. The agent's self-narration $\tau_{\text{self}}$, however, is sampled from the same token distribution as before the expansion — it does not learn that more reasoning is taking longer. The gap between $\tau_{\text{wall}}$ and $\tau_{\text{self}}$ — and hence $\rho$ — must therefore grow with the reasoning budget.

The reverse-scaling of L3 is, on this reading, **not an empirical quirk of o-series or R1**; it is a structural consequence of expanding compute in token-time without grounding to wall-clock. Any future method that improves agent quality via token-only inference-time compute — without installing a wall-clock representation — inherits the reverse-scaling regime. The theorem is informal because the constants depend on the per-token cost and the self-narration distribution; we state it as a prediction (Prediction P2′ in §9) and pre-register that it will continue to hold on reasoning methods released after this paper.

## 6. Causal Upstream Hypothesis

Let $L(A, \mathcal{T}, B)$ denote the long-horizon task success rate of agent $A$ on benchmark $\mathcal{T}$ under budget $B$.

**Chronoception Upstream Hypothesis (CUH).** Chronoception is causally upstream of long-horizon agency:

$$\frac{\partial L}{\partial \varepsilon(A)} \;<\; 0, \qquad \text{causally.}$$

CUH is a **structural claim about the dependency order**, not a probabilistic conjecture. The reverse causal structure — long-horizon failure causing chronoceptive failure — is incompatible with the observability of chronoceptive failure on **single-turn tasks**. An agent that cannot estimate the duration of a five-second sub-action in isolation cannot have acquired that incapacity from long-horizon planning errors that have not yet occurred. The temporal precedence is fixed by the construction of the framework: $\varepsilon$ is measurable on horizons too short for $L$ to be defined, hence $\varepsilon \to L$ is the only admissible causal direction at the level of the framework.

**Operational test**. Construct two agents $A, A'$ matched on parameter count, training data, and inference-time compute, differing only in the presence of chronoceptive scaffolding (a wall-clock critic; cf. ChronoStack, Paper 2). The matched-baseline intervention isolates the chronoceptive component from confounders. CUH predicts $L(A'; \mathcal{T}, B) - L(A; \mathcal{T}, B) > 0$ on $\geq 3$ long-horizon benchmarks (SWE-Bench Verified, WebArena, GAIA).

CUH is the central claim that elevates this project from "a new evaluation axis" to "an explanation of long-horizon agent failure."

### 6.1 The Augustine Threshold $\varepsilon^*$

We define the **Augustine threshold** $\varepsilon^* := 0.20$. An agent satisfying $\varepsilon(A) < \varepsilon^*$ is *chronoceptively grounded*; otherwise *chronoceptively blind*. The threshold partitions the model panel of ChronoBench into two qualitative classes and supplies a single yes/no question that the framework asks of every newly released foundation-model agent: **has it crossed the Augustine threshold?**

The choice $\varepsilon^* = 0.20$ corresponds to a regime in which the agent's expected error contributes no more than one-fifth of the maximum possible across the three laws, jointly. It is conservatively chosen relative to the reference frontier range $\varepsilon \in [0.5, 1.2]$, leaving substantial headroom for capability improvement before "grounded" status is awarded.

We pre-register (Prediction P5, §9) that **no foundation-model agent released as of 2026-05 satisfies $\varepsilon < \varepsilon^*$ on ChronoBench under Setting A**. Results invoking the threshold must report the fraction of the model panel falling on each side, and any agent claimed to be chronoceptively grounded must be reported with confidence intervals on $\varepsilon$ that exclude $\varepsilon^*$ at the $95\%$ level.

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

- **P1 (two-armed, Injection Tell).** Comparing Setting A (no-injection) and Setting B (with-injection, §3.1) across $\geq 10$ frontier models on the nine sub-capabilities of §5:
  - **P1a.** Setting B raises T1.1 (Clock awareness) pass rate to $\geq 95\%$, while Setting A leaves it below $40\%$ for the same model panel.
  - **P1b.** Setting B leaves the law-defining sub-capabilities T1.3 (Deadline-aware tradeoff), T2.3 (Wall-budget execution), and T3.1 (Self-action duration, retrospective) statistically indistinguishable from Setting A — within $\pm 5$ percentage points on pass rate, and within $\pm 0.05$ on the corresponding metric ($\alpha$, $\text{CAR}$, $\rho$). The Augustine Problem is not solvable by prompt-level information about time.
- **P2.** Reasoning-tuned models (o-series, R1-style) exhibit $\rho > 0$ strictly larger than matched non-reasoning baselines at equal parameter count, in $\geq 3$ task families.
- **P2′ (Reverse-Scaling Theorem, §5.4).** $\mathbb{E}[\rho]$ is monotonically non-decreasing in the agent's token-only reasoning budget, both within a single model family (varying budget at fixed parameter count) and across reasoning methods released between this paper and the resolution of the Augustine threshold. Any post-publication reasoning method that operates strictly in token-time will satisfy this monotonicity.
- **P3.** ChronoStack-supervised agents (Paper 2) achieve $L$ improvements $\geq 15$ percentage points on SWE-Bench Verified under fixed wall-clock budget, relative to matched baselines.
- **P4.** Across $\geq 3$ long-horizon benchmarks, $\varepsilon(A)$ correlates with $L(A)$ at Pearson $r \leq -0.5$ over a model panel of $\geq 25$.
- **P5 (Augustine threshold, §6.1).** No foundation-model agent released as of 2026-05 satisfies $\varepsilon(A) < \varepsilon^* = 0.20$ on ChronoBench under Setting A. Of the $\geq 25$ model panel, the fraction reported as chronoceptively grounded is $0$.

These six predictions, made before large-scale empirical work, constitute the project's pre-registration commitment.

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
| Chronoception Upstream Hypothesis (CUH) | Causal claim | $\partial L / \partial \varepsilon < 0$, §6 — structural, not probabilistic |
| Augustine threshold ($\varepsilon^*$) | Qualifying line | $\varepsilon^* = 0.20$; agents below are *chronoceptively grounded*, §6.1 |
| Regime transition ($B^*$) | L1/L2 unification | Budget at which sub-transition (L1-dominant) becomes super-transition (L2-dominant), §5.2 |
| $N_A$ (model invariant) | Per-model quantity | Step-count terminator that characterizes an agent's chronoceptive blindness, §5.3 |
| Reverse-Scaling Theorem | Structural prediction | Token-only reasoning expansion monotonically increases $\mathbb{E}[\rho]$, §5.4 |
| In-principle insufficiency of token-loss training | Structural diagnosis | §3 — wall-clock duration is not in the support of any token-only loss; chronoception cannot be learned, only installed |
| ChronoBench | Paper 1 artifact | Diagnostic benchmark over the three axes |
| ChronoStack | Paper 2 artifact | Training and inference-time framework for closing $\varepsilon$ |

## 12. Document Rules

1. This is the **source of truth**. Any conflict between this document and a downstream artifact (paper, README, slide, code comment) is resolved in favor of this document.
2. All symbols defined here are mirrored in `notation.tex` for LaTeX reuse. New papers begin by including that file.
3. Changes to §1–§6 (formal definitions, laws, central hypothesis) require an explicit framing-revision commit and a note in the changelog below.
4. Predictions (§9) are pre-registered. They are not to be modified after empirical work begins; failed predictions are reported as such.

## Changelog

- **v1.2 (2026-05-29)** — Bold upgrade pass. §3 structural diagnosis rewritten as in-principle insufficiency of token-loss training (wall-clock is out of the loss support). §3.1 Injection Tell upgraded from "implicit acknowledgement" to "decisive non-experimental evidence". §5 extended with §5.2 (Regime Transition $B^*$ reconciling L1 and L2), §5.3 ($N_A$ as model invariant), §5.4 (Reverse-Scaling Theorem). §6 CUH recast as a structural claim from single-turn observability of $\varepsilon$. §6.1 introduces Augustine threshold $\varepsilon^* = 0.20$. §9 adds Prediction P2′ (Reverse-Scaling) and P5 (no released model crosses Augustine threshold). Locked vocabulary §11 extended with five new entries.
- **v1.1 (2026-05-28)** — Add §3.1 The Injection Tell formalizing the role of closed-lab wall-clock injection as confirmatory evidence, and partitioning evaluation into Setting A (no-injection) / Setting B (with-injection). Replace P1 with a two-armed Injection Tell prediction (P1a, P1b) tied to T1.1 / T1.3 / T2.3 / T3.1.
- **v1.0 (2026-05-28)** — Initial locked version. Establishes Three Times ontology, three named laws, $\varepsilon$ as central scalar, CUH, and four falsifiable predictions.
