# ICLR 2027 Submission — Final Steps

**Deadlines:** abstract **2026-09-19** · full paper **2026-09-24** (both 11:59pm AoE)
**Venue:** ICLR 2027 main conference track (ICLR has no position-paper track;
this goes to the primary track). OpenReview.

---

## Pre-flight status (verified 2026-09-17)

| Check | Status |
|---|---|
| Main text length | **8.1 pages** (limit 9) |
| Anonymization — main PDF | clean (0 identifying hits) |
| Anonymization — supplementary PDF | clean (0 identifying hits) |
| PDF metadata `Author` field | absent |
| Broken `\ref` / `\cite` | none |
| `\iclrfinalcopy` | commented out (anonymous mode) |
| Supplementary compiles | yes, 11 pages |
| Figure PDFs bundled | 8 |

**Known deanonymization risk that was fixed:** `refs.bib` originally listed the
OSF pre-registration as `author = {Yuan, Aojie and Zhao, Yue}`, and the
Falsification paragraph cites it. The bibliography would have printed the real
author names — a desk-reject under ICLR's policy that *"any paper where author
identity is revealed in either the main text or the supplementary material will
be desk rejected."* The ICLR copy of `refs.bib` now uses
`author = {{Anonymous Authors}}` with a note that the link is supplied in the
camera-ready. **The arXiv copy (`paper1/arxiv-v0/bib/refs.bib`) still carries
the real names — do not sync the two bib files.**

---

## Submission steps

1. **Register the abstract by 09-19.** Title, abstract text, keywords, primary
   area. Abstract registration is a hard prerequisite for the full submission —
   missing it forfeits the full-paper slot.
   - Title: `The Augustine Problem in Agents: Chronoception Must Be Installed`
   - Abstract: copy from `main.tex` (the `abstract` environment)
   - Suggested primary area: *alignment, fairness, safety, privacy, and societal
     considerations* or *datasets and benchmarks* — pick whichever ICLR 2027
     offers that best matches; the alignment area is the better fit for the
     position framing.

2. **Upload the main PDF** — `iclr27/main.pdf` (rename to something neutral;
   do not upload a file named after yourself).

3. **Upload supplementary** — `iclr27_supp/supp.pdf` plus, optionally, the
   source zip. Supplementary is also double-blind: it has been swept.

4. **Fill the reproducibility form** using `REPRODUCIBILITY_CHECKLIST.md`.
   One caveat: the checklist file mentions the GitHub URL and the author name
   in its own body. **Do not paste those fields verbatim into the OpenReview
   form.** Where it asks about code release, say the artifacts are released and
   the URL will be supplied in the camera-ready.

5. **Do not** link the arXiv preprint from the submission. ICLR allows
   concurrent arXiv posting, but do not point reviewers at it — the preprint is
   non-anonymous and doing so is self-deanonymization.

---

## Post-submission

- Reviews expected ~November–December 2026.
- If rejected: the natural next venue is the **ICML 2027 Position Paper Track**
  (deadline **2027-01-22**, abstract 01-16). ICML runs a dedicated position
  track with its own reviewer pool — a materially better fit than ICLR's
  primary track, where this paper competes against method papers. 2024 stats:
  286 submissions / 75 accepted (26%), and this paper sits well above the
  median position paper on empirical density.
- The four-month gap between the ICLR decision and the ICML deadline is enough
  to run the human-baseline panel (`HUMAN_BASELINE_PROTOCOL.md`), which is the
  single largest remaining upgrade.

---

## Do not do

- **Do not fabricate the human baseline.** The paper's strongest differentiator
  is its honesty — the pre-registered F1–F4 falsification suite, the "honest
  negative finding" paragraph where our own data contradicts P8, the E5
  experiment reported as a failure. Synthetic "human subjects" would convert
  that asset into a retraction risk. If the panel is not run, say so: $\epsilon^*$
  is derived from Wittmann (2009) by literature extrapolation, and that is a
  legitimate, disclosable choice.
