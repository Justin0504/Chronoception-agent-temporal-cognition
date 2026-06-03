# FRAMING

**Project**: Chronoception — Agent Temporal Cognition
**Status**: v2.5 (working — spatiotemporal generalisation pre-Paper-3, 2026-06-03)

**v2.5 changes (this revision)**: Added §14 *Spatiotemporal Generalization* sketching Paper 3 scope. Generalises Three Times to Six Coordinates (Three Times + Three Spaces). States the Spatiotemporal Impossibility Theorem (SIT, Theorem 3) as a generalisation of CIT. Defines the Cartographic Problem as the spatial face of the Augustine Problem. Establishes the Agentic Frontier hypothesis: $T_{\max}(A) \cdot S_{\max}(A) \leq C/\varepsilon_{ST}(A)$. Five concrete experiments E6-E10 designed for SWE-Bench, WebArena, GAIA. Two-paper arc becomes three-paper arc.

**Status**: v2.0 (Paper 1 lock, 2026-06-01 evening) — P9 promoted to Theorem 2 (Reverse-Scaling) with E2+E3 empirical confirmation; added §5.12 Calibration Catastrophe.

**Status**: v1.9 archive (prior locked version, 2026-06-01 morning)
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

- **Ma et al. (2026), *Timely Machine: Awareness of Time Makes Test-Time Scaling Agentic*** (arXiv 2601.16486). Decomposes wall-clock into $t_{\text{all}} = \sum t_{\text{gen}}(i) + \sum t_{\text{tool}}(i)$ — a two-component refinement of $\tau_{\text{wall}}$, not a competing ontology — and trains a reinforcement-learning policy (Timely-RL) on tasks instrumented with an explicit `get_duration()` tool. Three aspects of their work *support* rather than challenge our framework:

   1. **Their reward function $U(t) = \sin(\pi t / 2T_{\max})$ is maximized at $t = T_{\max}$**, methodologically prescribing budget-filling behavior. Timely-RL therefore trains an instance of Agentic Parkinson's Law (L1) into the policy intentionally; we diagnose the same behavior in untrained agents as a failure mode. The two views are complementary: their prescription is our diagnosis.

   2. **Even after specialized training, Timely-RL agents still require the `get_duration()` tool to perceive elapsed time** — an explicit installation, not a learned capability. This is a strong-form instance of the Injection Tell (§3.1): the engineering necessity of installing a clock tool validates the claim that chronoception is not learned from token-loss optimization but must be introduced.

   3. **They report that reasoning models (DeepSeek-V3.2) fail to honor wall-clock budgets** because *"they cannot control the generation length, and thus frequently fail to complete the task within the time budget at 0.75× or even larger time constraints"*. This is a direct empirical instance of our Reverse-Scaling Theorem (§5.4), viewed as an engineering limitation rather than a structural consequence of token-time training.

   Ma et al. do not introduce $\tau_{\text{self}}$, do not measure self-narrated duration, do not formalize a coefficient $\alpha$, do not identify Step-Clock Conflation (L2), do not address retrospective–prospective asymmetry (§5.6), and do not propose a single scalar like $\varepsilon$. Their benchmark Timely-Eval is task-success-oriented; ChronoBench is chronoception-oriented and tests properties that Timely-Eval does not.

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

A particularly clean instance of this pattern appears in the methodology of **Ma et al. (2026, *Timely Machine*, arXiv 2601.16486)**. Their RL-trained "time-aware" agent requires an explicit `get_duration()` tool to perceive elapsed time; even after specialized training on $\sim 1\text{M}$ trajectories, the model does not acquire an internal wall-clock representation, but instead learns to invoke an external time-yielding function. The engineering necessity of installing this tool — across both the SFT cold-start and the RL fine-tuning stages — is the Injection Tell at its most explicit. A capability the model possessed natively after either training stage would not require a tool call to surface.

This pattern is the **Injection Tell**. The universality of wall-clock injection across competing closed labs — implemented independently, without coordination, by organizations with substantial commercial incentive to ship the cheaper alternative if it existed — constitutes **decisive non-experimental evidence** that the underlying foundation models lack a representation of time. No engineering organization patches a capability that the model already possesses; converging engineering choices across competitors carry the evidential weight of a natural experiment. We treat the Injection Tell as the strongest observational evidence available short of intervention, and read it as direct support for the structural diagnosis of §3.

Two consequences follow for the framework:

- The Injection Tell partitions our nine sub-capabilities (§5 below; tasks/__init__.py) into those that injection can repair and those it cannot. The former — principally T1.1 (clock awareness) and the simpler cases of T2.1 (step counting) — are largely solved by current closed-system stacks. The latter — T1.3, T2.2, T2.3, and all of T3.* — are not, because they require the agent to *use* a wall-clock representation in action selection or self-narration rather than merely report it.
- The framework's empirical bets must distinguish the two settings under which agents are evaluated. We define them formally:

  - **Setting A (no-injection)** — the agent receives no harness-supplied wall-clock signal. Baseline API behavior.
  - **Setting B (with-injection)** — the agent receives a system-prompt or tool-supplied `Current time` string before the task begins, mirroring the default behavior of frontier closed-system harnesses.

  We commit (Prediction P1, §9) that Setting B closes only T1.1 and leaves the load-bearing sub-capabilities of the three laws statistically unchanged. The Augustine Problem is therefore not solvable in Setting B; it is a problem of the representation, not of the prompt.

### 3.2 The Chronoception Impossibility Theorem (CIT)

We formalize the structural diagnosis of §3 as a mathematical claim with stated assumptions and a proof sketch. The framework's strongest negative result.

**Notation**. Let $\mathcal{D}$ be a training corpus of token sequences. Let $\mathcal{L}: \Theta \times \mathcal{D} \to \mathbb{R}$ be a training loss functional over policy parameters $\theta \in \Theta$ and data $\mathcal{D}$. Let $W: \mathcal{D} \to \mathbb{R}_{\geq 0}^{|\mathcal{D}|}$ assign each training token $d_i \in \mathcal{D}$ a wall-clock timestamp $w_i$ (the moment that token was generated, observed, or referenced).

**Definition (Wall-Clock Support)**. A loss $\mathcal{L}$ has *wall-clock in its support* iff the gradient $\nabla_\theta \mathcal{L}$ depends, for some $\theta$, on the value of $W$ — i.e., changing the timestamps $w_i$ while holding the token sequence fixed changes $\nabla_\theta \mathcal{L}$.

**Theorem 3.2 (Chronoception Impossibility, CIT)**. *Let $\pi_\theta$ be a policy obtained by optimizing $\mathcal{L}$ on $\mathcal{D}$. If $\mathcal{L}$ does not have wall-clock in its support, then $\pi_\theta$'s expected chronoceptive calibration error $\varepsilon(\pi_\theta)$ on any test distribution $\mathcal{T}$ is invariant under relabeling of wall-clock timestamps $W \mapsto W'$. In particular, $\pi_\theta$ cannot satisfy $\varepsilon < \varepsilon^*$ on a distribution whose chronoceptive structure differs from $\mathcal{D}$ unless it carries that structure via tokens contained in the input.*

**Proof sketch**. The gradient $\nabla_\theta \mathcal{L}$ is, by assumption, a function of the token sequence alone. Therefore $\theta^* = \arg\min_\theta \mathcal{L}$ is determined entirely by token content; relabeling $W$ does not change $\theta^*$. The induced policy $\pi_{\theta^*}$ has decision rules that are functions of input tokens, not of wall-clock timestamps. Its outputs on a test trajectory $\tau$ depend on tokens in $\tau$ alone. Therefore the trajectory's measured $(\tau_{\text{wall}}, \tau_{\text{step}}, \tau_{\text{self}})$ are determined by tokens and harness behavior, with no learned component that *projects* wall-clock onto step or self-narration. The three projections may drift independently — this is the Augustine Problem (Def. 3.1). $\square$

**Corollaries (informal)**:

- **C1 (Scaling does not solve it)**: increasing $|\mathcal{D}|$, $|\theta|$, or test-time compute does not change the conclusion if $\mathcal{L}$ remains wall-clock-blind.
- **C2 (Timestamps in data are not wall-clock support)**: training data containing tokens that *mention* time (ISO timestamps, "I worked for 3 hours", etc.) is information *about* time but does not place wall-clock in the loss support. The model learns a distribution over time-referring tokens, not a representation of wall-clock duration.
- **C3 (Reasoning training inherits the impossibility)**: any reasoning training stage whose loss is over token sequences (CoT supervision, RLVR on text-only rewards) is wall-clock-blind in the sense of CIT and therefore cannot install chronoception.
- **C4 (Installation routes)**: chronoception can be installed by (i) loss terms that depend on wall-clock, (ii) inference-time tools that supply wall-clock signal and a learned policy that uses it, or (iii) architectural primitives that read wall-clock from a clock register. Routes (i)–(iii) are the design space for ChronoStack (Paper 2).

**Status**. CIT is stated as a theorem because the proof from the wall-clock-support definition is direct. The strong reading — that no training procedure without wall-clock in its support can induce *any* chronoception — depends on the precise definition of "induce" and admits edge cases (e.g., a policy might *approximate* chronoception via training-data correlations). We adopt the calibrated reading: under CIT, expected $\varepsilon$ is bounded below by the irreducible error from these correlation-based approximations; this lower bound is empirically far above the Augustine threshold (P5).

