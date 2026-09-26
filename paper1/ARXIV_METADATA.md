# arXiv Submission Metadata & Citation Entries

_Fill in the arxiv submission form with the fields below. Replace
`ARXIV_ID` placeholders after your paper receives its assigned identifier
(typically 1–2 days after submission)._

---

## 1. Submission form fields

**Title**
```
Chronoception Must Be Installed: The Augustine Problem in LLM Agents
```

**Authors** (single-author submission at this stage)
```
Aojie Yuan
```
Affiliation: `University of Southern California`
Email: `aojieyua@usc.edu`

**Comments** (arxiv "Comments" field — visible on the abstract page)
```
37 pages, 7 figures, 13 tables. Position paper with layered evidence
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

> **Source of truth is `arxiv-v0/main.tex`.** This copy is hand-maintained and
> has drifted before: it once carried "24,008 METR HCAST runs" against the
> paper's 14,709, and the superseded "<5% of its wall-clock budget" claim that
> the paper's own data contradicts. Re-derive it from the `abstract`
> environment whenever that changes, and diff the numbers.

_(Plain text — arxiv strips most LaTeX. Unicode is fine and reads better than
ASCII transliteration.)_

```
LLM agents are trained on tokens and deployed in wall-clock time. We
argue they cannot close that gap from training alone. Under any loss
that is a functional of token sequences — from next-token prediction
through RLHF to reasoning supervision — the gradient is invariant to
how long the episode took, so no amount of scale, context, or
reasoning compute installs a representation of elapsed time.
Chronoception must be installed from outside the loss.

We name the failure the Augustine Problem, decompose it along the
three times an agent must keep aligned (tau_wall, tau_step,
tau_self), and measure it on ChronoBench: 9 sub-capabilities x 14
agents from 7 vendors, ~5,900 trajectories. Every agent leaves >=89%
of a stated wall-clock budget unspent, and a 60x increase in that
budget buys 1.4x more work — Parkinson's law holds, at a tenth of the
strength it requires. Injecting the current date repairs what agents
say, lifting date accuracy to >=96% panel-wide, and moves what they
do by |Delta CAR| <= 0.01. Three closed labs have independently
reached the same workaround, routing the wall-clock into the token
stream for consumer products (3/3 inject the date) but not for
developer tools (0/3): the harness perceives time on the model's
behalf.

Reasoning makes the gap worse rather than better. We show E[|rho|
given reasoning budget K] is monotone non-decreasing in K and confirm
it four ways, including a sign flip reproduced on an independent
vendor's training pipeline; nominal 90% intervals on self-reported
duration achieve 0-77% coverage. The consequence is a deployment
bound, T_max ~ 1/epsilon, supported on 14,709 METR HCAST runs
(one-sided p = 0.040): autonomous-agent horizons are limited by
chronoception, not by intelligence.

The gap is structural but not permanent. A LoRA fine-tune on
wall-clock-supported targets crosses our calibration threshold after
~60 s of training — the constructive converse of the impossibility
argument. Code, trajectories, and a locked pre-registration are
released.
```

---

## 3. Citation entries (fill in ARXIV_ID after assignment)

### BibTeX (canonical for most CS venues)
```bibtex
@article{yuan2026augustine,
  title   = {Chronoception Must Be Installed: The Augustine Problem in LLM Agents},
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
  title   = {{C}hronoception {M}ust {B}e {I}nstalled: {T}he {A}ugustine {P}roblem in {LLM} {A}gents},
  year    = {2026},
  eprint  = {ARXIV_ID},
  eprinttype = {arXiv},
  eprintclass = {cs.AI},
  url     = {https://arxiv.org/abs/ARXIV_ID}
}
```

### Plain (arxiv "cite as" style)
```
Aojie Yuan. Chronoception Must Be Installed: The Augustine Problem in
LLM Agents. arXiv:ARXIV_ID [cs.AI], September 2026.
```

### APA 7
```
Yuan, A. (2026). Chronoception must be installed: The Augustine
problem in LLM agents [Preprint]. arXiv. https://arxiv.org/abs/ARXIV_ID
```

### Chicago author-date
```
Yuan, Aojie. 2026. "Chronoception Must Be Installed: The Augustine
Problem in LLM Agents." arXiv preprint arXiv:ARXIV_ID.
```

---

## 4. Social media / announcement draft

### Short (Twitter/X, ≤280 chars)
```
New preprint: Chronoception Must Be Installed 🧵

LLM agents don't perceive their own time.
We prove why — under any token-only loss, gradient carries no
wall-clock signal (CIT).

Then: reasoning-token expansion makes it WORSE (Reverse-Scaling).

arxiv.org/abs/ARXIV_ID
```

### Medium (LinkedIn / academic Twitter thread)
```
🔥 New preprint: "Chronoception Must Be Installed: The Augustine Problem in LLM Agents"

We show LLM agents can't perceive wall-clock time, and prove this
gap is structural — not fixable by additional scale or reasoning
compute.

Key findings across 14 agents / 7 vendors / ~5,900 trajectories:

• Every agent leaves >=89% of its wall-clock budget unspent
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
- [ ] If you post on X, look up the real handles first. An earlier draft of
  this file suggested three (@wittmann, @garikaparthi, @ma_timelymachine) that
  were never verified to exist — do not tag an account you have not checked.
