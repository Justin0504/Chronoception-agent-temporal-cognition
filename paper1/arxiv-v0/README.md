# arXiv v0 — LaTeX source

**Status**: skeleton (2026-06-01). §1 Introduction is fully drafted prose; §2–§12 and appendices are placeholders.

**Target submission**: arXiv preprint, W3 deadline 2026-06-19.

## Build

```bash
cd paper1/arxiv-v0
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Layout

```
arxiv-v0/
├── main.tex                  — document root; \input{} each section
├── README.md                 — this file
├── sections/
│   ├── 01_intro.tex          ✓ drafted
│   ├── 02_three_times.tex    ☐ placeholder
│   ├── 03_augustine_problem.tex ☐ placeholder
│   ├── 04_chronobench.tex    ☐ placeholder
│   ├── 05_l2.tex             ☐ placeholder (L2 primary result)
│   ├── 06_l3.tex             ☐ placeholder (L3 + cross-vendor table)
│   ├── 07_injection_tell.tex ☐ placeholder (+ Injection Atlas table)
│   ├── 08_epsilon.tex        ☐ placeholder
│   ├── 09_agentic_timeline.tex ☐ placeholder (best-paper hook)
│   ├── 10_related_work.tex   ☐ placeholder
│   ├── 11_limitations.tex    ☐ placeholder
│   ├── 12_conclusion.tex     ☐ placeholder
│   ├── A_annotation_protocol.tex ☐ placeholder
│   ├── B_full_panel_tables.tex   ☐ placeholder
│   └── C_atlas_evidence.tex      ☐ placeholder
├── figures/                  — Figure assets
└── bib/
    └── refs.bib              — bibliography stub
```

## Notation

The document imports `../../notation.tex` which provides:
`\twall, \tstep, \tself, \parkinson, \CAR, \confab, \cce, \ccestar, ...`

These mirror `FRAMING.md` §11 and stay consistent across the paper, position note, and slides.

## Pending tasks before submission

- [ ] Draft §2–§12 from FRAMING.md and paper1/* derivatives
- [ ] Insert 7 figures (Three Times diagram, CAR curves, ρ histograms, Injection Tell bar chart, Injection Atlas distribution, ε ranking, Agentic Timeline)
- [ ] Confirm author order + acknowledgements with Yue Zhao
- [ ] Choose arXiv categories (cs.AI primary, cs.CL secondary, cs.LG tertiary)
