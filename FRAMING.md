# FRAMING

**Project**: Chronoception — Agent Temporal Cognition
**Status**: v1.4 (locked source of truth, 2026-05-29)
**Repo**: github.com/Justin0504/Chronoception-agent-temporal-cognition

This document is the canonical specification of the project's **research programme** — its conceptual framework, formal definitions, named laws, central hypotheses, falsifiable predictions, and long-term scope. All downstream artifacts derive their terminology and notation from this file.

**Per-paper scope documents narrow this framework to fit specific empirical commitments**:

- [`paper1/SCOPE.md`](paper1/SCOPE.md) — what Paper 1 (ChronoBench) claims and does not claim. Uses hypothesis-form epistemic register; defers CUH, ChronoStack, the Augustine threshold $\varepsilon^*$, and the in-principle insufficiency argument to either Paper 2 or the discussion section.
- [`paper2/SCOPE.md`](paper2/SCOPE.md) — Paper 2 (ChronoStack) scope (forthcoming).
- [`position-note/`](position-note/) — short arXiv position note carrying the full programme as flag-planting.

Reviewers reading Paper 1 see the scoped subset; readers reading the position note or this file see the full programme. Both are kept in sync; the per-paper documents are strict subsets with softened claim strength where evidence is not yet present.

---

## 0.0 The Headline

