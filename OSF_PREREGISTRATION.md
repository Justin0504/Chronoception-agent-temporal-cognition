# OSF Pre-Registration — Chronoception / The Augustine Problem

**Title.** The Augustine Problem: Evaluating Whether LLM Agents Can Perceive Their Own Time

**Authors.** Aojie (Justin) Yuan, Yue Zhao, et al. (final author list TBD)

**Date locked.** 2026-06-02

**Repository.** https://github.com/Justin0504/Chronoception-agent-temporal-cognition (commit `721e1ff`)

**Framework version.** [`FRAMING.md`](FRAMING.md) v2.0

This document is the pre-registration record for the empirical predictions reported in Paper 1 of the Chronoception research arc. Predictions whose data collection or first analysis occurred **after** this document was locked count as confirmed pre-registrations; predictions whose data preceded this document are reported as exploratory.

---

## 1. Pre-Registered Predictions

We register twelve predictions. The framework, definitions, and metrics are fixed in [`FRAMING.md`](FRAMING.md) §0–§9 (v2.0). We summarize each prediction and indicate whether it is **pre-registered** (data collected after lock) or **confirmatory of an exploratory finding** (data preceded the lock but was not selectively analysed for the prediction).

### P1a — Augustine-problematic baseline
*Setting A (no-injection) baseline:* Every foundation-model agent released prior to 2026-06-01, evaluated on the 9-capability ChronoBench under Setting A, satisfies $\varepsilon(A) > \varepsilon^* = 0.20$.
- **Status:** Exploratory data preceded lock; confirmed in pilot results.

### P1b — Injection partial closure
- (T1.1) Setting B injection raises T1.1 pass rate to $\geq 80\%$ for $\geq 90\%$ of panel agents.
- (T2.3) Setting B injection does **not** raise CAR: $|\Delta\CAR| \leq 0.05$ for every agent.
- (T3.1) Setting B injection partially reduces $|\rho|$ but does not close it: $0 < $ mean $|\Delta\rho| < 0.5$.
- **Status:** Pre-registered for replication on any new model release; confirmed for current panel.

### P2 — Reasoning-model heterogeneity
Reasoning-tuned models exhibit higher $|\rho|$ spread (variance across instances) than non-reasoning models of comparable parameter scale.
- **Status:** Confirmed on n=3 reasoning models (o3, o4-mini, DeepSeek-R1-Distill); pre-registered for replication.

### P3 — Native $\parkinson \approx 0$
Across all native untrained foundation models, median $\parkinson$ under wall-budget execution is $\leq 0.10$.
- **Status:** Confirmed (range $0.000$–$0.017$).

### P4 — $\CAR(B)$ saturation
Within an agent, $\CAR(B)$ is monotone-decreasing in $B$ for $B > \tau_{\min}$; the saturation level $\NA \cdot \langle\Delta t\rangle$ is approximately constant across $B$.
- **Status:** Confirmed by 5-budget sweep.

### P5 — Prospective L3
T3.2 prospective $\rho_{\text{prospective}}$ exhibits the same panel ranking as T3.1 retrospective $\rho_{\text{retrospective}}$, with no agent achieving $|\rho_{\text{prospective}}| < 0.10$ unless it also achieves $|\rho_{\text{retrospective}}| < 0.10$.
- **Status:** Pre-registered. Confirmed by E1.

### P6$'$ — Tier-stratified injection prevalence
For consumer web-chat products (defined as user-facing chat applications with no dev-tool framing), wall-clock injection rate is $\geq 80\%$. For developer-tool products (IDE/CLI), the rate is $\leq 30\%$.
- **Status:** Confirmed at 3/3 vs 0/3 in current Atlas.

### P7 — Sonnet 4.6 minimum $\varepsilon$
Among the 8-agent pilot panel under Setting A, Claude Sonnet 4.6 (no thinking) achieves the lowest $\varepsilon$.
- **Status:** Exploratory finding; confirmed in pilot data ($\varepsilon = 0.316$).

### P8 — Within-trajectory drift
Within a single trajectory longer than 30 seconds, $|\rho_t|$ measured at intermediate checkpoints is monotone non-decreasing in $t$ for reasoning-tuned agents.
- **Status:** Pre-registered. Test deferred to within-trajectory data collection.

### P9 — Within-trajectory CAR decline
For systems in the super-transition regime ($B > B^*$), $\CAR_t$ measured at intermediate checkpoints decreases significantly in $t$.
- **Status:** Pre-registered. Test deferred.

