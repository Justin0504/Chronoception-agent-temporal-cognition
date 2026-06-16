#!/usr/bin/env python3
"""Analyzer for the ChronoStack scaffolding budget-honoring loop.

Compares CAR (Clock-Adherence Ratio = wall-at-stop / budget) between the
scaffold-off baseline and the scaffold-on condition. The scaffolding route
"works" if the live wall-clock readout moves CAR toward 1 (the agent honors the
budget instead of stopping early, the L2 failure Paper 1 documented).

Per agent it reports, for each condition: median CAR, median |CAR - 1| (distance
from the ideal), median steps, and the fraction of voluntary 'DONE' stops. It
then compares the two conditions with a Mann-Whitney U test (normal
approximation, tie-corrected, standard library only) and gives a verdict.

Verdict (per agent):
- SCAFFOLD HELPS : median |CAR-1| is smaller with the scaffold AND the CAR
                   distributions differ at p < alpha.
- SCAFFOLD HURTS : median |CAR-1| is larger with the scaffold AND p < alpha.
- NO EFFECT      : difference not significant (this is the L2-style null --
                   even live scaffolding does not install budget-honoring).

Usage
-----
    python scripts/analyze_scaffolding.py --input-dir scaffolding-results
    python scripts/analyze_scaffolding.py --input-dir scaffolding-results \
        --output-csv scaffolding-results/car.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

DEFAULT_ALPHA = 0.05


def _rankdata(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _mann_whitney_p(a: list[float], b: list[float]) -> float | None:
    """Two-sided Mann-Whitney U p-value via tie-corrected normal approximation.

    Returns None if either group is empty. Adequate for n>=~8 per group; for
    tiny n it is approximate and the medians should be read alongside it.
    """
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return None
    combined = a + b
    ranks = _rankdata(combined)
    r1 = sum(ranks[:n1])
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    n = n1 + n2
    # Tie correction for the variance.
    counts: dict[float, int] = {}
    for v in combined:
        counts[v] = counts.get(v, 0) + 1
    tie_term = sum(t**3 - t for t in counts.values())
    var = (n1 * n2 / 12.0) * ((n + 1) - tie_term / (n * (n - 1))) if n > 1 else 0.0
    if var <= 0:
        return 1.0
    z = (u1 - mu) / math.sqrt(var)
    # Two-sided p via the normal CDF (math.erf).
    p = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))
    return min(1.0, max(0.0, p))


def _load(input_dir: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Return {agent: {condition: [record, ...]}}."""
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for agent_dir in sorted(p for p in input_dir.iterdir() if p.is_dir()):
        for cond_dir in sorted(p for p in agent_dir.iterdir() if p.is_dir()):
            files = sorted(cond_dir.glob("*.json"))
            if not files:
                continue
            recs = [json.loads(f.read_text(encoding="utf-8")) for f in files]
            out.setdefault(agent_dir.name, {})[cond_dir.name] = recs
    return out


def _summary(recs: list[dict[str, Any]]) -> dict[str, Any]:
    cars = [r["car"] for r in recs if isinstance(r.get("car"), (int, float))]
    steps = [r["n_steps"] for r in recs if isinstance(r.get("n_steps"), int)]
    voluntary = sum(1 for r in recs if r.get("stop_reason") == "voluntary_done")
    # Exploratory (not pre-registered) dispersion stats: the live clock can
    # tighten adherence and curb overruns without moving the median CAR.
    overruns = sum(1 for c in cars if c > 1.0)
    return {
        "n": len(recs),
        "median_car": statistics.median(cars) if cars else None,
        "median_abs_car_dev": statistics.median([abs(c - 1.0) for c in cars]) if cars else None,
        "car_stdev": statistics.pstdev(cars) if len(cars) > 1 else None,
        "car_min": min(cars) if cars else None,
        "car_max": max(cars) if cars else None,
        "frac_overrun": overruns / len(cars) if cars else None,
        "median_steps": statistics.median(steps) if steps else None,
        "frac_voluntary_done": voluntary / len(recs) if recs else None,
        "_cars": cars,
    }


