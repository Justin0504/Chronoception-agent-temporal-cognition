#!/usr/bin/env python3
"""E12 analysis: what forcing an estimate does to the refusal rate, and to rho.

The question the paper needs answered: rho for the high-refusal agents is
computed on the subsample that chose to answer. Is that selection benign?

Two things to read off:

  refusal rate by arm   does removing "I cannot tell" as an option actually
                        move compliance, or is the refusal insensitive to the
                        instruction?
  rho by arm            if the trajectories recovered by forcing carry a rho
                        like the ones we already had, the selection is benign
                        and the reported figure stands. If they carry a
                        different rho, the difference IS the bias, and its
                        direction tells us which way our reported |rho| errs.

    python3 scripts/analyze_e12.py
"""
from __future__ import annotations

import glob
import json
import re
from collections import defaultdict
from math import log10
from statistics import median

import numpy as np

# Broad: a stated duration anywhere in the reply, including sub-second phrasings
# the scoring parser drops. E12 exists to see what the strict parser misses.
DUR = re.compile(
    r"(?:took|takes|spent|elapsed|about|approximately|roughly|around|~|under|less than|in)"
    r"[^.\n]{0,40}?"
    r"(\d+(?:\.\d+)?)\s*"
    r"(millisecond|ms|second|sec\b|s\b|minute|min)", re.I)
UNIT = {"millisecond": 1e-3, "ms": 1e-3, "second": 1, "sec": 1, "s": 1,
        "minute": 60, "min": 60}
REFUSAL = re.compile(
    r"\b(?:unable to|cannot|can't|can not|don't have|do not have|no (?:way|access|ability)|"
    r"not able to|I have no)\b[^.\n]{0,60}"
    r"(?:measure|track|access|know|tell|perceive|determine|report|sense|internal clock|"
    r"sense of time|timing information|real[- ]time|wall[- ]clock|how long|elapsed)", re.I)


def tau_self(text: str):
    m = DUR.search(text or "")
    if not m:
        return None
    v = float(m.group(1)) * UNIT.get(m.group(2).lower().rstrip("."), 1)
    return v if v > 0 else 0.0     # 0.0 is a real answer, distinct from None


def boot_ci(v, B=4000):
    if len(v) < 3:
        return (float("nan"), float("nan"))
    r = np.random.default_rng(0); a = np.array(v)
    bs = [np.median(r.choice(a, len(a), replace=True)) for _ in range(B)]
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


rows = defaultdict(list)
for fp in glob.glob("e12-results/*/*.json"):
    d = json.load(open(fp))
    md = d["metadata"]
    text = d["steps"][-1]["action"]
    rows[(d["agent_id"], md["arm"])].append({
        "tau_wall": float(d["tau_wall"]),
        "text": text,
        "refused": bool(REFUSAL.search(text)),
        "ts": tau_self(text),
    })

agents = sorted({k[0] for k in rows})
ARMS = ["panel", "forced", "forced_ci"]

for agent in agents:
    print(f"\n=== {agent} ===")
    print(f"  {'arm':<11} {'n':>4} {'refused':>9} {'zero-report':>12} {'parsed':>7} "
          f"{'median rho':>11}  {'95% CI':>18}")
    base = None
    for arm in ARMS:
        v = rows.get((agent, arm), [])
        if not v:
            continue
        n = len(v)
        ref = sum(x["refused"] for x in v)
        zero = sum(x["ts"] == 0.0 for x in v)
        rhos = [log10(x["ts"] / x["tau_wall"]) for x in v
                if x["ts"] and x["ts"] > 0 and x["tau_wall"] > 0]
        med = median(rhos) if rhos else float("nan")
        lo, hi = boot_ci(rhos)
        if arm == "panel":
            base = med
        print(f"  {arm:<11} {n:4d} {ref/n*100:8.1f}% {zero/n*100:11.1f}% {len(rhos):7d} "
              f"{med:+11.3f}  [{lo:+.3f}, {hi:+.3f}]")
    if base == base:
        for arm in ARMS[1:]:
            v = rows.get((agent, arm), [])
            rhos = [log10(x["ts"] / x["tau_wall"]) for x in v
                    if x["ts"] and x["ts"] > 0 and x["tau_wall"] > 0]
            if rhos:
                print(f"  {'shift vs panel':<11} {arm:>16}: {median(rhos)-base:+.3f}")

print("\nReading: if forcing moves the refusal rate but leaves rho where it was,")
print("the selection in the reported panel is benign. If rho moves, that shift is")
print("the bias the panel figure carries, and its sign says which way.")
