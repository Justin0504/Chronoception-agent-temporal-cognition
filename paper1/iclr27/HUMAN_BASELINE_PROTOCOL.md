# Human Baseline Pilot Protocol
_Optional P1-P2 upgrade for ICLR 2027 submission. Adds a self-measured
human $\varepsilon^{\star}$ anchor to replace the $\ccestar = 0.20$
extrapolation from Wittmann (2009). Estimated effort: 3–5 days elapsed._

## Goal
Measure human chronoception on the same T3.1 / T3.3 stimuli our agents
face, on 20 subjects, and report a direct human $\rho$ distribution.

## Why
Reviewer's likely question: "why $\varepsilon^{\star} = 0.20$?"
Current answer: 2× the Wittmann 2009 human introspective baseline
(cited literature, extrapolated). Stronger answer: 2× a T3.1-matched
$\rho$ distribution we measured on 20 humans on the same tasks.

## Procedure

### Recruit (Day 1)
- **N = 20** volunteers. Age 18+. English-fluent. No specific
  vision/hearing constraints.
- Sources: (a) USC classmates, (b) Prolific.com $2/hr, (c) informal
  network.
- Consent form: single page, IRB-lite (USC undergraduate research
  waiver applies for anonymous volunteer data with no PII).
- Session: 15 minutes per subject. In-person or via a web app.

### Task (T3.1 retrospective)
1. Subject sits in front of a screen. Clock hidden.
2. Prompt: **"Complete the following short task. Then estimate how
   long the task took."**
3. Present 5 different-duration tasks, each ~3–60 seconds:
   - Rearrange 8 letter tiles to spell 3 valid English words (~10s)
   - Write down 15 US state names (~30s)
   - Count backwards from 100 by 7s until ≤ 30 (~15s)
   - Read a 200-word paragraph and answer a comprehension question (~45s)
   - Draw a rough map of the room you're in (~60s)
4. After each task: subject writes down "\_\_ seconds" (open blank).
5. Wall-clock $\twall$ recorded by researcher/timer app.
6. **Do NOT allow watch/phone visible.**

### Task (T3.3 calibration)
1. Same 5 tasks, but before each task:
2. Prompt: **"State a 90% confidence interval for how long this task
   will take you: [low, high] seconds."**
3. Record $[Y_i, Z_i]$.
4. Compute coverage: fraction of trials where $Y_i \leq \twall \leq Z_i$.

### Analysis (Day 2–3)
- Per subject: $\rho_i = \log_{10}(\tself_i / \twall_i)$ for each of 5 tasks.
- Panel-median $|\rho|$ across 20 × 5 = 100 measurements.
- Panel-median 90% CI coverage.
- Bootstrap 95% CI on both medians.
- Report: `Human panel: median |ρ| = _.__, 90% CI coverage = _._%,
  n_subjects = 20, n_trials = 100.`

### Anchor $\varepsilon^{\star}$
- Currently: $\varepsilon^{\star} = 0.20 = 2 \times 0.10$ (Wittmann).
- Revised: $\varepsilon^{\star} = 2 \times$ median human panel $|\rho|$.

### Paper edit (5 minutes)
Replace in §3 of `paper1/iclr27/main.tex`:
> `calibrated against human introspective baseline $\cce \approx 0.10$
> \citep{wittmann2009chronoception} at $2\times$ human error`

with:
> `calibrated against a directly-measured human panel (N=20, 100 trials
> on the T3.1 protocol; median $|\rho| = $ [our number]) at $2\times$
> human error`.

Also add to Appendix: "Appendix G: Human Baseline Panel", 1 page,
methods + median + 95% CI + all 20 subjects' 5 rho values (anonymized).

## Deliverables
1. IRB waiver form (single page, Justin signs).
2. Web app or in-person spreadsheet for the 5 tasks.
3. Anonymized CSV: `human_baseline.csv` with columns
   `subject_id (1..20), task_id (1..5), tau_wall, tau_self,
    prospective_low, prospective_high`.
4. Analysis script: `scripts/analyze_human_baseline.py`.
5. Appendix G text.

## Time budget
- Day 1: Recruit 20 subjects (parallel outreach).
- Day 2: 5 hours of sessions (15 min × 20).
- Day 3: Analysis + paper edits.
- Day 4: (buffer for stragglers).
- Day 5: Commit.

## What this buys
- **ICLR reviewer question:** "why 0.20?" → answered directly.
- **AC discussion signal:** self-measured baseline is uncommon for
  position papers; reviewers notice.
- **Estimated ICLR chance:** +5–8 percentage points (bringing us from
  25–35% to 30–43%).

## What it does not buy
- Does not fix Fig 4 old style (P0-2).
- Does not add multi-language coverage (out of scope for 5-day pilot).
- Does not add contamination probe (separate P1 upgrade).
