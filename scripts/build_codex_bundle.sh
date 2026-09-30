#!/usr/bin/env bash
# Rebuild the conceptual-figure handoff zip.
#
# The brief inside it goes stale silently -- nothing rebuilds it, so nothing
# fails. It has already drifted once, still describing the paper's framing from
# before the repositioning. Re-run this whenever the paper changes, and re-read
# README.md in the output against the current sections.
set -euo pipefail
PKG=$(mktemp -d); trap 'rm -rf "$PKG"' EXIT

cp paper1/CODEX_FIGURE_BRIEF.md "$PKG/README.md"
cp scripts/chronofig.py scripts/make_style_proof.py "$PKG/"
cp paper1/figures-style/style_proof.png "$PKG/"
cp paper1/arxiv-v0/main.pdf "$PKG/paper_current.pdf"
mkdir -p "$PKG/existing_figures" "$PKG/logos" "$PKG/prose"
cp paper1/arxiv-v0/figures/*.pdf "$PKG/existing_figures/"
cp paper1/arxiv-v0/figures/logos/*.png "$PKG/logos/"
for s in 01_intro 02_three_times 05_l2 06_l3 07_injection_tell 09_agentic_timeline; do
  cp "paper1/arxiv-v0/sections/$s.tex" "$PKG/prose/"
done

cat > "$PKG/HOW_TO_USE.txt" <<'TXT'
Read README.md first -- it is the brief.

  chronofig.py        the style module you must match. Its docstring carries
                      the reasoning behind each constraint.
  make_style_proof.py run it to render palette, type scale and the Three Times
                      glyphs at true print size (needs chronofig.py alongside).
  style_proof.png     that render, if you would rather just look.
  paper_current.pdf   the preprint as it stands.
  existing_figures/   the figures already in the paper. Six are data plots and
                      not in scope; two are schematics you may replace.
                      README section 2 says which is which.
  logos/              vendor marks, already colour-matched. Reuse, don't redraw.
  prose/              the sections a new figure would sit beside.

Hand back: one file per figure, PDF preferred, a regenerating .py better still.
Say which section each belongs in and the one-sentence claim it makes.
TXT

( cd "$PKG" && zip -qr /tmp/codex_figures.zip . -x '.*' '__MACOSX*' )
cp /tmp/codex_figures.zip paper1/codex_figures.zip

# the bundle has to stand on its own -- verify the style module runs unpacked
V=$(mktemp -d); ( cd "$V" && unzip -q paper1/codex_figures.zip 2>/dev/null || unzip -q /tmp/codex_figures.zip )
( cd "$V" && mkdir -p paper1/figures-style scripts && cp chronofig.py scripts/ \
  && python3 make_style_proof.py >/dev/null 2>&1 ) \
  || { echo "FAIL: chronofig.py does not run from the unpacked bundle"; rm -rf "$V"; exit 1; }
rm -rf "$V"
echo "==> paper1/codex_figures.zip  ($(du -h paper1/codex_figures.zip | cut -f1)), style module verified standalone"
