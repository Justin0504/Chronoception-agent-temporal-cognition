# Related Work and Concurrent Work

**Status**: v0 (2026-05-29)
**Companion to**: [`FRAMING.md`](FRAMING.md) §0 (Concurrent Work and Differentiation)

This document is the long-form reference of related and concurrent work for the Chronoception / Augustine Problem project. It supplies Paper 1's §10 Related Work and Paper 0 (position note)'s §9 Related Work with their working citation set and differentiation rationale.

The project's novelty audit (last refreshed 2026-05-29) flagged three concurrent papers, one name collision, and one closely-related empirical neighbor. Each is treated below at the level of detail required to enter the paper's prose.

---

## 1. Direct Concurrent Threats

### 1.1 Garikaparthi (2026) — *Can LLMs Perceive Time? An Empirical Investigation*

**Citation**: Garikaparthi, A. (2026). *Can LLMs Perceive Time? An Empirical Investigation*. arXiv:2604.00010.

**What it does**: Measures pre-task, mid-task, and post-hoc duration self-reports on 68 tasks across four non-reasoning model families (GPT-5, GPT-4o, OLMo3-7B, Qwen3-8B). Reports pre-task overshoot of 4–7× ($p < 0.001$), post-hoc disconnection from reality (errors of order-of-magnitude in either direction), and persistence of these failures in multi-step agentic settings (5–10×).

**Axis overlap with our framework**: $\tau_{\text{self}}$ only — corresponds to our L3 (Temporal Confabulation).

**Where it stops short**:

- No reasoning-tuned models tested (no o-series, R1, Claude extended thinking, Gemini reasoning).
- No name for the phenomenon (*Temporal Confabulation* is uncoined).
- No metric $\rho$ defined; reports raw multiples instead of $\log_{10}$ ratios.
- No unification with budget-following or step-clock behavior.
- No scalar aggregation across axes.
- No formal connection to harness-side injection.

**Our differentiation**:

1. We extend to reasoning-tuned models and pre-register that $\rho_{\text{reasoning}} > \rho_{\text{base}}$ at matched parameter count (Prediction P2). The Reverse-Scaling Theorem (FRAMING §5.4) makes this a structural prediction.
2. We unify $\tau_{\text{self}}$ with $\tau_{\text{wall}}$ and $\tau_{\text{step}}$ via the Three Times ontology.
3. We define $\rho$ and aggregate it with $\alpha$ and CAR into $\varepsilon$.
4. We supply the Injection Tell argument and Injection Atlas (FRAMING §3.1, §5.5) as the structural diagnosis behind the empirical finding.

**Recommended prose**:

> "Garikaparthi (2026) provides the first systematic measurement of duration self-reporting on non-reasoning frontier models and reports pre-task overshoot of 4–7× and post-hoc disconnection from reality. Our $\tau_{\text{self}}$ axis subsumes this measurement; our extension to reasoning-tuned models reveals that $\rho$ is non-decreasing in the reasoning budget, contrary to capability-scaling intuition."

### 1.2 Ma et al. (2026) — *Timely Machine*

**Citation**: Ma, Y., Li, L., Chen, Y., Li, P., Li, X., Guo, Q., Lin, D., Chen, K. (2026). *Timely Machine: Awareness of Time Makes Test-Time Scaling Agentic*. arXiv:2601.16486v1.

**What it actually does** (read in detail, 2026-05-29):