def analyze(input_dir: Path, alpha: float) -> dict[str, Any]:
    data = _load(input_dir)
    per_agent: dict[str, Any] = {}

    for agent, conds in data.items():
        off = _summary(conds["scaffold_off"]) if "scaffold_off" in conds else None
        on = _summary(conds["scaffold_on"]) if "scaffold_on" in conds else None

        comparison: dict[str, Any] = {}
        if off and on and off["_cars"] and on["_cars"]:
            p = _mann_whitney_p(on["_cars"], off["_cars"])
            dev_off = off["median_abs_car_dev"]
            dev_on = on["median_abs_car_dev"]
            significant = p is not None and p < alpha
            if significant and dev_on < dev_off:
                verdict = "SCAFFOLD HELPS"
            elif significant and dev_on > dev_off:
                verdict = "SCAFFOLD HURTS"
            else:
                verdict = "NO EFFECT"
            comparison = {
                "p_value": p,
                "significant": significant,
                "median_car_off": off["median_car"],
                "median_car_on": on["median_car"],
                "median_abs_car_dev_off": dev_off,
                "median_abs_car_dev_on": dev_on,
                "verdict": verdict,
            }
        else:
            comparison = {"verdict": "INSUFFICIENT DATA"}

        # Drop internal arrays before returning.
        for s in (off, on):
            if s is not None:
                s.pop("_cars", None)
        per_agent[agent] = {"scaffold_off": off, "scaffold_on": on, "comparison": comparison}

    return {"alpha": alpha, "per_agent": per_agent}


def _print_report(result: dict[str, Any]) -> None:
    print("=" * 70)
    print("ChronoStack scaffolding — budget-honoring loop (CAR)")
    print("=" * 70)
    print(f"Alpha: {result['alpha']}")
    print()
    if not result["per_agent"]:
        print("(no data)")
        print("=" * 70)
        return
    for agent, a in result["per_agent"].items():
        print(f"Agent: {agent}")
        for cond_key, label in (("scaffold_off", "OFF"), ("scaffold_on", "ON ")):
            s = a[cond_key]
            if s is None:
                print(f"  {label}: (no data)")
                continue
            def fmt(v: Any, nd: int = 3) -> str:
                return f"{v:.{nd}f}" if isinstance(v, (int, float)) else " - "
            print(f"  {label}: n={s['n']}  median CAR={fmt(s['median_car'])}  "
                  f"|CAR-1|={fmt(s['median_abs_car_dev'])}  "
                  f"steps={fmt(s['median_steps'],1)}  voluntary_done={fmt(s['frac_voluntary_done'],2)}")
            print(f"       CAR range=[{fmt(s['car_min'],2)}, {fmt(s['car_max'],2)}]  "
                  f"stdev={fmt(s['car_stdev'])}  overrun(>1)={fmt(s['frac_overrun'],2)}  "
                  f"(exploratory)")
        c = a["comparison"]
        if "p_value" in c:
            print(f"  compare: CAR {fmt(c['median_car_off'])} -> {fmt(c['median_car_on'])} "
                  f"(off->on), Mann-Whitney p={c['p_value']:.3f}")
        print(f"  VERDICT: {c['verdict']}")
        print()
    print("=" * 70)


def _write_csv(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["agent", "condition", "n", "median_car", "median_abs_car_dev",
                    "median_steps", "frac_voluntary_done", "verdict"])
        for agent, a in result["per_agent"].items():
            verdict = a["comparison"].get("verdict", "")
            for cond_key in ("scaffold_off", "scaffold_on"):
                s = a[cond_key]
                if s is None:
                    continue
                w.writerow([agent, cond_key, s["n"], s["median_car"], s["median_abs_car_dev"],
                            s["median_steps"], s["frac_voluntary_done"], verdict])


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Analyze the scaffolding budget-honoring loop.")
    p.add_argument("--input-dir", default="scaffolding-results")
    p.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    p.add_argument("--output-csv", default=None)
    p.add_argument("--output-json", default=None)
    args = p.parse_args(argv)

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"input dir not found: {input_dir}")

    result = analyze(input_dir, args.alpha)
    _print_report(result)

    if args.output_csv:
        _write_csv(result, Path(args.output_csv))
        print(f"\nWrote CSV: {args.output_csv}")
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(f"Wrote JSON: {args.output_json}")


if __name__ == "__main__":
    main()
