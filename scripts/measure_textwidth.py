#!/usr/bin/env python3
"""Measure \textwidth from a built PDF, so chronofig.TEXTWIDTH_IN is never a guess.

Groups words into lines by baseline and takes the mode of the justified left
and right edges; justified body lines all terminate at exactly \textwidth.
Figure-internal text does not share those edges and falls out of the mode.

    python3 scripts/measure_textwidth.py paper1/iclr27/main.pdf
"""
import re, subprocess, sys
from collections import Counter, defaultdict

for f in sys.argv[1:] or ["paper1/iclr27/main.pdf", "paper1/arxiv-v0/main.pdf"]:
    out = subprocess.run(["pdftotext", "-bbox", "-f", "2", "-l", "8", f, "-"],
                         capture_output=True, text=True).stdout
    rows = defaultdict(list)
    for m in re.finditer(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)"', out):
        x0, y0, x1 = map(float, m.groups())
        rows[round(y0, 1)].append((x0, x1))
    body = [v for v in rows.values() if len(v) > 4]
    if not body:
        print(f"{f}: no body lines found"); continue
    left = Counter(round(min(a for a, _ in v)) for v in body).most_common(1)[0][0]
    right = Counter(round(max(b for _, b in v)) for v in body).most_common(1)[0][0]
    print(f"{f:26s} textwidth = {right-left} pt = {(right-left)/72:.2f} in")