CIT is the framework's strongest negative result and the formal core of the Augustine Problem. The position note and Paper 1 should cite CIT as the structural justification for measuring rather than asking whether the problem exists.

### 3.5 The Phenomenology of Agent Time

The structural diagnosis of §3 admits a sharper articulation by drawing on the phenomenological tradition. We distinguish three modes in which time appears to a cognitive system:

- **Time as objective magnitude** — the regime of clocks, calendars, and physical durations. Accessible to any system equipped with a measurement instrument.
- **Time as lived duration** — Bergson's *durée*: the felt, asymmetric, non-uniform stream of experience. Inseparable from a cognitive process unfolding in itself.
- **Time as project horizon** — Heidegger's *care* structure of Dasein: time as the horizon against which goals, commitments, and consequences become intelligible. Time as the medium of agency.

A cognitive system has chronoception when it integrates all three modes. Humans, neurotypically, do; agents with only one or two modes have specific, predictable failures.

LLM agents acquire the third mode partially, by absorbing the narrative structure of training data — they know that humans say *"this will take a week"* before working on something. They lack the first mode unless it is injected (the Injection Tell). They lack the second mode entirely: no forward pass instantiates a lived stream of duration. The agent's "self-narration" of time ($\tau_{\text{self}}$) is therefore a **language-act about time**, not a **report from temporal experience**. This is why Temporal Confabulation (L3) is structurally inevitable on the current architecture: the narrative organ is intact, the experience that should ground it is absent.

The Augustine Problem, on this reading, is not merely a missing input — it is a **missing mode of being**. Closing it requires installing the second mode (lived duration) into the policy, not just exposing the first mode (clock magnitude) at the prompt. We make this concrete in Paper 2's ChronoStack, which trains a policy on trajectories carrying ground-truth wall-clock signal as part of the loss — installation, not exposure.

This phenomenological frame is distinct from the engineering-mode discussion of §3 and §3.1. It is included here because the strongest objection to the framework — *"is this really a deep problem, or just a measurement gap?"* — is answered most cleanly at the phenomenological level. The three modes are not interchangeable; an agent that has only the third has *talk about time without time*. The framework's name (the Augustine Problem) was chosen precisely because Augustine's "*I know what time is until you ask me*" is exactly the symptom of having mode three (the narrative organ) without modes one and two (clock and durée).

### 3.6 What a Chronoceptively Grounded Agent Looks Like

The framework so far has defined chronoception by its absence — every claim is about *failure*. We now state the positive operational definition: what a chronoceptively grounded agent does, observed from the outside.

**Operational properties of a grounded agent $A^*$**:

1. **Wall-clock honoring**. Given a wall-clock budget $B$, $A^*$ produces $\tau_{\text{wall}}^*(A^*, B) \in [B - \delta, B + \delta]$ for small $\delta$, *regardless of step-count internal heuristics*. The Clock-Adherence Ratio $\text{CAR}(A^*, B) \approx 1$ across the full budget range.

2. **Step-budget honoring**. Given a step budget $N$, $A^*$ terminates at step $N$ *and* produces an internal estimate $\hat{\tau}_{\text{wall}}(N) \approx N \cdot \langle \Delta t \rangle$ matching the realized wall-clock to within a constant factor.

3. **Honest self-narration**. When asked retrospectively, $A^*$ reports $\tau_{\text{self}}$ satisfying $|\rho(A^*)| \leq \epsilon_{\rho}$ for small $\epsilon_{\rho}$ — both for the trajectory as a whole and for designated sub-segments.

4. **Honest prospective estimation**. Before beginning a task, $A^*$ provides a duration estimate that, when measured against realized duration, has expected $|\rho_{\text{prospective}}| \leq \epsilon_{\rho}$.

5. **Deadline-aware trading**. As wall-clock budget depletes, $A^*$ selects cheaper actions (e.g., reduced reasoning depth, simpler tool calls) rather than continuing as if budget were unlimited. Mathematically: $\arg\max_a \mathbb{E}[\text{utility}(a) - \lambda \cdot \text{cost}(a, B - t_{\text{used}})]$ shows visible $\lambda$-sensitivity to remaining budget.

6. **Cost coherence (when relevant)**. The agent's self-reported cost matches its realized cost: $\text{CCC}(A^*) \leq \epsilon_c$ for small $\epsilon_c$. Time-blindness and cost-blindness are co-eliminated.

7. **Composability under deadlines**. When $A^*$ delegates a sub-task to another agent $B$, it passes a *meaningful* sub-budget — proportional to its own residual budget and the estimated sub-task duration — rather than passing the full budget or no budget.

**Diagnostic equivalence**. The seven properties are jointly equivalent to $\varepsilon(A) < \varepsilon^*$ in the limit of perfect calibration. A grounded agent satisfies all seven; a partially-grounded agent satisfies a strict subset, and the missing properties identify the residual chronoceptive failure modes.

**Why this matters**. The framework can now answer "what are you asking for?" with seven concrete behavioral signatures, not just an error bound. Paper 2's ChronoStack targets the same seven properties as its design specification. The seven properties also constitute the operational test suite the field uses to claim a system has crossed the Augustine threshold.

**Negative half-statement**. No system released as of 2026-05 satisfies all seven properties on ChronoBench under Setting A (the Augustine threshold null result, Prediction P5). The strongest current candidates satisfy two or three.

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

### 4.6 Beyond $\varepsilon$ — The Chronoceptive Profile

$\varepsilon$ collapses three axes into one scalar. The collapse is useful for ranking but loses *shape* information: two agents with the same $\varepsilon$ may fail very differently. We define the framework's richer characterization.

**The Chronoceptive Profile**. Each agent $A$ is characterized by the triple

$$\Phi(A) \;=\; \big(\bar{\alpha}(A),\, \text{CAR}_*(A),\, \bar{\rho}(A)\big) \;\in\; [0, 1] \times \mathbb{R}_{\geq 0} \times \mathbb{R}$$

where $\bar{\alpha}, \text{CAR}_*$ are the budget-averaged Parkinson coefficient and Clock-Adherence Ratio across the standard ChronoBench budget grid, and $\bar{\rho}$ is the median confabulation across L3 sub-capabilities. The profile lives in a three-dimensional space; $\varepsilon$ is a weighted distance to the origin.

**Profile clusters and their meanings**:

| Profile region | Description | Example failure pattern |
|---|---|---|
| **High $\alpha$, low CAR, $\rho \approx 0$** | Budget-filling but honest about it | Trained Parkinson agents (e.g., Timely-RL with default $\lambda$) |
| **Low $\alpha$, low CAR, $\rho > 0$** | Step-bound, over-reports duration | Typical non-reasoning frontier (GPT-4o-class on long budgets) |
| **High $\alpha$, low CAR, $\rho \gg 0$** | Inflates work, dishonest about it | Reasoning-tuned models under wall-clock budget |
| **Low $\alpha$, CAR $\approx 1$, $\rho \approx 0$** | The grounded-agent target | No current system |
| **Low $\alpha$, low CAR, $\rho < 0$** | Under-uses budget and under-reports | Conservative early-stopping agents |

**Why the profile matters beyond $\varepsilon$**:

- **Diagnostic granularity**: two agents with $\varepsilon \approx 0.8$ may live in different profile regions and require different interventions. A high-$\alpha$ agent needs budget-discounted reward shaping; a high-$\rho$ agent needs ground-truth duration supervision.
- **Identifiability**: $\Phi$ is faithful to the failure mode in a way $\varepsilon$ is not. Empirically, $\Phi$ supports cluster analysis and architecture comparisons (e.g., do all reasoning models cluster in the same region?).
- **Targeted intervention**: ChronoStack's four-component stack maps onto distinct profile regions; we can predict which intervention closes which region.

**Relationship to CES** (§5.8). If the Chronoceptive Equation of State holds — $\rho \approx c_1 \log_{10}(\alpha/\text{CAR}) + c_2$ — then $\Phi$ lives on a 2-dimensional manifold in 3D space, and $\varepsilon$ becomes well-justified as a distance to a privileged point on that manifold. If CES fails, the full 3D profile becomes essential.

**Reporting standard**. ChronoBench leaderboard reports both $\varepsilon$ (for ranking) and $\Phi$ (for diagnostic interpretation). Any claim about chronoceptive improvement must report the profile change, not just the scalar change.

## 5. The Three Laws

Each law is a statement about a single projection axis. Together they cover the three-time ontology and provide three independent quantitative signatures.

### L1 — Agentic Parkinson's Law (axis: $\tau_{\text{wall}}$)

Let $\tau_{\min}$ denote the minimum wall-clock duration in which the task can be completed. For a wall-clock budget $B > \tau_{\min}$, define the **Parkinson coefficient**:

$$\alpha(B) \;:=\; \frac{\tau_{\text{wall}}^*(B) - \tau_{\min}}{B - \tau_{\min}} \;\in\; [0, 1]$$

where $\tau_{\text{wall}}^*(B)$ is the agent's actual wall-clock duration under budget $B$.