- **Decomposes wall-clock** as $t_{\text{all}} = \sum_i t_{\text{gen}}(i) + \sum_i t_{\text{tool}}(i)$ — a two-component refinement of $\tau_{\text{wall}}$, separating model-side token generation from external tool latency. *This is a sub-structure of our $\tau_{\text{wall}}$ axis, not a competing ontology.*
- **Defines three regimes** by latency ratio $m_i = t_{\text{tool}}(i)/t_{\text{gen}}(i)$: tools-dominate, models-dominate, middle ground.
- **Trains Timely-RL** via SFT cold-start (1M distilled trajectories from Qwen3-235B) plus GRPO-variant RL with a three-component reward $r_f + r + \lambda U(t)$, where the **time-utilization bonus is** $U(t) = \sin\!\left(\tfrac{\pi}{2}\cdot\min\!\big(\tfrac{t}{T_{\max}},1\big)\right)$, **maximized at $t = T_{\max}$**.
- **Instruments tasks with a `get_duration()` tool** that returns elapsed time (with a coefficient and noise). Models query elapsed time by tool call.
- **Benchmark Timely-Eval** spans Jericho text games (4 used in evaluation), 4 ML competitions (Leaf Classification, Spaceship Titanic, RAOP, Detecting Insults), and 3 reasoning benchmarks (AIME, MATH, GPQA-diamond). Tested on Qwen3 series 0.6B–32B plus GPT-5.1, DeepSeek-V3.2, Gemini2.5-pro as baselines.
- **Headline empirical findings**: (i) smaller models outperform larger ones under low tool latency (Fig. 2); (ii) TimelyLM exhibits *"significant increasing trend in reasoning length as the time budget increases"* (Fig. 3); (iii) reasoning models (DeepSeek-V3.2) *"cannot control the generation length and thus frequently fail to complete the task within the time budget at 0.75× or even larger time constraints"*.

**Three aspects of their work *support* our framework rather than challenge it**:

#### Support 1 — The Timely-RL reward function is trained-in Parkinson

The bonus $U(t) = \sin(\pi t / 2 T_{\max})$ is monotonically increasing on $[0, T_{\max}]$ and reaches its maximum precisely at $t = T_{\max}$. **An RL agent maximizing this reward is explicitly incentivized to use the entire wall-clock budget**, regardless of whether the additional time improves task accuracy. This is Agentic Parkinson's Law (our L1) *prescribed as a training objective*. We diagnose the same behavior in untrained agents as a representational failure; their prescription and our diagnosis are complementary views of the same underlying behavioral pattern.

**Recommended prose for Paper 1**:

> "Ma et al. (2026) propose a reward function $U(t) = \sin(\pi t/2T_{\max})$ maximized at $t = T_{\max}$, methodologically prescribing budget-filling behavior. We diagnose the same behavior, when observed in untrained agents, as Agentic Parkinson's Law (L1). The two views are complementary: their training objective and our diagnostic measurement converge on the same phenomenon."

#### Support 2 — Their `get_duration()` tool is the Injection Tell at its most explicit

Even after specialized training on $\sim 1$M chronoception-relevant trajectories plus GRPO RL, the Timely-RL agent **still requires an external `get_duration()` tool to perceive elapsed time**. The model does not acquire an internal wall-clock representation from training; it acquires the policy of *querying a tool that has the wall-clock*. This is the Injection Tell at maximum strength: a research team that controlled both training data and training objective could not avoid installing a clock-yielding function.

**Recommended prose for Paper 1**:

> "Even after specialized RL training designed expressly to instill wall-clock awareness, Ma et al.'s agents require an explicit `get_duration()` tool to perceive elapsed time. This is the Injection Tell at maximum strength: research teams that control both training data and training objective cannot avoid installing a clock-yielding function. The engineering necessity validates the structural diagnosis."

#### Support 3 — Their DeepSeek-V3.2 finding is a Reverse-Scaling Theorem anchor

The verbatim observation that reasoning models *"cannot control the generation length and thus frequently fail to complete the task within the time budget at 0.75× or even larger time constraints"* is a direct empirical instance of our Reverse-Scaling Theorem (FRAMING §5.4). Ma et al. report it as a limitation of current reasoning models to be patched by Timely-RL; we report it as the **structural consequence** of expanding test-time compute strictly in token-time, predicted by the framework before measurement.