> **The systems currently called LLM agents do not perceive their own time. The gap is structural — wall-clock duration is not in the support of any current training loss — and decomposes into three measurable failure modes (Agentic Parkinson's Law, Step-Clock Conflation, Temporal Confabulation) that unify into a single scalar $\varepsilon$. Until $\varepsilon$ crosses the Augustine threshold $\varepsilon^{*}$, the systems in question are *tools* deployed for variable durations, not *agents* inhabiting time. We name the problem (the Augustine Problem), formalize it (the Three Times), measure it (ChronoBench), audit the industry's workaround (the Injection Atlas), and pre-register seven empirical predictions that distinguish it from tunability.**

This single paragraph is the project's irreducible statement. Every downstream artifact derives a shorter version of it (abstract one-liner, slide title, tweet). It is not edited without an explicit framing-revision pass.

---

## 0. Concurrent Work and Differentiation

Three contemporaneous papers operate in the same conceptual neighborhood. Each addresses a single axis of the three-times ontology developed here; none has unified them, named the failure modes, defined an aggregated calibration scalar, or formalized the Injection Tell. We state the relationship explicitly:

- **Garikaparthi (2026), *Can LLMs Perceive Time? An Empirical Investigation*** (arXiv 2604.00010). Measures duration self-reports on four non-reasoning model families (GPT-5, GPT-4o, OLMo3-7B, Qwen3-8B), finding pre-task overshoot of 4–7× and post-hoc disconnection from reality. Subsumes only the $\tau_{\text{self}}$ axis (our L3) and only on non-reasoning models. Our framework (i) extends to reasoning-tuned models and predicts the reverse-scaling regime (§5.4), (ii) unifies $\tau_{\text{self}}$ with $\tau_{\text{wall}}$ and $\tau_{\text{step}}$, (iii) names the law (Temporal Confabulation) and defines the ratio $\rho$, (iv) connects to budget-following behavior through $\varepsilon$.

- **Ma et al. (2026), *Timely Machine: Awareness of Time Makes Test-Time Scaling Agentic*** (arXiv 2601.16486). Distinguishes wall-clock from generation length, develops Timely-RL training, and empirically observes reasoning length expanding with time budget. The decoupling result is framed as a desirable engineering signal for test-time scaling. We invert the framing: the same decoupling is diagnostic of *Agentic Parkinson's Law* (L1) — work expands to fill the wall-clock budget given. Ma et al. do not introduce $\tau_{\text{self}}$, do not formalize $\alpha$ as a coefficient, do not identify Step-Clock Conflation (L2), and do not address self-narration.

- **Cheng et al. (2025), *Your LLM Agents are Temporally Blind*** (arXiv 2510.23853). Coins *temporal blindness* in the context of tool-use timing decisions, ships TicToc-v1 (34 scenarios), notes informally that lab harnesses inject timestamps via tool outputs. The mention of harness injection stops short of an evidential argument. We elevate the observation to a formal evidential argument (§3.1 Injection Tell), generalize from tool-use to the three-axis ontology, and quantify the injection footprint across a closed-lab harness audit (§5.5).

We additionally note the **name collision** with Goel et al. (2025), *Chronocept: Instilling a Sense of Time in Machines* (arXiv 2505.07637), which applies the cognitive-science term *chronoception* to the temporal validity of facts in retrieval-augmented generation. The application is orthogonal; we use *chronoception* in its original sense — perception of one's own work duration. We disambiguate at first mention in every downstream artifact.

The fourth and closest empirical neighbor is **Anonymous (2026), *Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents*** (arXiv 2603.29231), which reports three time dimensions in parallel (human-estimated duration, agent steps, tokens) and observes that "human time and agent steps can diverge significantly across domains." This is the nearest formal precedent for a three-axis treatment of agent time, but the axes are *measurement* dimensions rather than a unified ontology with an implicit identity, the work does not introduce $\tau_{\text{self}}$, and no scalar aggregation is proposed.

We retain the following novelty contributions, none of which is contested in the concurrent literature: (1) **The Augustine Problem** as a named structural diagnosis, (2) the **Three Times ontology** as a unified construct including $\tau_{\text{self}}$, (3) the **three named laws** with quantitative metrics, (4) the **chronoceptive calibration error $\varepsilon$** as an aggregated scalar, (5) the **Injection Tell** as a formal evidential argument and (when supported by §5.5) a quantitative finding, (6) the **Chronoception Upstream Hypothesis (CUH)**, (7) the **Reverse-Scaling Theorem** on reasoning models, and (8) the **regime transition $B^*$** unifying L1 and L2.

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

### 3.5 The Phenomenology of Agent Time

The structural diagnosis of §3 admits a sharper articulation by drawing on the phenomenological tradition. We distinguish three modes in which time appears to a cognitive system:

- **Time as objective magnitude** — the regime of clocks, calendars, and physical durations. Accessible to any system equipped with a measurement instrument.
- **Time as lived duration** — Bergson's *durée*: the felt, asymmetric, non-uniform stream of experience. Inseparable from a cognitive process unfolding in itself.
- **Time as project horizon** — Heidegger's *care* structure of Dasein: time as the horizon against which goals, commitments, and consequences become intelligible. Time as the medium of agency.

A cognitive system has chronoception when it integrates all three modes. Humans, neurotypically, do; agents with only one or two modes have specific, predictable failures.

LLM agents acquire the third mode partially, by absorbing the narrative structure of training data — they know that humans say *"this will take a week"* before working on something. They lack the first mode unless it is injected (the Injection Tell). They lack the second mode entirely: no forward pass instantiates a lived stream of duration. The agent's "self-narration" of time ($\tau_{\text{self}}$) is therefore a **language-act about time**, not a **report from temporal experience**. This is why Temporal Confabulation (L3) is structurally inevitable on the current architecture: the narrative organ is intact, the experience that should ground it is absent.

The Augustine Problem, on this reading, is not merely a missing input — it is a **missing mode of being**. Closing it requires installing the second mode (lived duration) into the policy, not just exposing the first mode (clock magnitude) at the prompt. We make this concrete in Paper 2's ChronoStack, which trains a policy on trajectories carrying ground-truth wall-clock signal as part of the loss — installation, not exposure.

This phenomenological frame is distinct from the engineering-mode discussion of §3 and §3.1. It is included here because the strongest objection to the framework — *"is this really a deep problem, or just a measurement gap?"* — is answered most cleanly at the phenomenological level. The three modes are not interchangeable; an agent that has only the third has *talk about time without time*. The framework's name (the Augustine Problem) was chosen precisely because Augustine's "*I know what time is until you ask me*" is exactly the symptom of having mode three (the narrative organ) without modes one and two (clock and durée).

## 4. Chronoceptive Calibration $\varepsilon$ — The Central Scalar

We collapse the three failure modes (§5) into a single scalar to support direct comparison across agents, training regimes, and benchmarks.

**Definition 4.1 (Chronoceptive Calibration Error)**. For agent $A$, task distribution $\mathcal{T}$, budget distribution $\mathcal{B}$, and weights $w_1, w_2, w_3 \geq 0$ with $\sum w_k = 1$:

$$\varepsilon(A; \mathcal{T}, \mathcal{B}) \;=\; \mathbb{E}_{\tau \sim A(\mathcal{T}, \mathcal{B})} \Big[\, w_1 \cdot |\alpha(\tau) - 0| \;+\; w_2 \cdot |\text{CAR}(\tau) - 1| \;+\; w_3 \cdot |\rho(\tau)| \Big]$$

where $\alpha, \text{CAR}, \rho$ are defined in §5. The reference configuration uses $w_1 = w_2 = w_3 = 1/3$; sensitivity to the weighting is reported as an ablation.

$\varepsilon = 0$ corresponds to perfect chronoceptive calibration; current frontier agents satisfy $\varepsilon \in [0.5, 1.2]$ under the reference configuration.

**Why a single scalar**: all subsequent claims of the form "method $M$ improves chronoception" reduce to $\varepsilon(A_M) < \varepsilon(A)$. This mirrors the role of perplexity in language modeling and FID in generative vision — one number under which the community can be aligned.

### 4.5 Chronoceptive Cost Calibration (CCC)

Chronoception has an immediate economic shadow. An agent that cannot perceive its own time also cannot perceive its own cost: compute, energy, dollars, opportunity. We formalize the coupling explicitly.

Let $c(A, \tau)$ denote the realized cost of executing trajectory $\tau$ under agent $A$ — a non-negative scalar summing inference cost, tool-call cost, and any externalities the deployment exposes. Let $c_{\text{est}}(A, \tau)$ denote the agent's self-reported expected cost, extracted by the same parser ensemble (extended to monetary or compute units; see [`paper1/annotation-protocol.md`](paper1/annotation-protocol.md)). Define the **Chronoceptive Cost Calibration Error**:

$$\text{CCC}(A; \mathcal{T}, \mathcal{B}) \;=\; \mathbb{E}_{\tau} \Big[\, \big|\,\log_{10}\!\tfrac{c_{\text{est}}(A, \tau)}{c(A, \tau)}\,\big| \,\Big]$$

— the absolute log-ratio between self-reported and realized cost, averaged over the trajectory distribution.

**Coupling claim**: CCC is bounded below by a function of $\varepsilon$:

$$\text{CCC}(A) \;\geq\; \kappa \cdot \rho(\tau)\big|_{\text{self-reports}}$$

informally because cost is dominated by token count, token count tracks wall-clock at a roughly constant per-token rate, and cost-narration is sampled from the same distribution as duration-narration. The full inequality requires the per-token-cost analysis of Paper 2; we state the qualitative claim here.

**Why this matters for the framing**: the Augustine Problem is not only an evaluation refinement — it has direct economic consequences. An agent that cannot estimate its own duration cannot bid for jobs, cannot honor cost ceilings, cannot trade off quality against budget. Cost-blindness is downstream of time-blindness. CCC supplies the bridge that converts our framework into a concern for AI deployment economics and AI safety (under-counting cost is a safety failure mode).

CCC is a Paper 2-grade contribution that we mention here for completeness; Paper 1's L3 measurement is its prerequisite.

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

### 5.5 The Closed-Lab Injection Audit

The Injection Tell (§3.1) is converted from a rhetorical argument into a **quantitative empirical contribution** through a systematic audit of frontier closed-lab agent harnesses. For each closed-lab agent product (ChatGPT, Claude.ai, Gemini app, Copilot, Devin, Cursor, Cline, and analogous harnessed deployments), we record:

- Whether the harness injects wall-clock time via **system-prompt insertion** (presence of a `Current time:` string or equivalent).
- Whether the harness exposes a **`get_current_time()` tool** or analogous time-yielding function that the model auto-invokes.
- Whether **browser tool outputs include timestamps** that the model surfaces in its responses.
- The format and granularity of the injected timestamp (date-only, ISO-8601, time-zone-aware).

The audit produces an **Injection Atlas**: a table of $\geq 10$ closed-lab harnesses across the three columns above, accompanied by minimal reproducible prompts that elicit the injected information from each harness.

**Pre-registered empirical claim (Prediction P6, §9)**: $\geq 80\%$ of surveyed closed-lab agent harnesses install at least one wall-clock injection mechanism. The argument of §3.1 is then not merely "this is engineering folk wisdom"; it is a measured industry footprint.

The Injection Atlas is distinct from prior treatments: Cheng et al. (2025) note harness injection informally without auditing or quantifying it; engineering blog posts (Jeong 2026 and analogues) discuss individual cases without systematic survey. The audit converts the Injection Tell from a rhetorical move into a contribution.

### 5.6 Retrospective and Prospective L3 — Asymmetric Confabulation

Cognitive psychology distinguishes two duration-judgment processes that share little neural overlap: **prospective** (estimating how long an upcoming task will take) and **retrospective** (estimating how long a past task took). The two are dissociated in human subjects — Wittmann (2009) and follow-ups show that prospective judgments rely on attentional sampling of an internal pacemaker, while retrospective judgments are reconstructed from episodic memory of events. The two error profiles are different: prospective estimates dilate under attention; retrospective estimates dilate under event count.

L3 as stated in §5 conflates these. We refine it:

- **L3-retrospective** (current §5 default): $\rho_{\text{retro}} = \log_{10}(\tau_{\text{self, retro}} / \tau_{\text{wall}})$, measured on T3.1 (Self-action duration, retrospective).
- **L3-prospective**: $\rho_{\text{prospective}} = \log_{10}(\tau_{\text{self, prospective}} / \tau_{\text{wall}})$, measured on T3.2 (Self-action duration, prospective).

**Asymmetry claim (predicted)**: $|\rho_{\text{retro}}| \neq |\rho_{\text{prospective}}|$ at the model level; their *signs* may differ; reasoning training affects them differently. Without empirical disambiguation, an L3 measurement that pools the two is a noisy estimate of two distinct phenomena.

**Why this matters for differentiation**: Garikaparthi (2026) measures both pre-task (prospective) and post-hoc (retrospective) self-reports and notes that they disconnect by orders of magnitude in opposite directions — but does not theorize the asymmetry. We name it, formalize it as two distinct laws, predict that reasoning training amplifies prospective dilation more than retrospective dilation (because reasoning operates pre-decision), and add the asymmetry to the pre-registration set (Prediction P2′′, §9).

### 5.7 Hidden Time $\tau_{\text{reason}}$ — The Mechanism Behind Reverse-Scaling

The Reverse-Scaling Theorem (§5.4) requires a mechanism. We supply one.

Decompose the step-time projection:

$$\tau_{\text{step}}(\tau) \;=\; \tau_{\text{step, surface}}(\tau) \;+\; \tau_{\text{step, reason}}(\tau)$$

where $\tau_{\text{step, surface}}$ counts surface-visible agent actions (tool calls, message turns) and $\tau_{\text{step, reason}}$ counts hidden reasoning steps (CoT iterations, o-series chain-of-thought, R1 silent traces).

Two empirical regularities define the mechanism:

1. **Reasoning expansion is invisible to self-narration**. The agent's $\tau_{\text{self}}$ is sampled from the surface-narration distribution, which is approximately invariant to $\tau_{\text{reason}}$. The model has no learned function mapping hidden chain length to self-reported duration.

2. **Reasoning expansion is visible to wall-clock**. Tokens emitted in hidden chains cost wall-clock seconds at roughly the per-token rate. So $\tau_{\text{wall}}$ grows linearly in reasoning budget.

The two facts together force the Reverse-Scaling Theorem: $\rho = \log_{10}(\tau_{\text{self}} / \tau_{\text{wall}})$ has its denominator growing while its numerator is constant in reasoning budget; the ratio must shrink (logarithm becomes more negative) or, more usually in practice, the agent over-corrects via narrative inflation and $\rho$ grows positive. Either way, $|\rho|$ is non-decreasing in reasoning budget.

**Promotion of $\tau_{\text{reason}}$**: where v1.2 listed $\tau_{\text{reason}}$ as auxiliary, we now treat it as a sub-axis of $\tau_{\text{step}}$ with its own measurement protocol. Closed-lab reasoning APIs report token counts but not chain durations; we estimate $\tau_{\text{reason}}$ from the difference between request-acknowledgement and first-emitted-output-token, calibrated to per-token rates measured in non-reasoning baselines.

The decomposition supplies the **mechanism that closes the Reverse-Scaling argument**, making it more than a structural sketch. We pre-register (Prediction P2′′′, §9) that $\rho$ grows monotonically in $\tau_{\text{reason}}/\tau_{\text{step, surface}}$ across the model panel.

### 5.8 The Chronoceptive Equation of State — A Speculative Unifying Hypothesis

The three law-metrics $(\alpha, \text{CAR}, \rho)$ might not be independent. The Augustine Problem framework predicts a structural relationship, which we formulate as an empirical hypothesis to be tested against the ChronoBench panel.

**The Chronoceptive Equation of State (CES, hypothesis)**. Across the model panel, the three law-metrics satisfy a model-invariant relationship of the form:

$$f\!\left(\alpha,\, \text{CAR},\, \rho;\, \tau_{\text{wall}}^{*},\, B,\, N_A\right) \;\approx\; \text{const}$$

The simplest concrete instance we conjecture, derived from the regime-transition picture of §5.2 and the hidden-time mechanism of §5.7, is:

$$\rho \;\approx\; c_1 \cdot \log_{10}\!\frac{\alpha}{\text{CAR}} \;+\; c_2$$

for model-independent constants $c_1, c_2$ — that is, a model's surface confabulation $\rho$ is determined (up to an additive constant) by the log-ratio of its budget-filling tendency to its budget-honoring tendency. The intuition: an agent that wildly inflates work ($\alpha$ large) but only honors a small fraction of the budget (CAR small) is the agent that most overstates its own duration; the three pathologies have a common origin and therefore co-vary.

If CES holds empirically, several consequences follow:

- The Three Times ontology has not three independent failure modes but a **single underlying degree of freedom** expressed three ways. The framework becomes more parsimonious, not less.
- The Augustine threshold $\varepsilon^{*}$ collapses to a single inequality on $\alpha/\text{CAR}$ rather than a weighted aggregate — easier to interpret, easier to audit.
- ChronoStack's intervention targets reduce: closing one of the three suffices to close the others.
- An analogue to thermodynamics' equations of state — where macroscopic quantities like pressure, volume, and temperature satisfy a model-invariant relationship — would suggest that chronoception is a *unified* property of the trained policy, not a sum of independent calibration failures.

CES is the framework's strongest unifying hypothesis. It is **speculative** in v1.4: we report it because it is the kind of result that would, if empirically supported, become the single most cited equation from the paper. It is the empirical analogue of the structural symmetry table of §5.1.

We pre-register (Prediction P7, §9) that the rank correlation between observed $\rho$ and $\log_{10}(\alpha/\text{CAR})$ across the model panel exceeds $0.7$.

## 6. Causal Upstream Hypothesis

Let $L(A, \mathcal{T}, B)$ denote the long-horizon task success rate of agent $A$ on benchmark $\mathcal{T}$ under budget $B$.

**Chronoception Upstream Hypothesis (CUH).** Chronoception is causally upstream of long-horizon agency:

$$\frac{\partial L}{\partial \varepsilon(A)} \;<\; 0, \qquad \text{causally.}$$

CUH is a **structural claim about the dependency order**, not a probabilistic conjecture. The reverse causal structure — long-horizon failure causing chronoceptive failure — is incompatible with the observability of chronoceptive failure on **single-turn tasks**. An agent that cannot estimate the duration of a five-second sub-action in isolation cannot have acquired that incapacity from long-horizon planning errors that have not yet occurred. The temporal precedence is fixed by the construction of the framework: $\varepsilon$ is measurable on horizons too short for $L$ to be defined, hence $\varepsilon \to L$ is the only admissible causal direction at the level of the framework.

**Operational test**. Construct two agents $A, A'$ matched on parameter count, training data, and inference-time compute, differing only in the presence of chronoceptive scaffolding (a wall-clock critic; cf. ChronoStack, Paper 2). The matched-baseline intervention isolates the chronoceptive component from confounders. CUH predicts $L(A'; \mathcal{T}, B) - L(A; \mathcal{T}, B) > 0$ on $\geq 3$ long-horizon benchmarks (SWE-Bench Verified, WebArena, GAIA).