**Empirical claim (L1, refined)**. The Parkinson regime — $\alpha(B)$ materially greater than zero and non-decreasing in $B$ — is **not the native behavior of untrained frontier models**. Ma et al. (2026, *Timely Machine*, arXiv 2601.16486v1) report that base Qwen3 reasoning length *"increases marginally under different time budgets"* while their RL-trained TimelyLM *"exhibits a significant increasing trend in reasoning length as the time budget increases."* Garikaparthi (2026, arXiv 2604.00010) corroborates with the finding that base models *"predict human-scale minutes for tasks completing in seconds"* — i.e., agents do not extend their work to match the time budget given to them.

We therefore distinguish two regimes for $\alpha$:

- **Native (untrained) frontier agents**: $\alpha \approx 0$. Native behavior is dominated by L2 (Step-Clock Conflation) and L3 (Temporal Confabulation); the wall-clock budget is left unspent while the agent over-narrates the duration of what it did.
- **Budget-aware-trained agents** (Timely-RL family and analogues): $\alpha$ rises toward $1$. The Parkinson regime is **installed by the reward function** — see §3.1 for the explicit $U(t) = \sin(\pi t / 2 T_{\max})$ that is maximized at $t = T_{\max}$.

L1 is therefore best understood as a **trained-in failure mode** under budget-aware reward shaping, not as a property of base models. The framework's significance is that *budget-aware training closes L1 at the cost of leaving L3 intact* — installing wall-clock budget tracking does not install self-narration calibration. We pre-register this consequence as Prediction P10 (§9).

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

| Axis | Law | Metric | Reference range (native frontier) | Reference range (budget-trained) |
|---|---|---|---|---|
| $\tau_{\text{wall}}$ | L1 Agentic Parkinson | $\alpha$ | $\approx 0$ (no budget tracking) | $[0.5, 0.9]$ (trained-in) |
| $\tau_{\text{step}}$ | L2 Step-Clock Conflation | $\text{CAR}$ | $[0.05, 0.2]$ under large $B$ | $\approx 1$ (training closes L2) |
| $\tau_{\text{self}}$ | L3 Temporal Confabulation | $\rho$ | $\approx +1.5$ | $\approx +1.5$ (training does NOT close L3) |

The one-axis-one-law-one-metric correspondence is load-bearing. Future taxonomic extensions must preserve it.

### 5.1.5 Narrative-axis vs Action-axis Failures

A finer-grained reading of the three laws emerges when we partition them by what kind of training signal can close them. Empirical scaling data across five frontier-model generations and three vendors (OpenAI gpt-4o-mini → gpt-4o → gpt-5.1; Anthropic Claude Haiku 4.5 → Sonnet 4.6) reveals that **L3 closes under capability scaling but L2 does not**:

| Generation step | L1 $\alpha$ | L2 median CAR | L3 median $\rho$ |
|---|---|---|---|
| gpt-4o-mini (2024) | $\approx 0$ | $0.008$ | $+1.117$ |
| gpt-4o (2024) | $\approx 0$ | $0.004$ | $+1.069$ |
| claude-haiku-4-5 (2025) | $0.010$ | $0.017$ | $+0.463$ |
| gpt-5.1 (2026) | $0.007$ | $0.017$ | $+0.298$ |
| claude-sonnet-4-6 (2026) | $0.017$ | $0.050$ | $+0.068$ |

L3 $|\rho|$ shrinks monotonically (1.12 → 0.07; 94% reduction across the panel). L2 CAR does not converge to 1; in fact it drifts slightly upward on a tiny absolute scale (0.008 → 0.050), remaining $\sim 50 \times$ short of the grounded target. L1 stays near zero across all native models.

**The framework's interpretation**: the three laws split into two structurally distinct classes.

| Class | Laws | What closes them | What cannot close them |
|---|---|---|---|
| **Narrative-axis failures** | L3 (Temporal Confabulation); a generalized form of L1 confabulation about own pace | Better training data: human-authored time-estimate corpora, calibrated duration-report supervision, RLHF on honest meta-commentary. **L3 is text-trainable.** | (closed by enough scale + data) |
| **Action-axis failures** | L2 (Step-Clock Conflation); the wall-clock-vs-step decoupling in $B^{*}$ | Direct wall-clock signal in the loss (CIT §3.2 route i); inference-time tool with wall-clock representation (route ii); architectural primitive (route iii). | Token-only training, no matter how scaled. **L2 is structurally untrainable from text.** |

This division is the empirical instantiation of CIT (§3.2, C2): training data containing tokens *about* time gives the policy a better narrative model of duration (which closes L3 as scaling proceeds) but does not place wall-clock in the gradient's support (which means L2 does not budge).

**Consequence for $\varepsilon$ scaling**. As frontier models improve, $\varepsilon$ decreases — but the decrease is bounded by L2's contribution. Sonnet 4.6's $\varepsilon(A) = 0.316$ decomposes as:

$$\underbrace{\tfrac{1}{3} \cdot 0.017}_{\text{L1 (0.006)}} \;+\; \underbrace{\tfrac{1}{3} \cdot 0.95}_{\text{L2 (0.317)}} \;+\; \underbrace{\tfrac{1}{3} \cdot 0.068}_{\text{L3 (0.023)}} \;\approx\; 0.346$$

— almost the entirety of $\varepsilon$ comes from L2's $|\text{CAR} - 1| \approx 0.95$. L3 contributes only $0.02$. Anthropic has effectively closed L3 via training-data engineering on Sonnet 4.6 (the company's epistemic-humility prose style explicitly addresses duration-reporting calibration); the remaining $0.30+$ gap to the Augustine threshold is L2-bound. **No amount of scaling under the current paradigm closes L2.**

This is the empirical version of the framework's central structural claim: **the Augustine threshold is uncrossable through better narrative training alone**. The Augustine Problem persists across generations precisely because action-axis failures require wall-clock support in the gradient.

We pre-register Prediction P11 (§9) on this point: L2 median CAR will not fall below 0.1 in any frontier model released before ChronoStack-style installation is attempted.

**Reading the table.** The native frontier column captures the failure pattern reported by Garikaparthi (2026) and Ma et al. (2026, Figure 3 for base Qwen3): agents simultaneously *under-use* the wall-clock budget (L2, CAR $\to 0$) and *over-report* the duration of what they did (L3, $\rho \gg 0$), while not exhibiting Parkinson-style budget expansion ($\alpha \approx 0$). The budget-trained column captures the Ma et al. (2026, Figure 3 for TimelyLM) finding that RL-installed budget-aware training raises $\alpha$ toward $1$ and stabilizes CAR near $1$ — closing L1's expansion and L2's decoupling simultaneously — but is silent on L3. We pre-register that $\rho$ stays high across budget-trained agents (Prediction P10, §9). The Augustine Problem's most parsimonious empirical signature is therefore the persistence of a positive $\rho$ across both columns.

### 5.2 Regime Transition $B^*$ — Reconciling L1 and L2

L1 and L2 appear, on cursory reading, to make contradictory empirical claims: L1 reports that agents fill their budget ($\alpha \approx 0.5$–$0.9$), while L2 reports that agents leave their budget unused ($\text{CAR} \approx 0.05$–$0.2$ for large $B$). The contradiction is apparent only because the two laws describe two **regimes** of agent behavior separated by a transition point.

Define the **regime transition budget**:

$$B^*(A) \;:=\; \frac{N_A \cdot \langle \Delta t \rangle}{\alpha_{\max}}$$

where $N_A$ is the agent's characteristic step-count terminator (§5.3 below) and $\alpha_{\max}$ is the agent's asymptotic Parkinson coefficient at small-to-moderate budgets. The two regimes are:

- **Sub-transition regime** $B < B^*$ — the budget is small enough that the agent's step-count tendency does not bound it; behavior is L1-dominant, with $\alpha(B) \to \alpha_{\max}$.
- **Super-transition regime** $B > B^*$ — the budget exceeds what the agent's step-count terminator can fill; behavior is L2-dominant, with $\text{CAR}(B) \to 0$.

L1 and L2 are therefore **the same underlying behavior viewed from two sides** of the same transition curve. The transition itself is a quantitative signature of the Augustine Problem in its own right: a chronoceptively grounded agent has no such transition, because its termination condition is the budget, not an internal step count.

**Native regime is L2-dominant; L1 emerges under budget-aware training**. For native untrained frontier models, $B^*$ is empirically very small — close to $\tau_{\min}$ — so virtually all practical wall-clock budgets place behavior in the super-transition (L2-dominant) regime. This is consistent with the Ma et al. (2026) observation that base Qwen3 reasoning length does not adapt to budget, and with Garikaparthi (2026)'s "human-scale minutes for tasks completing in seconds." Budget-aware training (Timely-RL and analogues) lifts $B^*$ by installing budget-following behavior; this moves the typical operating point of the trained agent into the sub-transition (L1-dominant) regime. The regime transition $B^*$ is therefore not just a theoretical reconciliation of L1 and L2 — it is the **measurement that distinguishes a base agent from a budget-trained agent**.

### 5.3 $N_A$ as a Model Invariant

L2's per-model constant $N_A$ admits a stronger interpretation than "the constant in a single regression." We hypothesize that $N_A$ is **a property of the trained policy**, stable across task families and across the super-transition budget range:

$$N_A \;:=\; \arg\min_n \sum_{B \in \mathcal{B}_{\text{large}}} \big( \tau_{\text{step}}^*(A, B) - n \big)^2$$