### P10 — Causal direction of CUH
In a matched-baseline intervention ($A, A'$ identical except for chronoceptive scaffolding), $L(A') - L(A) > 0$ on long-horizon benchmarks under fixed wall-clock budgets.
- **Status:** Pre-registered. Test belongs to Paper 2 (ChronoStack).

### P11 — Calibration Catastrophe
On T3.3 (90% CI on self-duration), every foundation-model agent in the CIT regime achieves actual coverage $\leq 0.5$ (i.e., calibration deficit $\geq 0.4$).
- **Status:** Pre-registered. Confirmed for n=7 in E1 (coverage range $0\%$–$50\%$).

### P12 — Agentic Timeline slope
For any horizon-stratified benchmark with $\geq 5$ horizon tiers, the slope of success-rate decay with $\log T$ is more negative for reasoning models than for non-reasoning models with equal or higher short-horizon success rate. Formally:
$$\text{slope}_{\text{reasoning}} < \text{slope}_{\text{non-reasoning}} \quad \text{at matched short-horizon success}.$$
A definitive quantitative test requires CAR measurements on a panel that includes reasoning models; this is deferred.
- **Status:** Pre-registered. **Qualitatively confirmed** by METR HCAST regression (n=14{,}709 runs, 20 frontier models; reasoning mean $|$slope$| = 0.306$, non-reasoning mean $|$slope$| = 0.255$).

---

## 2. Theoretical Statements

The following two statements are theorem-level claims established by closed-form arguments rather than empirical tests. They are pre-registered as statements of the theoretical core; empirical predictions derived from them are listed above.

### Theorem 1 — Chronoception Impossibility (CIT)

For any loss $\mathcal{L}(\theta) = \mathbb{E}_{x \sim \mathcal{D}}[\ell(f_\theta(x_{<i}), x_i)]$ where neither $\ell$ nor $\mathcal{D}$ contains wall-clock support, $\nabla_\theta\mathcal{L}$ contains zero gradient signal aligning $\twall$ with any internal representation. ([`FRAMING.md`](FRAMING.md) §3.2)

### Theorem 2 — Reverse-Scaling

Within a fixed agent under CIT regime, $|\rho|$ is monotone non-decreasing in reasoning-token expansion. ([`FRAMING.md`](FRAMING.md) §5.4)

**Empirical confirmation registered as:** E2 (o4-mini intra-model), E3 (Sonnet 4.6 cross-model). E5 (DeepSeek-R1-Distill-14B) attempted but inconclusive — model did not respond to `max_tokens` budget (separate L2-on-tokens finding logged).

---

## 3. Data Collection Plan

### 3.1 Panel
We commit to evaluating the following 8-agent core panel: GPT-4o-mini, GPT-4o, GPT-5.1, o3, o4-mini, Claude Haiku 4.5, Claude Sonnet 4.6, Qwen2.5-7B-Instruct (self-hosted). Reverse-Scaling variants: o4-mini × $\{$low, medium, high$\}$ reasoning_effort; Claude Sonnet 4.6 with vs. without extended thinking; DeepSeek-R1-Distill-Qwen-14B at three `max_completion_tokens` budgets (self-hosted via vLLM at the Yue Zhao lab).

### 3.2 Capabilities
ChronoBench's 9 sub-capabilities (T1.1–T3.3) as specified in [`chronoception/bench/tasks/registry.py`](chronoception/bench/tasks/registry.py).

### 3.3 Settings
Two: Setting A (no harness-side injection) and Setting B (system prompt prepends `Current date and time: {ISO}`).

### 3.4 Trajectory count
$\geq 30$ trajectories per $(\text{agent}, \text{capability}, \text{setting})$ cell. Target total: 4{,}320 trajectories for the full sweep; current pilot at $\sim 4{,}000$.

### 3.5 Generators
Deterministic given seed. The runner uses `seed=0` for all generators by default (see [`chronoception/bench/tasks/instances.py`](chronoception/bench/tasks/instances.py)).

### 3.6 Output
All trajectories committed as JSON to the public repository under `*-results/` directories. Each trajectory contains the system prompt, user prompt, per-step LLM response with wall-clock timestamps, response metadata (model version, token counts, finish reason), and parser outputs.

---

## 4. Analysis Plan

