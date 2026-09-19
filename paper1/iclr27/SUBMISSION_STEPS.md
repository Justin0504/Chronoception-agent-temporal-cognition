# ICLR 2027 Submission — Final Steps

**Deadlines (verified against iclr.cc 2026-09-18):** abstract **2026-09-18 23:59 AoE**
· full paper **2026-09-25 23:59 AoE**. AoE is UTC-12, so in US Pacific the abstract
is due **2026-09-19 ~04:59 PDT** — i.e. overnight tonight. An earlier revision of
this file said 09-19 / 09-24; both were a day off.
**Venue:** ICLR 2027 main conference track (ICLR has no position-paper track;
this goes to the primary track). OpenReview.

---

## Pre-flight status (verified 2026-09-18)

| Check | Status |
|---|---|
| Main text length | **8 pages** (limit 9) |
| Anonymization — real names / institution / email | 0 hits in `.tex`, `.bib`, and the built PDF |
| Anonymization — URLs of any kind | **none in the ICLR tree** (so no GitHub or OSF link to leak) |
| PDF metadata `Author` / `Creator` / `Producer` / `Title` | all absent |
| Broken `\ref` / `\cite` | none in any of the three documents |
| Overfull boxes > 100 pt | none |
| `\iclrfinalcopy` | commented out (anonymous mode) |
| Supplementary compiles | yes, 12 pages |
| Figures | 7, all regenerated from the trajectories after the epsilon correction |

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
   - Abstract: paste `ABSTRACT_PLAINTEXT.txt` (Unicode symbols, already
     de-LaTeXed; OpenReview renders it correctly and it stays readable in
     listing views). Do **not** paste the raw `abstract` environment — it is
     full of `\cce`-style macros that will not resolve.
   - TL;DR (if the form offers the field): *LLM agents cannot perceive
     wall-clock time; we prove no token-only training loss can install that
     perception, and measure what it costs across 14 agents from 7 vendors.*
   - Keywords: `LLM agents`, `temporal reasoning`, `agent evaluation`,
     `benchmark`, `impossibility result`
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

5. **arXiv is allowed; the link is not.** ICLR 2027's guidelines state that
   having papers on arXiv is permitted under the dual-submission policy, and
   that *"related arxiv papers by the same authors do not break anonymity; if
   cited, these should be cited in third person."* So posting the preprint
   during review is fine. What is not fine is pointing reviewers at it: the
   preprint carries real names, so linking it is self-deanonymization. The
   ICLR tree currently contains no URLs at all, which is the safe state —
   keep it that way.

6. **The abstract stays editable.** OpenReview allows edits to the registered
   abstract up to the full-paper deadline, so tonight's registration does not
   have to be final. Registering is the irreversible part; the text is not.

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