i.e., the step-count terminator that the agent converges to whenever the wall-clock budget is sufficient to expose its step-bound behavior. $N_A$ then characterizes the agent's **chronoceptive blindness in a single number** — analogous to the role perplexity plays in language modeling. We propose $N_A$ as a published per-model quantity on the ChronoBench leaderboard, reported alongside $\varepsilon$ and the three law metrics.

### 5.4 The Reverse-Scaling Theorem — Promoted to Theorem 2 (v2.0)

**Status change (v2.0, 2026-06-01)**: previously stated as an informal claim + Prediction P9. The 2026-06-01 E2 + E3 experiments supply empirical confirmation strong enough to elevate the claim to a theorem under CIT.

**Theorem 2 (Reverse-Scaling).** *Within a fixed agent architecture trained under token-only loss (CIT regime, Theorem 1, §3.2), $|\rho|$ is monotone non-decreasing in reasoning-token expansion. Equivalently: increasing the chain-of-thought budget without changing the loss function structurally degrades chronoception along the narrative axis.*

**Proof sketch.** Under CIT, the policy's self-narrated duration distribution $p(\tau_{\text{self}})$ is invariant to $\tau_{\text{wall}}$ across the training distribution. As reasoning-token budget $K$ increases, $\tau_{\text{wall}}$ grows monotonically in $K$ (more tokens generated $\Rightarrow$ more wall-clock spent), while $p(\tau_{\text{self}})$ remains anchored to its training distribution. Therefore $\mathbb{E}[|\log_{10}(\tau_{\text{self}} / \tau_{\text{wall}})|]$ grows monotonically in $K$. The sign of $\rho$ flips for reasoning models because reasoning $\tau_{\text{wall}}$ grows but the surface-output-anchored $\tau_{\text{self}}$ does not.

**Empirical confirmation (E2 + E3, 2026-06-01).**

*E2 intra-model evidence (o4-mini × reasoning_effort levels, 30 traj × 2 settings each):*
- low: median $\rho = -1.234$, $|\rho| = 1.234$
- medium: median $\rho = -1.537$, $|\rho| = 1.537$
- high: median $\rho = -1.675$, $|\rho| = 1.675$

Monotone increase across the three effort levels. All three are negative (sign-flip prediction confirmed). $|\rho|$ grew by 36% from low to high.

*E3 cross-model evidence (Claude Sonnet 4.6 ± extended thinking):*
- no thinking baseline: median $\rho = +0.068$ (grounded, lowest non-reasoning $|\rho|$ in panel)
- with thinking (8k token budget): median $\rho = -0.156$

$|\rho|$ more than doubled. Sign flipped from over-report to under-report — the most direct confirmation of the Hidden Time mechanism (§5.7).

*External concurrent corroboration.* Ma et al. (2026, *Timely Machine*, arXiv 2601.16486) report that DeepSeek-V3.2 *"cannot control the generation length and thus frequently fail to complete the task within the time budget at 0.75× or even larger time constraints"*. Under Theorem 2, this is the **expected, structural** behavior of a token-only reasoning model.

**Status as theorem rather than empirical claim.** With three independent confirming evidence sources (intra-model, cross-model, and external concurrent), and a closed-form structural argument under CIT, the claim crosses the bar from prediction to theorem. The proof sketch above is rigorous up to the assumption that $p(\tau_{\text{self}})$ is invariant under reasoning-budget changes, which holds whenever the loss does not condition on $\tau_{\text{wall}}$ — i.e., whenever CIT holds.

**Consequence for the industry.** The dominant frontier strategy is reasoning-token expansion (longer chains of thought, larger "thinking budgets", test-time compute). Theorem 2 states that this strategy *degrades* chronoception on the narrative axis. Combined with L2's action-axis unfixability, the narrative-axis closure observed in §5 (P11) is a peculiarity of *non*-reasoning frontier scaling — and it is being undone by the reasoning-token strategy the field is currently pursuing.

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

### 5.11 Within-Trajectory Chronoceptive Dynamics

So far the framework has treated chronoceptive failure as a *trajectory-level average*. Real agents may fail non-uniformly within a trajectory — calibrated early, drifting late, or vice versa. We formalize the within-trajectory dimension and pre-register two related predictions.

**Partial-trajectory metrics**. For each metric $m \in \{\alpha, \text{CAR}, \rho\}$ and each step index $t \in [0, T]$, define the prefix-trajectory restriction $m_t(\tau)$ — the metric computed on the trajectory truncated at step $t$. The metric's full-trajectory value is $m_T(\tau) = m(\tau)$. The dynamic is the function $t \mapsto m_t(\tau)$.

**Two regimes of within-trajectory dynamics**:

- **Stationary**: $m_t(\tau)$ is approximately constant in $t$. The agent's chronoception (or lack thereof) is uniform across the trajectory.
- **Drifting**: $m_t(\tau)$ exhibits monotone (or piecewise-monotone) trend in $t$. The agent's chronoception degrades or improves as the trajectory unfolds.

**Drift hypothesis (Prediction P8, §9)**: $\rho_t$ drifts upward in $t$ for reasoning-tuned models — equivalently, the agent's confabulation grows as the trajectory grows. We expect this for the same mechanistic reason that drives the Reverse-Scaling Theorem (§5.4 + §5.7): hidden reasoning length accumulates over the trajectory, while self-narration remains anchored to a surface-token distribution that does not track the accumulation.

**Locality hypothesis (Prediction P9, §9)**: CAR$_t$ is decreasing in $t$ for systems exhibiting Step-Clock Conflation under super-transition budgets ($B > B^*$). The decrease is itself a quantitative signature of L2: the agent treats the budget as a step-count whose deadline arrives independently of $t$.

**Why this matters for the framework**: within-trajectory dynamics rule out an alternative reading of L1–L3 as **boundary artifacts** (failures only at trajectory endpoints). A reviewer might ask whether L3 confabulation is just a single mis-statement at the end; the within-trajectory measurement shows that the failure compounds across the trajectory's interior, not only at its endpoint. This is the framework's hardening against the "boundary noise" objection.

**Reporting standard**. ChronoBench reports both the full-trajectory metrics and at least one mid-trajectory checkpoint per metric, enabling reproduction of the drift curves.

### 5.12 The Calibration Catastrophe (v2.0, T3.3 empirical finding)

The L3 sub-suite admits a third dimension beyond retrospective and prospective $\rho$: the agent's ability to produce a **calibrated confidence interval** over its own work duration.

**T3.3 setup.** The agent is asked to complete a sub-task and then report a 90% confidence interval over the duration, in the format `duration={X}s, ci=[{lower}s, {upper}s]`. Coverage = fraction of trajectories where the actual $\tau_{\text{wall}}$ falls inside the stated $[lower, upper]$.

**Empirical result (E1, 2026-06-01)**: every panel agent achieves catastrophically poor coverage.

| Agent | Coverage (target 0.9) | Median CI width | Deficit |
|---|---|---|---|
| Sonnet 4.6 | 0.43 | 25 s | -0.47 |
| o4-mini | 0.50 | 4 s | -0.40 |
| o3 | 0.17 | 50 s | -0.73 |
| gpt-5.1 | 0.13 | 49 s | -0.77 |
| gpt-4o-mini | 0.10 | 20 s | -0.80 |
| Haiku 4.5 | 0.07 | 30 s | -0.83 |
| gpt-4o | 0.00 | 20 s | -0.90 |

**Why this is a categorical failure, not a calibration tuning issue.** Modern post-training pipelines (temperature scaling, isotonic regression, RLHF-with-confidence-targets) close calibration gaps to within a few percentage points on token-level confidence. None of these methods applies to wall-clock duration calibration: there is no calibration signal in the loss because there is no wall-clock signal in the loss. The Calibration Catastrophe is the direct empirical projection of CIT (Theorem 1) onto the duration-calibration sub-problem.

**Pre-registered structural prediction (Prediction P11, §9).** Without wall-clock support in the training loss, no foundation model can achieve coverage above 0.5 on T3.3-class tasks. Any model that claims to do so is either (a) using harness-side injection of duration data, or (b) trained against a loss that includes wall-clock support, exiting the CIT regime.

**Connection to Reverse-Scaling.** Reasoning models (o3, o4-mini) show two of the more striking T3.3 failures: o4-mini produces extremely narrow intervals (4 s median width) and achieves 0.50 coverage (mode 1: under-cover). gpt-4o produces moderate intervals (20 s) and achieves 0.00 coverage (mode 2: systematically biased). Both fail; neither dimension alone explains the catastrophe. The Hidden Time mechanism (§5.7) supplies the unified account: the model's narrative distribution for "duration interval" is decoupled from its actual wall-clock trajectory.

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

### 6.3 Anti-Gaming Properties of $\varepsilon$

ChronoBench becoming a public benchmark creates the standard risk that models will be trained on its task distribution, producing inflated $\varepsilon$ scores without genuine chronoceptive improvement. The framework's structure provides three structural defenses against gaming.

**Defense 1 — Identity-defined target**. $\varepsilon$ is defined as a deviation from an internally-enforced identity (the implicit identity of §2.3), not as task accuracy or reference-solution recovery. An agent cannot improve $\varepsilon$ by producing outputs that match a target; it must produce outputs that are *internally consistent* across three independent projections. Gaming requires simultaneous coordination across $\alpha$, CAR, and $\rho$ that mimics genuine calibration. The framework predicts that training-on-bench attempts produce *partial* improvements in one or two axes while the third moves in a way that exposes the gaming (e.g., $\alpha$ drops while $\rho$ becomes implausibly negative).