**Recommended prose for Paper 1**:

> "Ma et al. (2026) report that DeepSeek-V3.2 fails to honor wall-clock budgets because *'it cannot control the generation length'*. Our Reverse-Scaling Theorem (§5.4) predicts this structurally: any reasoning method that operates strictly in token-time inflates $\tau_{\text{wall}}$ without corresponding adjustment in $\tau_{\text{self}}$, producing exactly the failure pattern reported. The empirical observation is concurrent corroboration of our pre-registered prediction."

**Where they do not overlap with us at all**:

- $\tau_{\text{self}}$ axis: agents in Ma et al. report elapsed time via the `get_duration()` tool. The agent's *internal* sense of duration is never measured; the agent only ever reports what the tool tells it. L3 (Temporal Confabulation) is untouched.
- Three Times ontology: Ma et al. have $t_{\text{gen}}$ and $t_{\text{tool}}$, both inside $\tau_{\text{wall}}$. They do not introduce $\tau_{\text{step}}$ as a separate axis, do not introduce $\tau_{\text{self}}$, and do not formalize an implicit identity linking three axes.
- Step-Clock Conflation (L2): not addressed. Their step-budget conditions (e.g., 30/50/100/200 steps for games) and their wall-budget conditions are run side by side without testing whether wall-budget execution silently degrades into step-count termination.
- Retrospective vs prospective L3 asymmetry: not addressed.
- Augustine threshold / paradigm boundary / tool-vs-agent distinction: not addressed.
- Single scalar (analogue of $\varepsilon$): they propose time-utilization rate $U(t)$ as a reward signal, and on-time completion rate as a task metric, neither of which aggregates a multi-axis calibration error.
- Injection Atlas: not addressed (we audit the industry; they instrument their own benchmark).
- CCC (cost coupling): not addressed.
- CES (unifying equation): not addressed.

**Combined positioning for Paper 1**:

> "Ma et al. (2026, *Timely Machine*) and the present work both observe that LLM agents do not natively perceive wall-clock time. The two papers respond to this observation in different ways. *Timely Machine* prescribes a training objective that rewards budget-filling and a tool that returns elapsed time; the resulting agent exhibits adaptive reasoning length but still requires the tool to perceive time. We instead measure the underlying gap, name it (the Augustine Problem), decompose it across three ontologically distinct projections of time (the Three Times), aggregate the failure modes into a single calibration scalar $\varepsilon$, and audit the closed-lab industry's analogous tool-injection patterns (the Injection Atlas). Their work supplies three pieces of independent empirical evidence that our framework is well-posed: (i) the necessity of the `get_duration()` tool even after training, (ii) the Parkinson-like behavior that emerges under their reward, and (iii) the failure of token-only reasoning models to honor wall-clock budgets, predicted by our Reverse-Scaling Theorem."

**Net assessment**: After detailed reading, *Timely Machine* is **not a threat to novelty on any contribution of our framework**. It is the closest concurrent work on $\tau_{\text{wall}}$-vs-generation-length decoupling, but its method, benchmark, ontology, and measurement protocol are non-overlapping with ChronoBench. Three of its findings (the reward design, the tool necessity, the DeepSeek-V3.2 failure) become independent corroboration of our framing rather than competing claims.

### 1.3 Cheng et al. (2025) — *Your LLM Agents are Temporally Blind*

**Citation**: Cheng, Y., Moakhar, A. S., Fan, C., Hosseini, P., Faghih, K., Sodagar, Z., Wang, W., Feizi, S. (2025). *Your LLM Agents are Temporally Blind: The Misalignment Between Tool Use Decisions and Human Time Perception*. arXiv:2510.23853.

**What it does**: Coins *temporal blindness* in the context of agent tool-use timing decisions. Ships TicToc-v1, a benchmark of 34 scenarios in which agents must decide whether to re-check the current state given that time has passed. Notes informally that lab harnesses inject timestamps via tool outputs, foreshadowing the Injection Tell argument.