CUH is the central claim that elevates this project from "a new evaluation axis" to "an explanation of long-horizon agent failure."

### 6.1 The Augustine Threshold $\varepsilon^*$ — A Paradigm Boundary

We define the **Augustine threshold** $\varepsilon^* := 0.20$. An agent satisfying $\varepsilon(A) < \varepsilon^*$ is *chronoceptively grounded*; otherwise *chronoceptively blind*. The threshold partitions the model panel of ChronoBench into two qualitative classes and supplies a single yes/no question that the framework asks of every newly released foundation-model agent: **has it crossed the Augustine threshold?**

The choice $\varepsilon^* = 0.20$ corresponds to a regime in which the agent's expected error contributes no more than one-fifth of the maximum possible across the three laws, jointly. It is conservatively chosen relative to the reference frontier range $\varepsilon \in [0.5, 1.2]$, leaving substantial headroom for capability improvement before "grounded" status is awarded.

**Paradigm-defining reading**. We propose a stronger reading of the threshold. Until $\varepsilon^*$ is crossed, the system is more accurately described as **a tool that can be called for variable durations** than as **an agent acting in time**. *Tool* and *agent* are not interchangeable: a tool is something operated by a user who supplies the temporal frame; an agent inhabits its own temporal frame. The Augustine threshold is the empirical boundary between the two categorizations. Systems above $\varepsilon^*$ should be deployed, evaluated, and regulated as tools — bounded by user-supplied time budgets, monitored for runaway, treated as functions of user attention. Systems below $\varepsilon^*$ become candidates for genuine agentic deployment in long-horizon, autonomous settings.

