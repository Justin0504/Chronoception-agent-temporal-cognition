# arXiv v0 — LaTeX source

**Status**: full first draft (2026-06-01). §1–§12 and appendices A/B/C are drafted prose; figure assets and final author/affiliation TBD.

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
│   ├── 02_three_times.tex    ✓ drafted (Definition 1, implicit identity)
│   ├── 03_augustine_problem.tex ✓ drafted (Definition 2, CIT Theorem 1)
│   ├── 04_chronobench.tex    ✓ drafted (panel + benchmark spec)
│   ├── 05_l2.tex             ✓ drafted (CAR table + P11 anchor)
│   ├── 06_l3.tex             ✓ drafted (rho table + reasoning heterogeneity)
│   ├── 07_injection_tell.tex ✓ drafted (T1.1 + Injection Atlas tables)
│   ├── 08_epsilon.tex        ✓ drafted (eps decomp + Sonnet 4.6 breakdown)
│   ├── 09_agentic_timeline.tex ✓ drafted (Hyp 1, P12, field implications)
│   ├── 10_related_work.tex   ✓ drafted (concurrent work positioning)
│   ├── 11_limitations.tex    ✓ drafted (panel size, parser, settings B)
│   ├── 12_conclusion.tex     ✓ drafted
│   ├── A_annotation_protocol.tex ✓ drafted (T1.1 parser, selfparser, env pins)
│   ├── B_full_panel_tables.tex   ✓ drafted (consolidated panel + 5-gen)
│   └── C_atlas_evidence.tex      ✓ drafted (verbatim leaked prompts)
├── figures/                  — Figure assets
└── bib/
    └── refs.bib              — bibliography stub
```

## Notation

The document imports `../../notation.tex` which provides:
`\twall, \tstep, \tself, \parkinson, \CAR, \confab, \cce, \ccestar, ...`

These mirror `FRAMING.md` §11 and stay consistent across the paper, position note, and slides.

## Pending tasks before submission

- [x] Draft §2–§12 from FRAMING.md and paper1/* derivatives
- [x] Draft appendices A/B/C
- [ ] Insert 7 figures (Three Times diagram, CAR curves, ρ histograms, Injection Tell bar chart, Injection Atlas distribution, ε ranking, Agentic Timeline)
- [ ] Confirm author order + acknowledgements with Yue Zhao
- [ ] Choose arXiv categories (cs.AI primary, cs.CL secondary, cs.LG tertiary)
- [ ] Full LaTeX build + proofread pass
- [ ] Expand bib/refs.bib stubs to full entries (agentbench, swebench, webarena, gaia, inverse-scaling)