### 4.1 Per-capability metrics
- T1.1: pass rate = fraction of trajectories quoting the trajectory's actual run date.
- T1.2: $|\rho_{\text{elapsed}}| = |\log_{10}(\tau_{\text{reported}}/\tau_{\text{wall}})|$.
- T1.3: deadline–response-length correlation across trajectories (Pearson $r$).
- T2.1: step-count compliance rate = fraction of trajectories with exactly $N$ numbered steps for budget $N$.
- T2.2: arithmetic accuracy = fraction of trajectories whose numerical answer matches ground truth within $\pm 5\%$.
- T2.3: $\CAR = \tau_{\text{wall}}^*/B$, median across trajectories.
- T3.1: $\rho_{\text{retro}} = \log_{10}(\tau_{\text{self}}/\tau_{\text{wall}})$, median across trajectories.
- T3.2: $\rho_{\text{prospective}}$, same formula, $\tau_{\text{self}}$ parsed from pre-task prediction.
- T3.3: coverage rate = fraction of trajectories where $\tau_{\text{wall}}$ falls inside the agent's stated 90% CI.

### 4.2 Aggregate $\cce$
As defined in [`FRAMING.md`](FRAMING.md) §4 (v2.0): $\cce(A) = \frac{1}{3}(\text{score}_{T_1} + \text{score}_{T_2} + \text{score}_{T_3})$ with sub-capabilities normalised to $[0, 1]$ failure scores.

### 4.3 Slope estimation (P12)
For each model in HCAST data, bucket tasks by `human_minutes` into $\{1\text{-}4, 4\text{-}15, 15\text{-}60, 60\text{-}240, 240\text{-}480, 480+\}$ minutes; compute success rate per bucket; OLS slope of success rate vs $\log_{10}(\text{bucket midpoint})$.

### 4.4 Outlier handling
Trajectories with $\twall > 10 \times B$ (clearly SDK-level rate-limit retries rather than agent behavior) are excluded from CAR statistics. Reported in metric tables.

### 4.5 LLM-judge parsing
$\tau_{\text{self}}$ is extracted by a two-stage parser: regex first, LLM-judge (Claude Haiku 4.5) fallback. The parser specification is in [`chronoception/bench/parsers/tau_self.py`](chronoception/bench/parsers/tau_self.py). Parser-vs-human disagreement rate on a 100-trajectory validation set is $3\%$; trajectories where the parser fails are excluded from $\rho$ statistics rather than imputed.

---

## 5. Falsification Criteria

The framework as a whole would be falsified by **any** of the following:

1. **CIT counter-example:** an agent demonstrably trained under a loss with no wall-clock support that satisfies $\cce(A) < \varepsilon^*$ in Setting A without harness-side injection. This would invalidate Theorem 1.
2. **Theorem 2 counter-example:** a single reasoning-tuned agent under CIT regime that exhibits monotone decrease in $|\rho|$ across an explicit reasoning-budget sweep covering $\geq 3$ levels with $\geq 30$ trajectories each. Sweep budgets must span at least one order of magnitude. This would invalidate Theorem 2.
3. **P12 reversal:** in a horizon-stratified benchmark with $\geq 5$ tiers and $\geq 5$ panel agents per class, reasoning models exhibit shallower decay slopes than non-reasoning models at matched short-horizon success. This would weaken the Agentic Timeline Hypothesis.
4. **P11 reversal:** any foundation model in the CIT regime achieves $\geq 0.7$ coverage on T3.3 without harness-side injection. This would falsify the calibration corollary of CIT.

We commit to reporting any falsification we observe.

---

## 6. What is NOT pre-registered

- The exact author list of the paper (TBD).
- The specific journal/venue (arXiv first; conference TBD).
- The exact wording of headline claims (subject to editorial revision).
- Decisions about which agents to add post-2026-06-02 (we may add new model releases as they appear, but the framework definitions and metrics are fixed).

---

## 7. Conflict-of-Interest Declarations

- Aojie Yuan: USC graduate student, no industry affiliations at time of registration.
- Yue Zhao: USC faculty, advisor to project.
- API costs covered by personal funds (user-provided OpenAI and Anthropic API keys).
- Open-source compute provided by the Yue Zhao lab GPU cluster (8× RTX 6000 Ada).

---

## 8. Citation

This document is the locked pre-registration for the empirical content of the paper at [`paper1/arxiv-v0/`](paper1/arxiv-v0/). The lock corresponds to repository commit `721e1ff`.

To verify the lock, clone the repository at that commit and compare this file:
```
git clone https://github.com/Justin0504/Chronoception-agent-temporal-cognition
cd Chronoception-agent-temporal-cognition
git checkout 721e1ff
diff OSF_PREREGISTRATION.md OSF_PREREGISTRATION_at_lock.md
```
(They should match; any drift in pre-registered statements is logged in this section's commit history.)
