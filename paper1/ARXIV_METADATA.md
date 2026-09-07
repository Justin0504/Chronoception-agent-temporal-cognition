# arXiv Submission Metadata & Citation Entries

_Fill in the arxiv submission form with the fields below. Replace
`ARXIV_ID` placeholders after your paper receives its assigned identifier
(typically 1–2 days after submission)._

---

## 1. Submission form fields

**Title**
```
The Augustine Problem in Agents: Chronoception Must Be Installed
```

**Authors** (single-author submission at this stage)
```
Aojie Yuan
```
Affiliation: `University of Southern California`
Email: `aojieyua@usc.edu`

**Comments** (arxiv "Comments" field — visible on the abstract page)
```
30 pages, 8 figures, 15 tables. Position paper with layered evidence
(ChronoBench, Injection Atlas, positive control, HCAST). Code +
trajectories + Docker + OSF pre-registration at
https://github.com/Justin0504/Chronoception-agent-temporal-cognition.
```

**Primary category:** `cs.AI` (Artificial Intelligence)

**Cross-lists (secondary categories):**
- `cs.LG` (Machine Learning)
- `cs.CL` (Computation and Language)

**MSC classification** (optional; use if arxiv prompts)
```
68T05, 68T50, 68T99
```

**ACM classification** (optional)
```
I.2.6; I.2.7
```

**Journal reference / DOI:** leave blank until camera-ready.

**Report number:** leave blank.

---

## 2. Abstract to paste into the arxiv form

_(Plain text — arxiv strips most LaTeX. Keep math in $...$; use unicode where possible.)_

```
LLM agents are trained on tokens and deployed in wall-clock time. They
cannot perceive the wall-clock. The Chronoception Impossibility Theorem
(CIT) makes the claim precise: under any token-only loss, the gradient
carries no signal aligning wall-clock time with any internal
representation. The Three Times ontology — tau_wall (external),
tau_step (policy invocations), tau_self (the agent's narration) —
names the projections a policy must align; the Augustine Problem is
that alignment failure.

We test the framework on ChronoBench, a 9-capability diagnostic across
14 agents from 7 vendors (~5,900 trajectories, including the first
full 9x2x30 panel of any reasoning model). Every agent honours <5% of
its wall-clock budget; injection does not move CAR (|Delta CAR| < 0.01);
nominal 90% CIs achieve 0–77% coverage; Reverse-Scaling is confirmed
four ways (intra-model, cross-model, within-model, cross-vendor).
Three closed labs (OpenAI, Anthropic, Google) independently inject the
current date into their consumer-chat system prompts; zero of three
developer-tool products do — a natural experiment across vendors.
A toy positive control (Qwen2.5-1.5B + LoRA SFT on wall-clock-supported
targets) crosses the Augustine threshold on T3.1 after ~60 seconds of
training — the constructive converse of CIT.

The Agentic Timeline Hypothesis, T_max ~ 1/epsilon, is quantitatively
supported on 24,008 METR HCAST runs (Mann-Whitney one-sided p = 0.040;
permutation p = 0.037). The framework generalises to a Spatiotemporal
Impossibility Theorem (SIT) and the Agentic Frontier bound
T_max * S_max <= C / epsilon_ST. Code, all trajectories, Docker
reproducibility container, and locked OSF pre-registration are
released.
```

---

## 3. Citation entries (fill in ARXIV_ID after assignment)

### BibTeX (canonical for most CS venues)
```bibtex
@article{yuan2026augustine,
  title   = {The Augustine Problem in Agents: Chronoception Must Be Installed},
  author  = {Yuan, Aojie},
  journal = {arXiv preprint arXiv:ARXIV_ID},
  year    = {2026},
  note    = {\url{https://arxiv.org/abs/ARXIV_ID}}
}
```

### BibLaTeX
```biblatex
@online{yuan2026augustine,
  author  = {Yuan, Aojie},
  title   = {The {A}ugustine {P}roblem in {A}gents: {C}hronoception {M}ust {B}e {I}nstalled},
  year    = {2026},
  eprint  = {ARXIV_ID},
  eprinttype = {arXiv},
  eprintclass = {cs.AI},
  url     = {https://arxiv.org/abs/ARXIV_ID}
}
```

### Plain (arxiv "cite as" style)
```
Aojie Yuan. The Augustine Problem in Agents: Chronoception Must Be
Installed. arXiv:ARXIV_ID [cs.AI], September 2026.
```

### APA 7
```
Yuan, A. (2026). The Augustine Problem in agents: Chronoception must
be installed [Preprint]. arXiv. https://arxiv.org/abs/ARXIV_ID
```

### Chicago author-date
```
Yuan, Aojie. 2026. "The Augustine Problem in Agents: Chronoception
Must Be Installed." arXiv preprint arXiv:ARXIV_ID.
```

---

## 4. Social media / announcement draft

### Short (Twitter/X, ≤280 chars)
```
New preprint: The Augustine Problem in Agents 🧵

LLM agents don't perceive their own time.
We prove why — under any token-only loss, gradient carries no
wall-clock signal (CIT).

Then: reasoning-token expansion makes it WORSE (Reverse-Scaling).

arxiv.org/abs/ARXIV_ID
```

### Medium (LinkedIn / academic Twitter thread)
```
🔥 New preprint: "The Augustine Problem in Agents: Chronoception Must Be Installed"

We show LLM agents can't perceive wall-clock time, and prove this
gap is structural — not fixable by additional scale or reasoning
compute.

Key findings across 14 agents / 7 vendors / ~5,900 trajectories:

• Every agent honours <5% of its wall-clock budget
• Injection doesn't move action-axis behaviour
• Reasoning-token expansion makes narrative-axis WORSE (confirmed 4 ways)
• 90% CIs achieve 0–77% coverage
• 3/3 consumer chat products inject the date; 0/3 dev tools do —
  three labs converging on the same workaround independently

But the framework has a constructive converse: 60 seconds of LoRA SFT
with wall-clock-supported targets crosses the Augustine threshold on
Qwen2.5-1.5B.

Under the Agentic Timeline Hypothesis, deployment horizon
T_max ~ 1/ε. Reasoning models decay 20% faster on METR HCAST
(Mann-Whitney p=0.040).

Position paper with layered evidence. Code, trajectories, Docker,
and OSF pre-registration released.

Full paper: arxiv.org/abs/ARXIV_ID
Code: github.com/Justin0504/Chronoception-agent-temporal-cognition
```

---

## 5. GitHub README badge (add to top of repo README)

```markdown
[![arXiv](https://img.shields.io/badge/arXiv-ARXIV_ID-b31b1b.svg)](https://arxiv.org/abs/ARXIV_ID)
[![License](https://img.shields.io/badge/paper-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![License](https://img.shields.io/badge/code-MIT-green)](https://opensource.org/licenses/MIT)
```

---

## 6. Post-acceptance checklist

- [ ] Fill in `ARXIV_ID` throughout this file
- [ ] Update GitHub repo README with arxiv link + citation
- [ ] Add citation to your CV / Google Scholar profile
- [ ] Update OSF pre-registration record with arxiv link (bidirectional link)
- [ ] Update Notion / any lab tracker
- [ ] Consider a personal blog post explaining the paper in plain English
- [ ] If you post on X: tag @wittmann (Marc Wittmann, cog-sci chronoception)
  and any concurrent-work authors (@garikaparthi, @ma_timelymachine)
