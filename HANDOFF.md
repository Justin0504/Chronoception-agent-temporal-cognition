# Six-Day Handoff — 2026-06-10 to 2026-06-16

Justin is offline for six days. This file documents what is **safe to touch**, what is **deliberately frozen**, and what would be **most useful for a collaborator to work on** in his absence.

If you want to do something not listed here, that's fine — open a branch, push your work, and Justin will integrate when he returns. Just don't force-push to `main` or rewrite history.

---

## What is frozen

The Paper 1 LaTeX is finished. Do not refactor it during the handoff window. The current frozen artifacts are:

- `paper1/augustine_problem_v8_dual_scale.pdf` — the latest PDF
- `paper1/augustine_overleaf.zip` — self-contained Overleaf package
- `FRAMING.md` v2.5 — framework source of truth
- `OSF_PREREGISTRATION.md` locked at repo commit `a6f20c3`

If you find a small typo or a broken cross-reference, fix it directly and commit; do not rewrite paragraphs.

The 4{,}000 trajectory JSONs under `pilot-results/`, `e1-results/`, `e2-results/`, `e3-results/`, `e5-results/` are frozen as the dataset Paper 1 is built on. Do not modify; if you re-run experiments, write into new directories.

---

## What is safe to touch

- **Paper 2 (ChronoStack) scoping.** Write a `paper2_chronostack/SCOPE.md` and start sketching the four installation routes (loss / tool / scaffolding / architecture). The A.1 toy positive control is in `paper2_chronostack/toy_a1/` and provides a starting point for the loss-extension route.
- **Paper 3 (Agentic Frontier) scoping.** Extend `PAPER3_SCOPE.md` with experiment specifications for E6–E10 if you want to. Don't run E6 (SWE-Bench Lite spatial pilot) yet — that costs ~$80 in API and Justin should approve.
- **New writing in Paper 1 appendices.** If you find a topic that deserves an extra appendix (e.g., a more detailed analysis script, a derivation), add it as a new `paper1/arxiv-v0/sections/G_*.tex` and hook it from `main.tex`. The numbering scheme is A–F today.
- **Analysis scripts.** Anything in `scripts/` is fair game. The existing analysers (`compute_metrics.py`, `analyze_e1.py`, `p12_hcast_regression.py`, `cross_traj_drift_analysis.py`) can be extended without disturbing the paper.
- **README and ONBOARDING polish.** If you find unclear sentences, fix them.
- **Tests.** `tests/` has pytest coverage for the metrics; if you add a feature, add a test.

---

## What would be most useful

In rough order of value to Paper 2:

1. **Sketch the four ChronoStack installation routes.** Each route is one design document under `paper2_chronostack/routes/`. Suggested filenames: `01_loss_extension.md`, `02_tool_interface.md`, `03_scaffolding.md`, `04_architectural_primitive.md`. Each should describe the construction, the expected $\varepsilon$ reduction on each ChronoBench axis, the cost (compute + complexity), and the risks. The A.1 SFT-based loss extension is the simplest example of route 1.
2. **Extend A.1.** The 7B variant did not cross $\varepsilon^*$. Try (a) higher LoRA rank (32 or 64), (b) more training data (1{,}000 or 2{,}000 pairs), (c) DPO with a wall-clock reward signal, or (d) a richer noise model on the self-duration targets. Each variation is a single small experiment; document in `paper2_chronostack/toy_a1/experiments.md`. Server access required.
3. **Within-trajectory dynamics on existing data.** Single-step ChronoBench cannot measure P8/P9 directly. The cross-trajectory proxy is in `scripts/cross_traj_drift_analysis.py` and reported as an honest negative in Paper 1 §6. If you build a multi-step harness for SWE-Bench Lite or any agentic loop, that's the cleanest way to measure within-trajectory drift. Document in `paper3/within_trajectory_design.md` if you start.
4. **Spatial axis pilot design.** The Cartographic Problem and the Agentic Frontier are the Paper 3 thesis. The first concrete experiment is E6 (Spatial-CAR on SWE-Bench Lite). Don't run it (cost), but if you want to design the prompts and the SAR metric implementation, write a draft in `paper3/E6_design.md`.

---

## What requires Justin's approval before doing

- Any spend over $20 on API.
- Any new commitment on behalf of the project (talks, submission to venues, co-author add).
- Any commit to `main` that rewrites a section of Paper 1.
- Any change to `FRAMING.md`.
- Force-push or history-rewrite.
- Sharing the repo with anyone outside the existing collaborator set.

---

## How to reach me (Justin)

I'm not checking email or Slack during the handoff window. If something is on fire — a major paper error discovered, a server issue, an arXiv embargo question — leave a clear message on USC email `aojieyua@usc.edu` with subject `[chronoception URGENT]` and I'll see it when I check on the way back. For non-urgent items, just commit your work and I'll integrate.

If you really need a human, contact **Yue Zhao** (`yzhao@usc.edu`). He has the high-level context.

---

## Repo etiquette

- Branch from `main` for any non-trivial work: `git checkout -b your-name/topic`.
- Commit messages: descriptive subject + body if non-trivial.
- Push frequently so nothing is lost on your laptop alone.
- Don't commit secrets. `.env` is gitignored; verify with `git check-ignore -v .env` before you push anything that touches credentials.
- If you train models, save checkpoints under `/data/haiyuez/...` on the lab server, not in this git repo.

---

## A short list of "if you only do one thing"

If you have 30 minutes: **read `ONBOARDING.md` end to end and skim Paper 1**.

If you have 2 hours: read `FRAMING.md` v2.5 and Paper 1 §1, §3, §6, §9, §12. That covers the framework, both theorems, the centrepiece L3 section, the deployment bridge, and the future-work spatiotemporal sketch.

If you have a day: do the above plus run the figure regeneration scripts under `scripts/make_*_figure.py` to confirm the build is clean on your machine, and write one ChronoStack route design (task #1 in §3 above).

Thanks for keeping the project moving. See you on the other side.
