# arXiv submission

Package: `chronoception_arxiv.tar.gz` — rebuild with `bash scripts/build_arxiv_package.sh`,
which verifies by unpacking into a fresh directory and refuses to write a package
whose page count or cross-references differ from the repo build.

## Form fields

**Title**
```
Chronoception Must Be Installed: The Augustine Problem in LLM Agents
```

**Authors** — both, in this order; mark equal contribution if the form allows
```
Aojie Yuan    (University of Southern California, aojieyua@usc.edu)
Zijian Su     (University of Michigan, simoon@umich.edu)
```

**Abstract** — paste `paper1/arxiv-v0/ABSTRACT_PLAINTEXT.txt` verbatim.
Do not paste the LaTeX `abstract` environment; it is full of macros that will
not resolve.

**Primary category** `cs.AI`  **Cross-list** `cs.LG`, `cs.CL`

**Comments**
```
44 pages, 8 figures. Position paper. Code, trajectories, and a locked
pre-registration at
https://github.com/Justin0504/Chronoception-agent-temporal-cognition
```

**License** CC BY 4.0 — matches what the paper's own backmatter states.

## Before you click submit

- The submitting author owns the arXiv account; the other author is added by
  email on the form, not by editing the PDF.
- arXiv builds the source itself. It will produce its own PDF; ours is only for
  checking. If its build differs from 44 pages, stop and compare.
- Source is pure ASCII (em dashes and section signs were converted to `---` and
  `\S`) and uses no XeTeX-only packages, so pdflatex should handle it. `tikz`
  was loaded but never used and has been dropped.
- The first announcement is permanent. A v2 is cheap, a retraction is not.