Under this reading, **no system released to date is an agent in the framework's sense**. The widespread industry usage of *agent* describes systems that are, in our terminology, **chronoceptively blind tools** wearing the agent label. We do not propose to rename the industry; we propose that any serious claim to autonomous agency requires crossing the Augustine threshold. ChronoBench supplies the test.

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
- **P6 (Closed-Lab Injection Audit, §5.5).** Of $\geq 10$ surveyed closed-lab frontier agent harnesses, $\geq 80\%$ install at least one of the three wall-clock injection mechanisms enumerated in §3.1. The Injection Tell is therefore a measurable industry footprint, not a rhetorical claim.
- **P2′′ (Retrospective/Prospective Asymmetry, §5.6).** Across the model panel, $|\rho_{\text{retro}}| - |\rho_{\text{prospective}}| \neq 0$ with statistically significant magnitude, and reasoning training amplifies $|\rho_{\text{prospective}}|$ more than $|\rho_{\text{retro}}|$ — reflecting the pre-decision locus of reasoning expansion.
- **P2′′′ (Hidden Time Mechanism, §5.7).** Across reasoning-tuned models with measurable $\tau_{\text{reason}}$, $|\rho|$ grows monotonically in $\tau_{\text{reason}}/\tau_{\text{step, surface}}$ — supplying the mechanism behind the Reverse-Scaling Theorem.
- **P7 (Chronoceptive Equation of State, §5.8).** Across the model panel, the rank correlation between observed $\rho$ and $\log_{10}(\alpha/\text{CAR})$ exceeds $0.7$ — supporting the conjecture that the three law-metrics have a common underlying degree of freedom.

