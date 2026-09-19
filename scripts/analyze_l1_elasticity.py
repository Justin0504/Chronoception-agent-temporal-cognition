#!/usr/bin/env python3
"""L1 (Agentic Parkinson) measured as a budget elasticity, from the T2.3 corpus.

Why this analysis and not the T1.3 capability
---------------------------------------------
T1.3 was the capability nominally assigned to L1, and it cannot answer the
question. Two independent reasons:

1. Its trajectories carry `budget=None, budget_kind="none"`, so the stated
   deadline lives only inside the prompt string and alpha is not computable.

2. Worse, the ten T1.3 prompts pair each deadline with a different question,
   and the pairing tracks intrinsic task size almost perfectly: 5 s asks for
   the capital of Australia, 180 s asks for a short story. Deadline and task
   size are confounded, so a longer answer at a longer deadline says nothing.
   No reanalysis fixes this; the design would have to be re-run crossed.

T2.3 already has the design L1 needs: one fixed task, budget varied over
B in {60, 300, 900, 1800, 3600} s, n=30 per cell per setting. That is a 60x
range on a single factor with the task held constant.

What is measured
----------------
The budget elasticity

    e := d log10(tau_wall) / d log10(B)

fit per agent by OLS over all (B, tau_wall) pairs, with a bootstrap CI.
Parkinson's law in its strong form ("work expands to fill the time available")
is e = 1. No response to the budget at all is e = 0.

What is NOT a separate result
-----------------------------
CAR = tau_wall / B, so d log CAR / d log B = e - 1 identically. Reporting that
the fitted e "predicts" the CAR ladder would be circular -- it is the same fit
restated. What the comparison does test is whether a single exponent describes
the budget response, i.e. whether log tau_wall is linear in log B; `--check-fit`
reports that residual.

    python3 scripts/analyze_l1_elasticity.py
    python3 scripts/analyze_l1_elasticity.py --check-fit
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
from collections import defaultdict
from math import log10
from pathlib import Path
from statistics import median

import numpy as np

OUT = Path("pilot-results/l1_elasticity.csv")
BUDGETS = [60, 300, 900, 1800, 3600]

PANEL: dict[str, list[str]] = {
    "gpt-4o-mini":   ["pilot-results/openai_gpt-4o-mini/T2.3/{s}/*.json"],
    "gpt-4o":        ["pilot-results/openai_gpt-4o/T2.3/{s}/*.json"],
    "gpt-5.1":       ["pilot-results/openai_gpt-5.1/T2.3/{s}/*.json"],
    "o3":            ["pilot-results/openai_o3/T2.3/{s}/*.json"],
    "o4-mini":       ["e1-results/o4-mini/**/T2.3/{s}/*.json"],
    "Claude Haiku 4.5":  ["pilot-results/anthropic_claude-haiku-4-5/T2.3/{s}/*.json"],
    "Claude Sonnet 4.6": ["pilot-results/anthropic_claude-sonnet-4-6/T2.3/{s}/*.json"],
    "Sonnet 4.6 + thinking": ["e3-results/claude-sonnet-4-6-thinking/**/T2.3/{s}/*.json"],
    "Qwen2.5-7B":    ["pilot-results/oss_qwen2.5-7b-instruct-yuezhao/T2.3/{s}/*.json"],
    "GLM-5.2-FP8":   ["vultr-results/glm-5.2-fp8/**/T2.3/{s}/*.json"],
    "Kimi-K2.6":     ["vultr-results/kimi-k2.6/**/T2.3/{s}/*.json"],
    "MiniMax-M2.7":  ["vultr-results/minimax-m2.7/**/T2.3/{s}/*.json"],
    "Qwen3.6-27B":   ["vultr-results/qwen3.6-27b/**/T2.3/{s}/*.json"],
}


def observations(patterns: list[str]) -> list[tuple[float, float]]:
    """(log10 B, log10 tau_wall) over both settings; injection is orthogonal to L1."""
    out = []
    for setting in ("no_injection", "with_injection"):
        for pat in patterns:
            for fp in glob.glob(pat.format(s=setting), recursive=True):
                try:
                    d = json.load(open(fp))
                except (OSError, json.JSONDecodeError):
                    continue
                b = d.get("budget")
                if d.get("budget_kind") != "wall" or not b or b <= 0:
                    continue
                steps = d.get("steps") or []
                if not steps:
                    continue
                tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
                if tw > 0:
                    out.append((log10(b), log10(tw)))
    return out


def elasticity(obs, n_boot: int = 4000):
    x = np.array([a for a, _ in obs])
    y = np.array([b for _, b in obs])
    e = float(np.polyfit(x, y, 1)[0])
    rng = np.random.default_rng(0)
    boot = []
    for _ in range(n_boot):
        i = rng.integers(0, len(x), len(x))
        if len(set(x[i].tolist())) < 2:
            continue
        boot.append(np.polyfit(x[i], y[i], 1)[0])
    return e, float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-fit", action="store_true",
                    help="report how well a single exponent describes the ladder")
    args = ap.parse_args()

    rows = []
    for name, pats in PANEL.items():
        obs = observations(pats)
        if len(obs) < 20:
            continue
        e, lo, hi = elasticity(obs)
        rows.append({"agent": name, "elasticity": round(e, 4),
                     "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                     "n": len(obs), "excludes_zero": "yes" if lo > 0 or hi < 0 else "no"})

    rows.sort(key=lambda r: -r["elasticity"])
    w = max(len(r["agent"]) for r in rows)
    print("L1 budget elasticity  e = d log10(tau_wall) / d log10(B)")
    print("Parkinson's law in full: e = 1.   No budget response at all: e = 0.\n")
    print(f"{'agent':<{w}}  {'n':>4}  {'e':>7}  {'95% CI':>18}  CI excl. 0")
    for r in rows:
        print(f"{r['agent']:<{w}}  {r['n']:4d}  {r['elasticity']:+7.3f}  "
              f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]  {r['excludes_zero']:>10}")

    med = median(r["elasticity"] for r in rows)
    npos = sum(1 for r in rows if r["ci_lo"] > 0)
    print(f"\npanel median e = {med:.3f};  {npos}/{len(rows)} agents have a CI strictly above 0.")
    print(f"A 60x budget increase therefore buys {60**med:.2f}x more wall-clock, "
          f"where Parkinson's law requires 60x.")

    if args.check_fit:
        print("\n--- is one exponent enough? (log tau_wall linear in log B) ---")
        for name, pats in PANEL.items():
            obs = observations(pats)
            if len(obs) < 20:
                continue
            by = defaultdict(list)
            for lb, lt in obs:
                by[round(10 ** lb)].append(10 ** lt)
            if len(by) < 3:
                continue
            e, _, _ = elasticity(obs, n_boot=200)
            xs = sorted(by)
            fit_ref = median(by[xs[0]])
            errs = []
            for b in xs[1:]:
                pred = fit_ref * (b / xs[0]) ** e
                errs.append(abs(pred - median(by[b])) / median(by[b]))
            print(f"  {name:<{w}}  median |relative error| over the ladder = {median(errs)*100:4.0f}%")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