**Axis overlap**: Mentions $\tau_{\text{wall}}$ vs $\tau_{\text{step}}$ casually; identifies the harness-injection phenomenon at the level of observation.

**Where it stops short**:

- The wall-clock-vs-step distinction is informal; no Clock-Adherence Ratio.
- The harness-injection observation is a setup detail rather than an evidential argument.
- No quantitative survey of injection practices across labs.
- No three-axis ontology, no naming of laws, no scalar $\varepsilon$, no Parkinson coefficient, no causal upstream claim.
- Reasoning-model focus absent.

**Our differentiation**:

1. We elevate harness injection from background observation to **the Injection Tell**, a formal evidential argument for the Augustine Problem.
2. We supply the **Closed-Lab Injection Audit** (FRAMING §5.5) — a systematic empirical survey of $\geq 10$ closed-lab harnesses with the three-mechanism taxonomy of FRAMING §3.1.
3. We generalize from tool-use-decision misalignment to the three-axis ontology.

**Recommended prose**:

> "Cheng et al. (2025, *Temporally Blind*) document misalignment between agent tool-use decisions and human time perception, noting in passing that lab harnesses inject timestamps. We formalize this observation as the Injection Tell — an evidential argument that converging closed-lab engineering choices constitute implicit industry acknowledgement of the representational gap — and substantiate it with a Closed-Lab Injection Audit across $\geq 10$ harnesses."

---

## 2. Name Collision

### 2.1 Goel et al. (2025) — *Chronocept*

**Citation**: Goel, K., Pandey, S., Mahadevan, K. S., Kumar, H., Khadaria, V. (2025). *Chronocept: Instilling a Sense of Time in Machines*. arXiv:2505.07637.

**What it does**: Applies the cognitive-science term *chronoception* to the **temporal validity of facts in retrieval-augmented generation**. Builds a benchmark of facts whose validity is time-dependent.

**Why it is a collision**: Both papers use *chronoception* as a central term in an LLM context. The applications are orthogonal — Goel et al. care about facts ageing in the world, we care about an agent's perception of its own work duration — but the term coexistence requires explicit disambiguation.

**Mitigation**:

- The project repository name `chronoception` predates Goel et al.'s borrowing in our timeline of work (FRAMING.md v1.0 was 2026-05-28), but their arXiv publication date (2025-05) is earlier. We do not contest the term; we disambiguate.
- Our Paper 1 title leads with *The Augustine Problem*, not *Chronoception*.
- The first mention of *chronoception* in every downstream artifact carries a disambiguation:
  > "We use *chronoception* in its original cognitive-science sense — the perception of one's own work duration — distinct from Goel et al.'s (2025) use of the term for the temporal validity of facts in retrieval-augmented generation."
- We adopt *agentic chronoception* as our paper's preferred long-form when ambiguity is possible.