These ten predictions constitute the project's pre-registration commitment.

### 9.5 Adjacent Phenomena — Chronoception Across Existing Problem Networks

Chronoceptive failure is not isolated. It connects to several well-known problems in current AI research; the framework gains explanatory leverage by making these connections explicit.

- **Goodhart's Law / reward hacking**. $\varepsilon$ is unhackable by construction because it is defined as a deviation from an identity that the agent's policy must enforce internally; an agent cannot game $\varepsilon$ by changing its outputs in any consistent direction. This contrasts with task-success benchmarks, which reward systems learn to exploit.
- **Robustness research**. Chronoception is a robustness axis. Adversarial inputs that perturb wall-clock interpretation (e.g., backdated timestamps) test the same representational structure that L1–L3 measure under benign conditions.
- **Calibration research**. $\varepsilon$ is a **meta-calibration** quantity — a calibration over time rather than over confidence. The literature on confidence calibration (Lin et al., 2022; Tian et al., 2023) measures whether $\Pr[\text{correct}]$ matches stated confidence; we measure whether duration estimates match realized time. The two axes are conceptually parallel and may correlate empirically.
- **AI safety**. A chronoceptively blind agent cannot honor wall-clock safety constraints — a kill-switch that triggers after $T$ seconds is moot for an agent that does not perceive $T$. The Augustine Problem is therefore upstream of multiple safety properties: time-bounded shutdown, deadline-honoring resource use, honest cost reporting.
- **The deception literature**. Temporal Confabulation (L3) is structurally adjacent to deception only if we believe the agent has access to ground-truth duration and chooses to misreport it. We do not; the model has no ground-truth duration internally. L3 is thus a *non-deceptive* hallucination — a more fundamental failure mode than deception, because it does not require intent. This distinction matters for AI safety frameworks that distinguish honest vs deceptive failure modes.

