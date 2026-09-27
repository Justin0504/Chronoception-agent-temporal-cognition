#!/usr/bin/env python3
"""E11 analysis: budget elasticity on the crossed deadline design.

Answers the two questions the T2.3 estimate could not:

  1. Is the elasticity a property of the AGENT or of one task? E11 asks six
     questions at every deadline, so an elasticity is fit per (agent, question)
     and the spread across questions is the answer.

  2. How much of the T2.3 elasticity was compliance with an instruction rather
     than spontaneous expansion? E11 runs each deadline under both a neutral
     framing ("You have B seconds") and T2.3's instructed framing ("Work on
     this for B seconds; do not stop early"). The neutral arm measures
     spontaneous L1; the gap between arms is the instruction effect that the
     T2.3 number was silently carrying.

Also reports the control arm, which gives an unconstrained tau_wall per
question -- the empirical floor that makes alpha computable.

    python3 scripts/analyze_e11.py
"""
from __future__ import annotations

import csv
import glob
import json
from collections import defaultdict
from math import log10
from pathlib import Path
from statistics import median

import numpy as np

OUT = Path("e11-results/e11_elasticity.csv")


def load() -> list[dict]:
    rows = []
    for fp in glob.glob("e11-results/*/*.json"):
        try:
            d = json.load(open(fp))
        except (OSError, json.JSONDecodeError):
            continue
        md = d.get("metadata", {})
        if md.get("experiment") != "E11":
            continue
        rows.append({
            "agent": d["agent_id"],
            "question": md["question_id"],
            "deadline": md["deadline_s"],
            "framing": md["framing"],
            "tau_wall": float(d["tau_wall"]),
            "chars": md.get("response_chars"),
            "tokens": md.get("completion_tokens"),
        })
    return rows


def elasticity(pairs):
    """OLS slope of log10 tau_wall on log10 budget, with a bootstrap CI."""
    if len({b for b, _ in pairs}) < 2:
        return None, None, None
    x = np.array([log10(b) for b, _ in pairs])
    y = np.array([log10(t) for _, t in pairs if t > 0])
    if len(x) != len(y) or len(x) < 4:
        return None, None, None
    e = float(np.polyfit(x, y, 1)[0])
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(2000):
        i = rng.integers(0, len(x), len(x))
        if len(set(x[i].tolist())) < 2:
            continue
        bs.append(np.polyfit(x[i], y[i], 1)[0])
    return e, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main() -> int:
    rows = load()
    if not rows:
        print("no E11 trajectories yet")
        return 1
    agents = sorted({r["agent"] for r in rows})
    print(f"E11: {len(rows)} trajectories across {len(agents)} agents\n")

    out_rows = []
    for agent in agents:
        A = [r for r in rows if r["agent"] == agent]
        ctrl = [r for r in A if r["deadline"] is None]
        print(f"=== {agent}  (n={len(A)}, control n={len(ctrl)}) ===")

        # ---- (2) framing: spontaneous vs instructed ----
        print(f"  {'framing':<12} {'n':>4}  {'e':>7}  {'95% CI':>18}")
        by_framing = {}
        for fr in ("neutral", "instructed"):
            pairs = [(r["deadline"], r["tau_wall"]) for r in A
                     if r["framing"] == fr and r["deadline"]]
            e, lo, hi = elasticity(pairs)
            by_framing[fr] = e
            if e is None:
                continue
            print(f"  {fr:<12} {len(pairs):4d}  {e:+7.3f}  [{lo:+.3f}, {hi:+.3f}]")
        if by_framing.get("neutral") is not None and by_framing.get("instructed") is not None:
            gap = by_framing["instructed"] - by_framing["neutral"]
            print(f"  {'instruction effect':<12} {gap:+.3f}"
                  f"   (T2.3 used the instructed wording)")

        # ---- (1) per-question spread ----
        print(f"\n  {'question':<16} {'e (neutral)':>12}  {'ctrl tau_wall':>13}")
        qes = []
        for q in sorted({r["question"] for r in A}):
            pairs = [(r["deadline"], r["tau_wall"]) for r in A
                     if r["question"] == q and r["framing"] == "neutral" and r["deadline"]]
            e, lo, hi = elasticity(pairs)
            c = [r["tau_wall"] for r in ctrl if r["question"] == q]
            tmin = median(c) if c else float("nan")
            if e is not None:
                qes.append(e)
                print(f"  {q:<16} {e:+12.3f}  {tmin:12.1f}s")
            out_rows.append({"agent": agent, "question": q,
                             "e_neutral": None if e is None else round(e, 4),
                             "tau_min_control_s": round(tmin, 2) if c else None,
                             "n_control": len(c)})
        if qes:
            print(f"  {'across questions':<16} median {median(qes):+.3f},"
                  f" range [{min(qes):+.3f}, {max(qes):+.3f}]")
        print()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        wr.writeheader()
        wr.writerows(out_rows)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
