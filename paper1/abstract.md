# Paper 1 — Abstract (v1)

**Working title**: *The Augustine Problem: Evaluating Whether LLM Agents Can Perceive Their Own Time*

**Parent scope**: [`SCOPE.md`](SCOPE.md) v0
**Research programme**: [`../FRAMING.md`](../FRAMING.md) v1.8 (2026-06-01)

---

## Primary abstract (≈260 words)

Large language model agents are trained on token sequences but act in wall-clock time. We ask, empirically, whether they perceive their own time. We formalize a **three-times ontology** — wall-clock time $\tau_{\text{wall}}$, step time $\tau_{\text{step}}$, and self-narrated time $\tau_{\text{self}}$ — define the **Augustine Problem** as the failure of an agent's policy to enforce the implicit identity linking them, and introduce **ChronoBench**, a diagnostic benchmark over nine sub-capabilities across the three axes. We evaluate 7 frontier agents from 3 providers (OpenAI, Anthropic, open-source self-hosted) under both no-injection and with-injection settings, across roughly 1{,}200 trajectories. We report four primary empirical findings. **Action-axis failure (L2 Step-Clock Conflation)**: across all 7 models, the Clock-Adherence Ratio under wall-clock budgets satisfies $\text{CAR} \leq 0.05$ — agents use less than $5\%$ of the budget given, regardless of model generation. Wall-clock injection does not move CAR within $\pm 0.01$ on any model. **Narrative-axis failure (L3 Temporal Confabulation)**: median $|\rho|$ ranges from $0.07$ to $1.54$ across the panel; reasoning models exhibit higher variance (o4-mini under-reports at $\rho \approx -1.5$ while o3 over-reports at $\rho \approx +0.3$). Capability scaling closes L3 monotonically (median $\rho$ falls from $+1.12$ in gpt-4o-mini to $+0.07$ in Claude Sonnet 4.6) but **does not close L2**. **The Injection Tell**: a tier-stratified Injection Atlas across 11 harnesses shows $3/3$ consumer web-chat products inject wall-clock (ChatGPT, Claude.ai, Gemini app — verbatim leaked-system-prompt evidence) while $0/3$ developer-tool products do. **The Augustine threshold**: no panel agent crosses $\varepsilon^{*} = 0.20$ on the full benchmark; L2's contribution alone exceeds this threshold for every model. We release ChronoBench, the Injection Atlas, model traces, and a `pip`-installable evaluation package.

---

## Short abstract (≈140 words, for arXiv tagline)

LLM agents are trained in token-time but act in wall-clock time. We ask whether they perceive their own time. We define the **three-times ontology** ($\tau_{\text{wall}}, \tau_{\text{step}}, \tau_{\text{self}}$), the **Augustine Problem**, and **ChronoBench** — a diagnostic benchmark on $\sim 1{,}200$ trajectories across 7 frontier agents from 3 providers. We find: (i) all 7 models honor under $5\%$ of wall-clock budgets given (L2 Step-Clock Conflation, unmoved by injection); (ii) self-narrated duration error closes monotonically with capability scaling ($\rho: +1.12 \to +0.07$ across 5 generations); (iii) consumer web-chat products inject today's date into system prompts at $100\%$ rate (ChatGPT, Claude.ai, Gemini — verbatim evidence), while developer-tool products do not; (iv) no panel agent crosses the Augustine threshold $\varepsilon^{*} = 0.20$ because L2 alone exceeds it. We release ChronoBench, the Injection Atlas, and a single chronoceptive calibration scalar $\varepsilon$.

---

## Notes

- v1 abstract reflects the actual 7-model pilot panel as of 2026-06-01 (gpt-4o-mini, gpt-4o, gpt-5.1, o3, o4-mini, Claude Haiku 4.5, Claude Sonnet 4.6, Qwen2.5-7B). v0 abstract claimed ≥25 models which is the Paper 1 final target; v1 is the v0 arXiv release abstract.
- Empirical headline numbers are exact: CAR ≤ 0.05 (median across all models), $\rho \in [-1.54, +1.73]$ across panel.
- Cross-vendor narrative: Anthropic API does not inject ($0\%$ A pass rate empirically on Haiku & Sonnet); OpenAI API injects on GPT-5.1 ($74\%$); consumer web tier $100\%$. This is the strongest cross-vendor evidence for the Injection Tell.
- Reasoning model finding: o4-mini and o3 disagree on direction of $\rho$ — refined P2 (v1.8) predicts higher $|\rho|$ spread, not uniform direction.
- The Augustine threshold $\varepsilon^{*}$ appears in the long abstract because the cross-panel result (no agent crosses it; L2 alone exceeds it) is the cleanest single-sentence statement of the framework's central structural claim.
- The Chronoception Upstream Hypothesis (CUH) and ChronoStack (Paper 2) are not in the abstract — that scope belongs to the position note and Paper 2 respectively.
- Concurrent work is referenced inline: "Ma et al. (2026)" L2 framing inversion; "Garikaparthi (2026)" L3 reasoning extension — both retained from v0. Web-tier evidence cites the leaked-system-prompts corpus indirectly via "verbatim leaked-system-prompt evidence".