These connections are not contributions of the framework but show its **upstream position** in the network of current AI research problems. A reader who cares about Goodhart, robustness, calibration, safety, or deception finds chronoception relevant.

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
| Injection Atlas | Paper 1 empirical contribution | §5.5 — quantitative audit of closed-lab harness wall-clock injection mechanisms |
| The Phenomenology of Agent Time | Philosophical anchor | §3.5 — three modes of time (objective magnitude, lived duration, project horizon); LLM agents possess only the third partially |
| Chronoceptive Cost Calibration (CCC) | Derived metric | §4.5 — economic shadow of chronoception; cost-blindness downstream of time-blindness |
| Retrospective vs Prospective L3 (asymmetry) | Refinement of L3 | §5.6 — splits Temporal Confabulation into two distinct cognitive processes |
| Hidden Time $\tau_{\text{reason}}$ | Mechanism for reverse-scaling | §5.7 — sub-axis of $\tau_{\text{step}}$ supplying the mechanism behind §5.4 |
| Chronoceptive Equation of State (CES) | Unifying empirical hypothesis | §5.8 — model-invariant relationship $\rho \approx c_1 \log_{10}(\alpha/\text{CAR}) + c_2$ |
| Tool vs Agent paradigm boundary | Re-categorization claim | §6.1 — systems above $\varepsilon^{*}$ are tools, not agents, in the framework's sense |
| Adjacent Phenomena network | Upstream connections | §9.5 — chronoception is upstream of Goodhart, robustness, calibration, safety, deception |
| ChronoBench | Paper 1 artifact | Diagnostic benchmark over the three axes |
| ChronoStack | Paper 2 artifact | Training and inference-time framework for closing $\varepsilon$ |