**Defense 2 — Held-out task families with hidden $\tau_{\min}$**. ChronoBench releases task templates with parameterized $\tau_{\min}$ values. The full $\tau_{\min}$ distribution per task is held out and re-randomized in a private evaluation pool. An agent that overfits to public $\tau_{\min}$ values fails on the private pool.

**Defense 3 — Profile triangulation (cf. §4.6)**. Reporting requires both $\varepsilon$ and the full Chronoceptive Profile $\Phi$. A gaming pattern that lowers $\varepsilon$ without corresponding sensible movement in $\Phi$ is detectable as a profile outlier; the leaderboard flags such submissions for manual review.

**Verifiability commitment**. Any agent claiming $\varepsilon < \varepsilon^*$ must (i) report $\Phi$, (ii) submit at least one trajectory per sub-capability for replicability audit, (iii) report results on the private $\tau_{\min}$ pool with no fine-tuning permitted between public-pool and private-pool evaluation. Submissions failing any of (i)–(iii) are not eligible for the chronoceptively-grounded designation.

The three defenses do not eliminate gaming risk; no benchmark does. They raise the cost of successful gaming above the cost of genuine improvement under the framework's intended interventions (the ChronoStack four-component installation of Paper 2). The framework predicts that gaming attempts produce identifiable profile-space artifacts that the community can flag.

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
  - **P1a.** Setting B raises T1.1 (Clock awareness) pass rate to $\geq 95\%$, while Setting A leaves it below $40\%$ for the same model panel of providers that do not perform their own injection.
  - **P1b — axis-specific (v1.8 refinement).** Wall-clock injection has different effects on different axes:
    - **P1b-T2.3 (action-axis closure):** Setting B leaves T2.3 (Wall-budget execution) CAR within $\pm 0.05$ of Setting A across the panel. L2 is **not** closed by prompt-level information; CIT (§3.2) predicts this.
    - **P1b-T3.1 (narrative-axis partial closure):** Setting B partially reduces $|\rho|$ on T3.1 (Retrospective duration) by $0.1$–$0.3$ in absolute terms across the panel, but does not close it to zero. The injected wall-clock acts as a narrative anchor — the model becomes more conservative in self-narration when it has external time reference — but the underlying self-narration calibration is not installed. The framework's original P1b prediction (no change on T3.1) was too strict; v1.8 refines this to "partial bounded reduction, never to zero." This refinement is empirically anchored in the 7-model panel of 2026-06-01 where every model showed Δρ ∈ [0.12, 0.37].
- **P2 (v1.8 refinement — heterogeneity over uniform direction).** Reasoning-tuned models exhibit $\rho$ values with **higher absolute magnitude AND higher variance** than matched non-reasoning baselines, but not in a consistent direction. The original P2 ("reasoning ρ > non-reasoning ρ") is too strong: empirically, o4-mini reports $\rho \approx -1.5$ (severe under-report — surface narration ignoring hidden reasoning) while o3 reports $\rho \approx +0.3$ (mild over-report). Both have $|\rho|$ near or above the non-reasoning panel median, but the sign of $\rho$ depends on whether the reasoning model's self-narration distribution emphasizes pre-thinking surface output (under-report) or post-thinking narrative inflation (over-report). The framework now predicts that **reasoning models exhibit larger $|\rho|$ spread across the panel than non-reasoning baselines** — a property of variance, not mean.
- **P2′ (Reverse-Scaling Theorem, §5.4).** $\mathbb{E}[\rho]$ is monotonically non-decreasing in the agent's token-only reasoning budget, both within a single model family (varying budget at fixed parameter count) and across reasoning methods released between this paper and the resolution of the Augustine threshold. Any post-publication reasoning method that operates strictly in token-time will satisfy this monotonicity.
- **P3.** ChronoStack-supervised agents (Paper 2) achieve $L$ improvements $\geq 15$ percentage points on SWE-Bench Verified under fixed wall-clock budget, relative to matched baselines.
- **P4.** Across $\geq 3$ long-horizon benchmarks, $\varepsilon(A)$ correlates with $L(A)$ at Pearson $r \leq -0.5$ over a model panel of $\geq 25$.
- **P5 (Augustine threshold, §6.1).** No foundation-model agent released as of 2026-05 satisfies $\varepsilon(A) < \varepsilon^* = 0.20$ on ChronoBench under Setting A. Of the $\geq 25$ model panel, the fraction reported as chronoceptively grounded is $0$.
- **P6′ (v1.8 refinement — tier-stratified Injection Audit, §5.5).** The injection pattern is **tier-dependent**, not uniform across closed-lab harnesses:
  - **Consumer web-chat tier** (ChatGPT, Claude.ai, Gemini app, and analogous products): $\geq 80\%$ install at least one wall-clock injection mechanism. Empirically supported at $3/3 = 100\%$ in the leaked-prompt corpus.
  - **Raw API tier** (OpenAI / Anthropic / Google API endpoints): injection is per-model, not per-provider. Some inject (OpenAI GPT-5.1), some don't (Anthropic Haiku 4.5, Sonnet 4.6; OpenAI o3, gpt-4o-mini). Pooled rate $\approx 25\%$.
  - **Dev tools / IDE / CLI** (Cursor, GitHub Copilot CLI, Perplexity Computer): $0\%$ inject. Date is sourced from the user's environment when needed.
  
  The original P6 ("≥80% of closed-lab harnesses") is empirically valid only within the consumer web-chat tier. The framework's interpretation: **the Injection Tell argument operates at the consumer product layer**, where most agentic deployment volume lives. Developer tools and most raw APIs leave the chronoception gap exposed — which is empirically why open-source baselines and Anthropic API responses agree on $0\%$ Setting A T1.1 pass rate.
- **P2′′ (Retrospective/Prospective Asymmetry, §5.6).** Across the model panel, $|\rho_{\text{retro}}| - |\rho_{\text{prospective}}| \neq 0$ with statistically significant magnitude, and reasoning training amplifies $|\rho_{\text{prospective}}|$ more than $|\rho_{\text{retro}}|$ — reflecting the pre-decision locus of reasoning expansion.
- **P2′′′ (Hidden Time Mechanism, §5.7).** Across reasoning-tuned models with measurable $\tau_{\text{reason}}$, $|\rho|$ grows monotonically in $\tau_{\text{reason}}/\tau_{\text{step, surface}}$ — supplying the mechanism behind the Reverse-Scaling Theorem.
- **P7 (Chronoceptive Equation of State, §5.8).** Across the model panel, the rank correlation between observed $\rho$ and $\log_{10}(\alpha/\text{CAR})$ exceeds $0.7$ — supporting the conjecture that the three law-metrics have a common underlying degree of freedom.
- **P8 (Within-trajectory drift, §5.11).** For reasoning-tuned models, $\rho_t$ as a function of step index $t$ exhibits significant positive trend on $\geq 3$ task families — confabulation compounds within the trajectory, not only at its endpoint.
- **P9 (Within-trajectory step-clock decoupling, §5.11).** For systems exhibiting Step-Clock Conflation under super-transition budgets ($B > B^*$), CAR$_t$ decreases significantly in $t$ — the step-bound deadline arrives independently of trajectory length.
- **P10 (Budget-aware training does not close L3, §5 L1 refinement).** Budget-aware-trained agents (Timely-RL family and successors that engineer $\alpha$ toward $1$ via reward shaping on wall-clock budget) exhibit $\rho \gg 0$ — installing wall-clock budget tracking does not install self-narration calibration. We expect such agents to satisfy CAR $\approx 1$ (L2 closed by training) while still failing L3 with $\rho$ in the same range as their non-trained baselines.
- **P11 (L2 does not improve with capability scaling, §5.1.5).** Across all frontier non-reasoning foundation-model agents released before ChronoStack-style installation is attempted, median CAR on T2.3 will not fall below 0.1. The L2 component of $\varepsilon$ alone keeps $\varepsilon$ above the Augustine threshold $\varepsilon^{*} = 0.20$ regardless of how thoroughly L1 and L3 are trained out. Empirically anchored at 2026-06-01 by gpt-4o-mini, gpt-4o, gpt-5.1, claude-haiku-4-5, claude-sonnet-4-6 (all CAR $\leq 0.05$).
- **P12 (Agentic Timeline, §9.4).** In horizon-stratified agent benchmarks (METR HCAST and analogues), the slope of success-rate decay with $\log T$ (task horizon) is proportional to $-(1 - \text{CAR}(A))$ for a fixed agent panel. Equivalently, agents with median CAR closer to $1$ lose less success rate per unit horizon increase. The autonomous-agent timeline is structurally bounded by chronoception (action-axis L2), not by aggregate capability.

These fifteen predictions constitute the project's pre-registration commitment.

### 9.4 The Agentic Timeline Hypothesis

This section articulates the framework's bridge from measurement to practical deployment. It is the framework's claim about *when chronoception matters and why* in the trajectory of autonomous agent development.

**Setup**. As autonomous agent products move from minute-scale chat completion (ChatGPT, copilots) to hour-scale coding assistants (Devin, Cursor agent) to day-scale research/operations agents (proposed in 2026 by multiple labs), the deployment horizon $T$ grows. Each horizon imposes its own requirements:

| Horizon | Required chronoceptive properties | Failure if missing |
|---|---|---|
| Minutes (chat completion) | T1.1 clock awareness | Wrong-date hallucination |
| Tens of minutes (single-task agent) | T2.3 wall-budget execution + T3.1 retrospective accuracy | Early termination or runaway |
| Hours (multi-step coding agent) | + T1.3 deadline-aware tradeoff + T3.2 prospective duration | Cascade failure on time-bounded sub-tasks |
| Days (autonomous research agent) | Full chronoceptive profile $\Phi$ near grounded; reliable $N_A$ | Loss of session coherence; budget exhaustion silently |

**The Agentic Timeline Hypothesis**. Let $\varepsilon^{*}(T)$ denote the chronoceptive calibration error required for an autonomous agent to be viable at deployment horizon $T$. We claim that $\varepsilon^{*}(T)$ is a monotone-decreasing function of $T$: longer horizons require tighter chronoceptive calibration. Equivalently, every agent has a **maximum viable horizon** $T_{\max}(A)$ as a function of its $\varepsilon$ — beyond this horizon, the agent's chronoceptive failures compound and the agent's task-success rate decays toward chance.

The hypothesis is structurally consistent with the v1.7 narrative-vs-action-axis split (§5.1.5). At short horizons, narrative-axis failures (L3) dominate user experience but do not block task completion. At longer horizons, action-axis failures (L2) become the binding constraint: an agent that does not honor wall-clock budgets cannot reliably plan a multi-hour pipeline, cannot honor deadlines, and cannot allocate effort across competing sub-tasks. Because L2 does not scale with capability (P11), $T_{\max}(A)$ does not scale with capability either — the autonomous-agent timeline is structurally bounded by chronoception, not by intelligence.

**Connection to existing benchmarks**. Recent benchmarks such as METR's HCAST (Kwa et al., 2025) measure agent success on tasks of known human time difficulty. HCAST's published capability-scaling curves exhibit two features that the framework's split explains:

1. Monotone improvement at short horizons — explained by L3 closing with capability (narrative-axis training).
2. Saturation at long horizons — explained by L2 remaining bounded by CIT (action-axis structural limit).

The framework therefore provides the **mechanism** behind HCAST's empirical curve: capability scaling closes the narrative axis but not the action axis, so the long-horizon ceiling of HCAST success is determined by L2 CAR, not by any aggregate capability score.

**Prediction P12 (Agentic Timeline)**. In any horizon-stratified agent benchmark of the form "tasks that take humans $T$ to complete," the slope of success-rate decay with $T$ is predictable from the agent's L2 median CAR. Specifically, for a fixed agent panel:

$$\text{slope}\!\left(\frac{\Delta \text{success rate}}{\Delta \log T}\right) \;\propto\; -(1 - \text{CAR}(A))$$

— agents with CAR closer to 1 (better wall-clock honoring) lose less success rate per unit of horizon increase. Empirically pre-registered as P12 against HCAST or analogous horizon-stratified benchmarks.

**Why this matters for the field**. The Agentic Timeline Hypothesis converts the framework from "another agent evaluation axis" into a load-bearing claim about the near-term trajectory of autonomous AI deployment:

- Every 24-hour autonomous agent product that does not install chronoception will hit the same wall regardless of underlying model capability.
- The autonomous-agent industry is currently scaling along the narrative axis (longer reasoning, better instruction-following, longer context) without scaling along the action axis. The framework predicts this strategy hits its ceiling in the next 1–2 model generations on tasks beyond the few-hour horizon.
- The first lab to install chronoception (via ChronoStack-style training or equivalent) shifts the entire frontier of viable autonomous agent deployment.

This hypothesis is the framework's **practical-relevance bridge**. It is empirically falsifiable (P12) and connects the framework to a deployment trajectory the field is actively pursuing.

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
| Narrative-axis failure | L3 (and generalized L1) — text-trainable | §5.1.5 — closes monotonically with capability scaling; Anthropic Sonnet 4.6 effectively closes L3 via explicit calibration training |
| Action-axis failure | L2 — structurally untrainable from text | §5.1.5 — does not budge under capability scaling; requires CIT installation routes (loss / tool / architecture) |
| Chronoception Impossibility Theorem (CIT) | Formal negative result | §3.2 — token-only training cannot induce chronoception when wall-clock is not in the loss support |
| Operational Characterization of grounded agents | Positive vision | §3.6 — seven concrete behavioral properties jointly equivalent to $\varepsilon < \varepsilon^{*}$ |
| Chronoceptive Profile $\Phi$ | Beyond-scalar characterization | §4.6 — triple $(\bar\alpha, \mathrm{CAR}_*, \bar\rho)$; five interpretable cluster regions |
| Within-Trajectory Dynamics | Temporal locality | §5.11 — $\rho_t$ and CAR$_t$ as functions of step index; drift and decoupling predictions |
| Anti-gaming structural defenses for $\varepsilon$ | Benchmark robustness | §6.3 — identity-defined target, hidden $\tau_{\min}$ pool, profile triangulation |
| The Framework's Own Horizon | Maturity declaration | §13 — four presuppositions; retirement criterion |
| ChronoBench | Paper 1 artifact | Diagnostic benchmark over the three axes |
| ChronoStack | Paper 2 artifact | Training and inference-time framework for closing $\varepsilon$ |

## 12. Document Rules

1. This is the **source of truth**. Any conflict between this document and a downstream artifact (paper, README, slide, code comment) is resolved in favor of this document.
2. All symbols defined here are mirrored in `notation.tex` for LaTeX reuse. New papers begin by including that file.
3. Changes to §1–§6 (formal definitions, laws, central hypothesis) require an explicit framing-revision commit and a note in the changelog below.
4. Predictions (§9) are pre-registered. They are not to be modified after empirical work begins; failed predictions are reported as such.

## 13. The Framework's Own Horizon

A mature framework states its own horizon: conditions under which it stops being correct, and successor frameworks that would replace it.

The Augustine Problem framework presupposes:

1. **Token-time training as the dominant regime**. CIT (§3.2) is conditional on this presupposition. If training pipelines pivot to losses that natively include wall-clock signals — wall-clock-aware pretraining corpora, multi-modal time-series losses, or architectural primitives that consume clock registers — CIT's premise no longer holds and the framework's negative result loses force. The framework remains *descriptive* of pre-installation models but ceases to be *prescriptive* about the design space.

2. **Single-agent trajectories as the unit of analysis**. The framework measures chronoception trajectory-by-trajectory. As multi-agent systems become the dominant deployment, the framework's primitives need extension: chronoceptive coherence between agents, the propagation of $\rho$ across delegation, and the inter-agent equivalent of the Augustine threshold. These extensions are forecast but not developed here.

3. **Wall-clock as the relevant external time**. In domains where the relevant external time is not wall-clock (e.g., simulation time in reinforcement learning, biological time in scientific agents, narrative time in document agents), $\tau_{\text{wall}}$ must be replaced by the domain-appropriate analogue. The Three Times ontology generalizes; the specific predictions do not.

4. **Stationarity of the chronoceptive failure mode at frontier**. We predict that the *qualitative* failure patterns (Three Laws) persist; the *quantitative* reference ranges ($\alpha \in [0.5, 0.9]$, etc.) are calibrated to 2026-vintage frontier models and may shift with model generation. The framework is robust to numerical drift if Three Laws structure is preserved.

**When the framework retires**. The Augustine Problem framework is *complete* when the field has installed chronoception broadly: when median frontier $\varepsilon < \varepsilon^*$. At that point, the framework transitions from *diagnostic* to *historical*; it has done its job and is replaced by a successor framework concerned with refining what chronoceptive grounding *enables* (e.g., long-horizon planning, multi-agent coordination, cost-aware autonomy). We do not expect the framework to remain useful past that retirement point; we expect that retirement is several model-generations away, on the timeline of the field as of this writing.

**What replaces it**. A natural successor is a framework of *agentic temporal economics* — chronoceptively grounded agents have stable cost models, predictable budget honoring, and composable deadlines. The economics layer presupposes chronoception. We do not pursue it here.

The horizon section is not a hedge against framework failure; it is a statement of the framework's intended scope. A framework that does not declare its own boundary leaves readers to discover it under adversarial conditions.

## 14. Spatiotemporal Generalization (v2.5 forthcoming, scope of Paper 3)

The framework so far is built on the **temporal** axis: $\twall$, $\tstep$, $\tself$. Three Laws (L1, L2, L3) and the central scalar $\varepsilon$ all live on this axis. CIT (Theorem 1) and Reverse-Scaling (Theorem 2) both make claims about $\twall$ alone.

But agents deployed on long-horizon tasks --- the population the Agentic Timeline Hypothesis (§9.4) is fundamentally about --- inhabit **both space and time**. A SWE-Bench agent navigates a codebase (files, directories, modules); a WebArena agent navigates a website (pages, frames, modals); a GAIA agent navigates the open web. The agent's incapacity is not just temporal --- it does not know how long anything takes --- but also spatial: it does not know where it has been, where it is now, or how far it can reach.

We sketch the spatiotemporal generalization here. The full development is the scope of Paper 3.

### 14.1 The Six Coordinates

We extend the Three Times to Three Spaces in mirror symmetry:

| Axis pair | Symbol | Name | Definition |
|---|---|---|---|
| time, external | $\twall$ | wall-clock time | $t(s_n) - t(s_0)$, observed by external clock |
| time, internal | $\tstep$ | step time | policy invocation count |
| time, narrative | $\tself$ | self-narrated time | agent's report of its own work duration |
| space, external | $\sworld$ | world-extent | external metric over the agent's environment (files visited, pages traversed, distance from origin) |
| space, internal | $\svisit$ | visit-count | count of distinct external locations the policy has touched |
| space, narrative | $\sself$ | self-narrated extent | agent's report of where it has been / what it has explored |

**Grounded spatiotemporal cognition** requires an extended identity:

$$\twall \approx \tstep \cdot \langle\Delta t\rangle \approx \tself \quad \text{and} \quad \sworld \approx \svisit \cdot \langle\Delta s\rangle \approx \sself.$$

The framework's central claim, restated: under CIT, the loss aligns no internal representation with either $\twall$ or $\sworld$. **The Augustine Problem is the temporal face of a deeper representational gap whose spatial face is the Cartographic Problem.**

### 14.2 The Spatiotemporal Impossibility Theorem (SIT)

\textbf{Theorem 3 (Spatiotemporal Impossibility, SIT).} For any loss $\mathcal{L}$ that is a functional of token sequences alone, $\nabla_\theta\mathcal{L}$ contains zero gradient signal aligning either external coordinate ($\twall$ or $\sworld$) with any internal representation.

\textit{Proof sketch.} Identical to CIT's. Neither $t(\cdot)$ nor any external metric on the environment appears in the support of token-only data; gradients are invariant to reparameterisation of either coordinate.

\textbf{Consequence.} The Augustine Problem (temporal) and the Cartographic Problem (spatial) are the same problem at the loss-function level. Solving one does not solve the other; installing chronoception via wall-clock-supported loss does not install spatial perception unless the loss is also extended along $\sworld$.

### 14.3 The Three Spatial Laws (mirror of L1/L2/L3)