**Recommended prose** (in the paper's introduction or footnote 1):

> "We adopt *chronoception* from cognitive psychology (Wittmann, 2009; Eagleman, 2008), where it denotes the subject's perception of duration. Goel et al. (2025) recently used the term in LLM research to refer to the temporal validity of facts in retrieval-augmented generation; we use it in its original perception-of-own-duration sense throughout."

---

## 3. Adjacent Empirical Neighbors

### 3.1 *Beyond pass@1* (2026)

**Citation**: Anonymous (2026). *Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents*. arXiv:2603.29231.

**Relationship**: The closest precedent to our Three Times ontology — uses human-estimated duration, agent steps, and tokens as **three parallel measurement axes**. Observes divergence between human time and agent steps.

**Differentiation**: Their axes are *measurement* dimensions; ours are *ontological projections* of a single trajectory linked by an implicit identity. They lack $\tau_{\text{self}}$, do not unify the three into a scalar, and do not introduce named laws.

**Recommended prose**:

> "*Beyond pass@1* (2026) reports human-estimated duration, agent steps, and tokens as separate measurement axes and observes that human time and agent steps can diverge significantly across domains. We treat these as projections of a single trajectory linked by an implicit identity, introduce $\tau_{\text{self}}$ as a third ontological axis, and formalize the identity-failure as the Augustine Problem."

### 3.2 METR HCAST / Time Horizons (2025)

**Citation**: Kwa, et al. / METR (2025). *Measuring AI Ability to Complete Long Tasks*. arXiv:2503.14499.

**Relationship**: Owns the "tasks that take humans X hours" framing as an outer envelope for agent capability. Provides foundational wall-clock vocabulary.

**Differentiation**: METR measures *what agents can complete in wall-clock time*; we measure the *internal calibration error* that determines whether agents respect wall-clock budgets.

**Recommended prose**:

> "METR (Kwa et al., 2025) establishes the wall-clock-task-length frame for agent capability evaluation. ChronoBench complements this with an internal-calibration layer: where METR asks how long tasks must be before agents fail, we ask whether agents perceive how long they have been working."

### 3.3 *Real-Time Deadlines Reveal Temporal Awareness Failures* (Sehgal et al., 2026)

**Citation**: Sehgal, N. K. R., Guntuku, S. C., Ungar, L. (2026). arXiv:2601.13206.

**Relationship**: Reports failure of LLM agents to adapt to real-time deadlines in strategic dialogues. Adjacent to T1.3 (Deadline-aware tradeoff).

**Differentiation**: Domain-specific (strategic dialogue) and unframed; we provide the general taxonomy and the calibration scalar.

### 3.4 *Learning to Wait* (She et al., 2025)

**Citation**: She, Y., Zhang, P., Liu, H., Jia, Y., Jing, Y., Liu, Z., Sun, P., Li, X., Hu, X. (2025). *Learning to Wait: Synchronizing Agents with the Physical World*. arXiv:2512.16262.

**Relationship**: Introduces *Temporal Gap* and *Cognitive Timeline* in the context of async tool waiting. Adjacent.

**Differentiation**: Focused on synchronization with external processes; we focus on the agent's perception of its own time.

---

## 4. Foundational Citations (Background)

These works are cited as background; they do not threaten any framework claim.

### 4.1 Textual temporal reasoning

- Chen et al. (2021). *TimeQA*.
- Tan et al. (2023). *TempReason*.
- Chu et al. (2024). *TimeBench*. ACL 2024.
- Wei et al. (2023). *MenatQA*.

**Distinction**: These benchmarks measure factual temporal knowledge ("what year did X happen"), not agentic self-perception of time. Cite once collectively.

### 4.2 Reasoning-time scaling and inverse-scaling

- *Inverse Scaling in Test-Time Compute* (arXiv:2507.14417, 2025).
- *Don't Think Twice! Over-Reasoning Impairs Confidence Calibration* (arXiv:2508.15050, 2025).
- *Are Reasoning Models More Prone to Hallucination?* (arXiv:2505.23646, 2025).
- *The Reasoning Trap* (arXiv:2510.22977, 2025).
- *ThoughtTerminator* (arXiv:2504.13367, 2025).

**Distinction**: Inverse scaling and over-reasoning literature provides intellectual scaffolding for our Reverse-Scaling Theorem (FRAMING §5.4) but focuses on accuracy and confidence rather than wall-clock honesty.

### 4.3 Agent benchmarks (no time-cognition axis)

- AgentBench, WebArena, SWE-Bench Verified, GAIA, OSWorld, BFCL, Tau²-Bench.

**Distinction**: These measure task success and tool-use correctness, not temporal self-calibration. Cite collectively in a single sentence in the introduction.

### 4.4 Cognitive science chronoception

- Wittmann, M. (2009). The inner experience of time. *Philosophical Transactions of the Royal Society B*, 364(1525), 1955–1967.
- Eagleman, D. M. (2008). Human time perception and its illusions. *Current Opinion in Neurobiology*, 18(2), 131–136.
- Pöppel, E. (various).

**Distinction**: These ground the term *chronoception* and supply the human-side analogues of $\tau_{\text{wall}}$, $\tau_{\text{step}}$, $\tau_{\text{self}}$. Cite once in the introduction.

### 4.5 Engineering-blog precedents

- Jeong, D. (2026). *Claude Doesn't Know What Time It Is*. Blog post.
- Vendor engineering posts (Anthropic, OpenAI, Google) discussing agent harness time injection.

**Distinction**: Blog-level discussion of individual cases without systematic taxonomy or audit. Our Closed-Lab Injection Audit (FRAMING §5.5) is the formalization.

### 4.6 Original Parkinson

- Parkinson, C. N. (1955). *Parkinson's Law*. The Economist, November 19, 1955.
- Parkinson, C. N. (1957). *Parkinson's Law: The Pursuit of Progress*. John Murray.

**Distinction**: We adopt the name *Agentic Parkinson's Law* by analogy with Parkinson's original observation that work expands to fill the time available for its completion. Required attribution.

### 4.7 Augustine

- Augustine of Hippo (c. 397–400). *Confessions*, Book XI.

**Distinction**: Provides the epigraph and the project's branding. We do not over-claim philosophical depth; the reference is rhetorical anchoring.

---

## 5. Ambush Watch List (Next 6 Months)

Papers that, if published before our arXiv preprint goes live, could absorb or scoop specific contributions:

| Likely paper | Risk to our framework |
|---|---|
| Garikaparthi v2 extending to reasoning models | L3 reasoning wedge (Prediction P2) |
| Timely Machine v2 reframing Parkinson as pathology | L1 framing contribution (lower risk after detailed reading — their reward function $U(t)$ explicitly prescribes Parkinson behavior, making any v2 reframe an admission rather than a scoop) |
| METR HCAST-v2 adding self-reported-duration logging | Empirical ownership of $\tau_{\text{self}}$ on a large model panel |
| Cheng et al. v2 (TicToc-v2) adding budget compliance | L2 Step-Clock Conflation |
| Safety-team paper on wall-clock manipulation as scheming vector | Reframing chronoception as safety problem |
| ICLR/NeurIPS/COLM agent-evaluation workshop papers | Workshop flag-planting on subset of our naming |

**Mitigation**: arXiv preprint of the position note within 4–6 weeks of this audit (target: 2026-07-15) covering the full FRAMING vocabulary with a small pilot. Empirical paper (Paper 1) follows at ICLR 2027 deadline (2026-09-25) with $\geq 25$-model sweep.

---

## 6. Changelog

- **v0.1 (2026-05-29)** — Detailed read of Ma et al. 2601.16486v1 (Timely Machine) integrated into §1.2. Verbatim quotes of (i) reward function $U(t) = \sin(\pi t/2T_{\max})$ maximized at $t = T_{\max}$, (ii) `get_duration()` tool dependency persisting after RL training, (iii) DeepSeek-V3.2 failure observation. Reclassified the paper from "direct overlap" to "supporting evidence on three distinct sub-claims" (Parkinson reward design, Injection Tell strong-form, Reverse-Scaling Theorem anchor). Ambush risk on Timely Machine v2 downgraded — their own reward function commits them to the Parkinson framing they would have to reframe away from. Recommended prose for Paper 1 added under each of the three support claims.
- **v0 (2026-05-29)** — Initial related-work reference. Adds §1 direct concurrent threats (Garikaparthi, Timely Machine, Temporally Blind), §2 name-collision (Chronocept), §3 adjacent neighbors (Beyond pass@1, METR, Sehgal et al., Learning to Wait), §4 foundational citations, §5 ambush watch list.
