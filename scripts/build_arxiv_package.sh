#!/usr/bin/env bash
# Build the arXiv source package and verify it from a clean unpack.
#
# arXiv wants source, not a PDF, and it builds in an empty directory with none
# of this repo around it. Two things broke the first time this was assembled
# and both were silent:
#
#   bib/ was left out, so the build fell back to a stale .bbl -- 30 reference
#   lines instead of 66 and seven unresolved cross-references, with no error.
#   The page count was the only visible symptom (42 against 44).
#
#   `tar --exclude='.*'` excluded everything, because every path in the archive
#   begins with "./". The tarball was 0 files and reported success.
#
# So this script always verifies by unpacking into a fresh directory and
# rebuilding there, and fails if the result differs from the repo build.
set -euo pipefail
SRC="paper1/arxiv-v0"
PKG=$(mktemp -d); OUT=$(mktemp -d); VS=$(mktemp -d); VO=$(mktemp -d)
trap 'rm -rf "$PKG" "$OUT" "$VS" "$VO"' EXIT

echo "==> building in place to refresh main.bbl"
( cd "$SRC" && tectonic -X compile main.tex --keep-intermediates --outdir . >/dev/null 2>&1 )
REPO_PAGES=$(pdftotext "$SRC/main.pdf" - | grep -c $'\f')

echo "==> assembling"
cp "$SRC/main.tex" "$SRC/main.bbl" "$PKG/"
cp -r "$SRC/sections" "$SRC/figures" "$SRC/bib" "$PKG/"
cp notation.tex "$PKG/"                       # lives two levels up in the repo
sed -i.bak 's|\\input{../../notation.tex}|\\input{notation.tex}|' "$PKG/main.tex"
rm -f "$PKG/main.tex.bak"

echo "==> verifying from a clean unpack"
( cd "$PKG" && COPYFILE_DISABLE=1 tar czf "$OUT/arxiv.tar.gz" \
    main.tex main.bbl notation.tex sections figures bib )
tar xzf "$OUT/arxiv.tar.gz" -C "$VS"
( cd "$VS" && tectonic -X compile main.tex --outdir "$VO" >/dev/null 2>&1 )

PAGES=$(pdftotext "$VO/main.pdf" - | grep -c $'\f')
UNRES=$(pdftotext "$VO/main.pdf" - | grep -c '??' || true)
FILES=$(tar tzf "$OUT/arxiv.tar.gz" | grep -vc '/$')

echo "    repo build      : $REPO_PAGES pages"
echo "    package rebuild : $PAGES pages, $UNRES unresolved refs, $FILES files"
[ "$PAGES" = "$REPO_PAGES" ] || { echo "FAIL: page count differs"; exit 1; }
[ "$UNRES" = "0" ] || { echo "FAIL: unresolved cross-references"; exit 1; }
[ "$FILES" -gt 30 ] || { echo "FAIL: package looks empty"; exit 1; }

mkdir -p paper1/arxiv-submit
cp "$OUT/arxiv.tar.gz" paper1/arxiv-submit/chronoception_arxiv.tar.gz
echo "==> wrote paper1/arxiv-submit/chronoception_arxiv.tar.gz"