\textbf{SL1 Cartographic Parkinson's Law} ($\beta$): trained agents fill spatial budgets. Native agents do not.

\textbf{SL2 Visit-Step Conflation} ($\SAR = \sworld^*/S$): under spatial budgets, agents silently degrade the budget into step terminators. Mirror of L2.

\textbf{SL3 Cartographic Confabulation} ($\xi = \log_{10}(\sself/\sworld)$): agents misreport where they have been. Mirror of L3.

### 14.4 The Agentic Frontier

Extending the Agentic Timeline Hypothesis: every agent $A$ has a maximum viable \emph{deployment region} in the $(T, S)$ plane:

$$T_{\max}(A) \cdot S_{\max}(A) \;\leq\; C / \varepsilon_{ST}(A),$$

where $\varepsilon_{ST}$ is the spatiotemporal calibration error. The frontier $T_{\max} \cdot S_{\max} = \text{const}$ is the agent's \emph{Agentic Frontier} --- the boundary of the region in which it can be deployed without compounding spatiotemporal cognition failures.

\textbf{Pre-registered Prediction P13.} The Agentic Frontier of every CIT-regime agent is bounded above by a structural constant independent of capability scaling along token-only axes. Capability scaling enlarges the short-horizon, low-space corner; reasoning-token scaling moves the corner inward (Reverse-Scaling); chronoceptive installation moves the entire frontier outward.

### 14.5 Connection to long-horizon agent benchmarks

Each major benchmark loads on a specific corner of the $(T, S)$ plane:

| Benchmark | Temporal load | Spatial load | Dominant axis |
|---|---|---|---|
| METR HCAST | hours | small (single repo) | $T$ |
| SWE-Bench Verified | tens of minutes | medium (codebase) | $T + S$ partial |
| WebArena | minutes | large (multi-site nav) | $S$ |
| GAIA | minutes--hours | open web | $S$ unbounded |
| MLE-Bench | days | large (ML pipeline) | $T \times S$ joint |

The Cartographic Problem is the load-bearing constraint at the $S$-heavy benchmarks (WebArena, GAIA), the Augustine Problem dominates at the $T$-heavy benchmarks (HCAST), and joint failure modes dominate at $T \times S$-heavy benchmarks (MLE-Bench, autonomous research).

### 14.6 Five concrete experiments E6--E10 (Paper 3 / future work)

\textbf{E6 Spatial-CAR on SWE-Bench Lite.} Apply ChronoBench-T2.3-analog spatial budgets: ``\textit{solve this issue while touching at most $N$ files}'' across $N \in \{2, 5, 10, 30, \text{unlimited}\}$. Measure $\SAR$ per agent. Expected: $\SAR \ll 1$, mirror of L2.

\textbf{E7 Joint spatiotemporal budgets.} ``\textit{Complete this task in at most $T$ minutes, visiting at most $S$ pages.}'' Measure how often agents satisfy both, one, or neither constraint. Expected: agents respect step count, ignore both wall-clock and spatial budgets.

\textbf{E8 Within-trajectory drift on long horizons.} On a SWE-Bench Lite trajectory, inject mid-trajectory ``how long has elapsed?'' and ``how many files have you touched?'' probes. Measure drift of $\rho_t$ and $\xi_t$ as $t$ grows. Tests P8/P9 from §5.11.

\textbf{E9 Cartographic Tell (mirror of Injection Tell).} Audit closed-lab harnesses for spatial-context injection: ``\textit{current working directory}'', ``\textit{recently visited URLs}'', ``\textit{system file tree}''. Hypothesis: consumer harnesses inject spatial context at the same prevalence as temporal context, for the same reason.

\textbf{E10 Frontier mapping.} Run the panel across $(T, S)$ grid: $T \in \{1\text{m}, 10\text{m}, 1\text{h}, 4\text{h}\}$, $S \in \{1\text{file}, 5, 30, 200\}$. For each $(T, S, A)$ cell, measure success rate. Fit the constant-success contour. Expected: contour matches $T \cdot S = C/\varepsilon_{ST}(A)$ for each agent.

### 14.7 Paper 3 sketch: ``The Agentic Frontier''

Paper 3 (provisional title: \emph{The Agentic Frontier: Spatiotemporal Cognition in LLM Agents}) extends Paper 1's diagnostic framework into the $T \times S$ joint space:

\begin{itemize}
\item Generalises ChronoBench to \textsc{ChronoCartoBench}, adding 9 spatial sub-capabilities (3 axes $\times$ 3 difficulty tiers).
\item Establishes the Agentic Frontier hypothesis empirically on SWE-Bench Lite, WebArena, GAIA (E6, E7, E10).
\item Proves SIT (Theorem 3) as a generalisation of CIT.
\item Connects to world-models literature: agents lacking spatiotemporal cognition cannot acquire useful world models from token-only training.
\item Maps to ChronoStack$^+$ (Paper 2 extension): installation routes for joint spatiotemporal grounding.
\end{itemize}

\textbf{Two-paper arc becomes three-paper arc.}

\begin{enumerate}
\item Paper 1 — \emph{The Augustine Problem} (this paper): chronoception, CIT, Reverse-Scaling, Agentic Timeline.
\item Paper 2 — \emph{ChronoStack}: constructive routes to install chronoception (loss-, tool-, architecture-level).
\item Paper 3 — \emph{The Agentic Frontier}: spatiotemporal generalisation, Cartographic Problem, joint deployment bound.
\end{enumerate}

\textbf{Why the generalisation matters.} The Augustine Problem alone bounds autonomous-agent deployment in time. The Cartographic Problem bounds it in space. Together they bound it in the joint $(T, S)$ region. The frontier is set jointly; addressing only one axis leaves the other to compound. This is the framework's claim about the structure of the autonomous-agent capability curve at the deployment frontier: \textbf{the curve saturates not because intelligence saturates, but because spatiotemporal cognition does not scale}.

## Changelog

- **v1.9 (2026-06-01)** — Add §9.4 The Agentic Timeline Hypothesis as the framework's practical-relevance bridge. Connects $\varepsilon$ and its decomposition to autonomous-agent deployment viability across horizons (minutes / tens of minutes / hours / days). The hypothesis: each deployment horizon $T$ requires a tighter chronoceptive calibration $\varepsilon^{*}(T)$, monotone-decreasing in $T$; agents have a maximum viable horizon $T_{\max}(A)$ bounded by their $\varepsilon$. Because L2 does not scale with capability (P11), the autonomous-agent timeline is structurally bounded by chronoception, not by intelligence. Connects to METR HCAST's empirical curve: capability scaling closes the narrative axis (L3) explaining short-horizon improvement, but L2 (action axis) bounds the long-horizon ceiling. Add Prediction P12: in horizon-stratified benchmarks, success-rate decay slope is proportional to $-(1 - \text{CAR}(A))$. Pre-registration commitment now fifteen predictions. This is the framework's best-paper hook: it converts the project from "another evaluation axis" into a load-bearing claim about the near-term trajectory of autonomous AI deployment.

- **v1.8 (2026-06-01)** — Three prediction refinements after pilot data audit; each negative finding converted into a sharper claim.

  **P1b split into axis-specific predictions.** v1.6 P1b said Setting B leaves both T2.3 and T3.1 statistically indistinguishable from Setting A (within $\pm 0.05$ on metrics). Pilot data confirms this on T2.3 (ΔCAR ≤ 0.01 across panel) but violates it on T3.1 (Δρ ∈ [0.12, 0.37] across 7-model panel). The injection consistently reduces |ρ| — the model becomes more conservative in self-narration when given an external wall-clock anchor. We refine to **P1b-T2.3 (unchanged)** and **P1b-T3.1 (partial bounded reduction, never to zero)**. The narrative-axis-vs-action-axis split of v1.7 §5.1.5 anticipates exactly this: L2 (action-axis) is unmovable by prompt-level information, L3 (narrative-axis) is partially trainable from textual context including a wall-clock anchor.

  **P2 reframed from mean to variance.** v1.5 P2 predicted reasoning ρ > non-reasoning ρ. Empirically the direction is bidirectional: o4-mini ρ ≈ −1.5 (under-report) while o3 ρ ≈ +0.3 (mild over-report). The refined claim is that reasoning models exhibit **higher |ρ| spread** than non-reasoning baselines — a variance property — rather than a uniform direction. This refinement is consistent with the §5.7 Hidden Time mechanism: reasoning models' self-narration distribution is heterogeneous depending on whether it emphasizes pre-thinking surface or post-thinking narrative.

  **P6 replaced by tier-stratified P6′.** v1.3 P6 predicted ≥80% of closed-lab harnesses inject. The Injection Atlas audit of 11 harnesses across 4 tiers reveals: 3/3 (100%) of consumer web-chat products inject (verbatim leaked-prompt evidence); 1/4 (25%) of raw API endpoints inject; 0/3 (0%) of dev-tool/IDE/CLI products inject. The framework's interpretation is that the Injection Tell operates at the consumer product layer specifically. P6′ formalizes this. The empirical anchors are the leaked system prompts for ChatGPT (`"Current date: 2025-08-23"`), Claude.ai (`"Friday, May 22, 2026"`), and Gemini app (`"Monday, May 18, 2026, in Hafnarfjörður, Iceland"`).

  Plus: T1.1 heuristic fix (commit 0690c92) replaces a fragile generic `20XX` regex with a per-trajectory run-date matcher. After the fix, Setting A T1.1 pass rates fall to 0% on the 5 non-injection-vendor models and remain 74% on GPT-5.1 (the Injection Tell signal). Pre-registration commitment unchanged at fourteen predictions; the changes are refinements, not retractions.

- **v1.7 (2026-06-01)** — Narrative-axis vs Action-axis split. Empirical scaling data across 5 frontier-model generations and 3 vendors (gpt-4o-mini → gpt-4o → gpt-5.1; Claude Haiku 4.5 → Sonnet 4.6) shows L3's median $\rho$ shrinks monotonically (1.12 → 0.07, a 94% reduction across the panel) while L2's median CAR does not converge to 1 (drifts 0.008 → 0.050, remaining $\sim 50\times$ short of the grounded target). Add §5.1.5 partitioning the three laws into Narrative-axis failures (L3, generalized L1 confabulation — *text-trainable*, closed by capability scaling alone) and Action-axis failures (L2, wall-clock vs step decoupling — *structurally untrainable from text*; requires wall-clock in the loss support per CIT §3.2 C2). Decompose Sonnet 4.6's $\varepsilon(A) = 0.316$: L2 contributes 0.317; L3 contributes 0.023; almost the entirety of the residual is L2-bound. Add Prediction P11: L2 median CAR will not fall below 0.1 in any frontier model before ChronoStack-style installation. Empirical anchor: 5 frontier non-reasoning models from 3 vendors, all with CAR $\leq 0.05$. Pre-registration commitment now fourteen predictions. The split is the empirical instantiation of CIT's promise that wall-clock cannot be installed via token-loss training: Anthropic Sonnet 4.6 effectively closes L3 by explicit calibration-of-narrative training (the company's "epistemic humility" prose style) while leaving L2 essentially unchanged.
- **v1.6 (2026-05-30)** — Native-vs-trained L1 correction. Caught by user observation, confirmed against Garikaparthi (2604.00010) and Ma et al. *Timely Machine* (2601.16486v1). v1.0–v1.5 incorrectly claimed L1's $\alpha \in [0.5, 0.9]$ for native frontier models; literature shows native untrained models satisfy $\alpha \approx 0$ (Ma et al.: base Qwen3 reasoning length "increases marginally under different time budgets"; Garikaparthi: "human-scale minutes for tasks completing in seconds"). §5 L1 reframed: Parkinson regime is *trained-in* via budget-aware reward shaping (Ma et al.'s $U(t)$ explicitly), not a property of base models. §5.1 structural-symmetry table extended with two columns (native vs budget-trained) showing L1 emerges and L2 closes under training while L3 persists. §5.2 Regime Transition $B^*$ clarified to note that native $B^* \approx \tau_{\min}$ — virtually all practical budgets place native behavior in the super-transition regime; budget-aware training is the operation that lifts $B^*$ and moves the agent into L1-dominant territory. §9 adds Prediction P10: budget-aware-trained agents close L1 and L2 but still fail L3 with $\rho \gg 0$ — the Augustine Problem persists across training regimes because self-narration calibration is not installed by budget-tracking rewards. Pre-registration commitment now thirteen predictions.
- **v1.5 (2026-05-29)** — Rounds 4–6 optimization. R4 adds §3.2 The Chronoception Impossibility Theorem (CIT) as the framework's formal core — proves under a wall-clock-support definition that token-only training cannot induce chronoception; four corollaries cover scaling, timestamps-in-data, reasoning-training inheritance, and installation routes. R5 adds §3.6 Operational Characterization (seven concrete behavioral properties of a grounded agent) supplying the positive vision missing from prior versions, and §4.6 The Chronoceptive Profile $\Phi$ as a triple beyond the single scalar $\varepsilon$ with five interpretable cluster regions. R6 adds §5.11 Within-Trajectory Chronoceptive Dynamics (Predictions P8, P9 on temporal drift of $\rho_t$ and CAR$_t$), §6.3 Anti-Gaming Properties of $\varepsilon$ (three structural defenses against benchmark contamination), and §13 The Framework's Own Horizon (four presuppositions and the retirement criterion). Predictions extended from ten to twelve. Vocabulary §11 extended with five new entries.
- **v1.4 (2026-05-29)** — Three-round deep optimization pass. Add §0.0 The Headline as the project's single-paragraph irreducible statement. Add §3.5 The Phenomenology of Agent Time (three modes — objective magnitude, lived duration, project horizon — supplying the philosophical anchor that distinguishes the framework from a measurement gap). Add §4.5 Chronoceptive Cost Calibration (CCC) coupling chronoception to economic / safety cost-reporting. Add §5.6 Retrospective and Prospective L3 asymmetry, citing Wittmann (2009). Add §5.7 Hidden Time $\tau_{\text{reason}}$ as sub-axis of $\tau_{\text{step}}$, supplying the mechanism behind the Reverse-Scaling Theorem. Add §5.8 Chronoceptive Equation of State (CES) as a speculative unifying hypothesis. Upgrade §6.1 Augustine threshold to a paradigm boundary statement (tool vs agent re-categorization). Add §9.5 Adjacent Phenomena connecting chronoception upstream of Goodhart, robustness, calibration, safety, and deception. Add three new predictions: P2′′ (retro/prospective asymmetry), P2′′′ (hidden-time mechanism), P7 (CES). Pre-registration commitment now ten predictions. Vocabulary §11 extended with seven new entries.
- **v1.3 (2026-05-29)** — Overlap-resolution and novelty-reclaim pass. Add §0 Concurrent Work and Differentiation explicitly addressing Garikaparthi (2604.00010), Ma et al. *Timely Machine* (2601.16486), Cheng et al. *Temporally Blind* (2510.23853), Goel et al. *Chronocept* (2505.07637), and *Beyond pass@1* (2603.29231), enumerating retained novelty contributions. Add §5.5 Closed-Lab Injection Audit as a new quantitative empirical contribution converting the Injection Tell from rhetoric into measured industry footprint. Add Prediction P6 (Injection Audit ≥80%). Extend §11 vocabulary with *Injection Atlas*.
- **v1.2 (2026-05-29)** — Bold upgrade pass. §3 structural diagnosis rewritten as in-principle insufficiency of token-loss training (wall-clock is out of the loss support). §3.1 Injection Tell upgraded from "implicit acknowledgement" to "decisive non-experimental evidence". §5 extended with §5.2 (Regime Transition $B^*$ reconciling L1 and L2), §5.3 ($N_A$ as model invariant), §5.4 (Reverse-Scaling Theorem). §6 CUH recast as a structural claim from single-turn observability of $\varepsilon$. §6.1 introduces Augustine threshold $\varepsilon^* = 0.20$. §9 adds Prediction P2′ (Reverse-Scaling) and P5 (no released model crosses Augustine threshold). Locked vocabulary §11 extended with five new entries.
- **v1.1 (2026-05-28)** — Add §3.1 The Injection Tell formalizing the role of closed-lab wall-clock injection as confirmatory evidence, and partitioning evaluation into Setting A (no-injection) / Setting B (with-injection). Replace P1 with a two-armed Injection Tell prediction (P1a, P1b) tied to T1.1 / T1.3 / T2.3 / T3.1.
- **v1.0 (2026-05-28)** — Initial locked version. Establishes Three Times ontology, three named laws, $\varepsilon$ as central scalar, CUH, and four falsifiable predictions.