## 12. Document Rules

1. This is the **source of truth**. Any conflict between this document and a downstream artifact (paper, README, slide, code comment) is resolved in favor of this document.
2. All symbols defined here are mirrored in `notation.tex` for LaTeX reuse. New papers begin by including that file.
3. Changes to §1–§6 (formal definitions, laws, central hypothesis) require an explicit framing-revision commit and a note in the changelog below.
4. Predictions (§9) are pre-registered. They are not to be modified after empirical work begins; failed predictions are reported as such.

## Changelog

- **v1.4 (2026-05-29)** — Three-round deep optimization pass. Add §0.0 The Headline as the project's single-paragraph irreducible statement. Add §3.5 The Phenomenology of Agent Time (three modes — objective magnitude, lived duration, project horizon — supplying the philosophical anchor that distinguishes the framework from a measurement gap). Add §4.5 Chronoceptive Cost Calibration (CCC) coupling chronoception to economic / safety cost-reporting. Add §5.6 Retrospective and Prospective L3 asymmetry, citing Wittmann (2009). Add §5.7 Hidden Time $\tau_{\text{reason}}$ as sub-axis of $\tau_{\text{step}}$, supplying the mechanism behind the Reverse-Scaling Theorem. Add §5.8 Chronoceptive Equation of State (CES) as a speculative unifying hypothesis. Upgrade §6.1 Augustine threshold to a paradigm boundary statement (tool vs agent re-categorization). Add §9.5 Adjacent Phenomena connecting chronoception upstream of Goodhart, robustness, calibration, safety, and deception. Add three new predictions: P2′′ (retro/prospective asymmetry), P2′′′ (hidden-time mechanism), P7 (CES). Pre-registration commitment now ten predictions. Vocabulary §11 extended with seven new entries.
- **v1.3 (2026-05-29)** — Overlap-resolution and novelty-reclaim pass. Add §0 Concurrent Work and Differentiation explicitly addressing Garikaparthi (2604.00010), Ma et al. *Timely Machine* (2601.16486), Cheng et al. *Temporally Blind* (2510.23853), Goel et al. *Chronocept* (2505.07637), and *Beyond pass@1* (2603.29231), enumerating retained novelty contributions. Add §5.5 Closed-Lab Injection Audit as a new quantitative empirical contribution converting the Injection Tell from rhetoric into measured industry footprint. Add Prediction P6 (Injection Audit ≥80%). Extend §11 vocabulary with *Injection Atlas*.
- **v1.2 (2026-05-29)** — Bold upgrade pass. §3 structural diagnosis rewritten as in-principle insufficiency of token-loss training (wall-clock is out of the loss support). §3.1 Injection Tell upgraded from "implicit acknowledgement" to "decisive non-experimental evidence". §5 extended with §5.2 (Regime Transition $B^*$ reconciling L1 and L2), §5.3 ($N_A$ as model invariant), §5.4 (Reverse-Scaling Theorem). §6 CUH recast as a structural claim from single-turn observability of $\varepsilon$. §6.1 introduces Augustine threshold $\varepsilon^* = 0.20$. §9 adds Prediction P2′ (Reverse-Scaling) and P5 (no released model crosses Augustine threshold). Locked vocabulary §11 extended with five new entries.
- **v1.1 (2026-05-28)** — Add §3.1 The Injection Tell formalizing the role of closed-lab wall-clock injection as confirmatory evidence, and partitioning evaluation into Setting A (no-injection) / Setting B (with-injection). Replace P1 with a two-armed Injection Tell prediction (P1a, P1b) tied to T1.1 / T1.3 / T2.3 / T3.1.
- **v1.0 (2026-05-28)** — Initial locked version. Establishes Three Times ontology, three named laws, $\varepsilon$ as central scalar, CUH, and four falsifiable predictions.
