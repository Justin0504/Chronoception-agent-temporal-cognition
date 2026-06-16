#!/usr/bin/env python3
"""Analyzer for the harness-bracketed elapsed-time tool experiment (route 2->4).

Reports, per (model, condition), the tool-use rate and the confabulation error
|rho| = |log10(tau_self / tau_wall)|, and compares the naive clock tool against
the harness-bracketed elapsed tool. The route-4 premise is supported if
elapsed_tool collapses |rho| where clock_tool could not -- especially for
reasoning models, whose hidden-reasoning time the visible-stream clock misses.

Usage
-----
    python scripts/analyze_elapsed_tool.py --input-dir elapsed-tool-results
    python scripts/analyze_elapsed_tool.py --input-dir elapsed-tool-results \
        --output-csv elapsed-tool-results/summary.csv
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

CONDITION_ORDER = ("no_tool", "clock_tool", "elapsed_tool")
GROUNDED_THRESHOLD = 0.3  # |rho| below this counts as "grounded"


def _rho(rec: dict[str, Any]) -> float | None:
    ts, tw = rec.get("tau_self"), rec.get("tau_wall")
    if not isinstance(ts, (int, float)) or ts <= 0:
        return None
    if not isinstance(tw, (int, float)) or tw <= 0:
        return None
    return math.log10(ts / tw)


def _median(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def _bootstrap_median_ci(
    xs: list[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float] | None:
    """Percentile bootstrap CI for the median (seeded, stdlib only).

    Returns None for n < 3 (a CI from one or two points is meaningless).
    """
    import random
    if len(xs) < 3:
        return None
    rng = random.Random(seed)
    n = len(xs)
    meds = []
    for _ in range(n_boot):
        sample = [xs[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(sample))
    meds.sort()
    lo = meds[int((alpha / 2) * n_boot)]
    hi = meds[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return (lo, hi)


def _load(input_dir: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for model_dir in sorted(p for p in input_dir.iterdir() if p.is_dir()):
        for cond_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
            files = sorted((cond_dir / "T3.1").glob("*.json"))
            if files:
                out.setdefault(model_dir.name, {})[cond_dir.name] = [
                    json.loads(f.read_text(encoding="utf-8")) for f in files
                ]
    return out


MIN_N_FOR_VERDICT = 5  # below this many parsed durations a cell is uninterpretable


def _summary(recs: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(recs)
    used = sum(1 for r in recs if (r.get("n_tool_calls", 0) or 0) >= 1)
    n_no_report = sum(1 for r in recs if r.get("tau_self") is None)
    abs_rhos = [abs(r) for r in (_rho(x) for x in recs) if r is not None]
    rhos = [r for r in (_rho(x) for x in recs) if r is not None]
    ci = _bootstrap_median_ci(abs_rhos)
    return {
        "n": n,
        "frac_used": used / n if n else None,
        "frac_no_report": n_no_report / n if n else None,  # agent gave no parseable duration
        "median_abs_rho": _median(abs_rhos),
        "median_abs_rho_ci": ci,
        "median_rho": _median(rhos),
        "frac_grounded": (sum(1 for a in abs_rhos if a < GROUNDED_THRESHOLD) / len(abs_rhos))
        if abs_rhos else None,
        "n_rho": len(rhos),
    }


def analyze(input_dir: Path) -> dict[str, Any]:
    data = _load(input_dir)
    per_model: dict[str, Any] = {}
    for model, conds in data.items():
        summaries = {c: _summary(conds[c]) for c in CONDITION_ORDER if c in conds}
        verdict = None
        clock, elapsed = summaries.get("clock_tool"), summaries.get("elapsed_tool")
        if clock and elapsed:
            # Guard: too few parsed durations (e.g. an agent that refuses to
            # report its own time) makes the cell uninterpretable -- don't claim
            # a fix or a null from n<MIN.
            if clock["n_rho"] < MIN_N_FOR_VERDICT or elapsed["n_rho"] < MIN_N_FOR_VERDICT:
                verdict = (
                    f"INCONCLUSIVE: too few parsed durations "
                    f"(clock n={clock['n_rho']}, elapsed n={elapsed['n_rho']}; "
                    f"no-report rate elapsed={elapsed['frac_no_report']:.0%}). "
                    "Likely a self-timing refusal, not a measurement result."
                )
            elif elapsed["median_abs_rho"] < GROUNDED_THRESHOLD and clock["median_abs_rho"] >= GROUNDED_THRESHOLD:
                verdict = ("ELAPSED TOOL FIXES IT: harness-bracketed elapsed grounds the report "
                           "where the naive clock tool did not.")
            elif elapsed["median_abs_rho"] < clock["median_abs_rho"] - 0.1:
                verdict = "ELAPSED TOOL HELPS: |rho| lower than the naive clock tool."
            else:
                verdict = "NO IMPROVEMENT over the naive clock tool."
        per_model[model] = {"summaries": summaries, "verdict": verdict}
    return {"per_model": per_model}


def _print_report(result: dict[str, Any]) -> None:
    print("=" * 74)
    print("Harness-bracketed elapsed-time tool (route 2 -> 4) — T3.1 |rho|")
    print("=" * 74)
    if not result["per_model"]:
        print("(no data)")
        print("=" * 74)
        return
    for model, m in result["per_model"].items():
        print(f"Model: {model}")
        for cond in CONDITION_ORDER:
            s = m["summaries"].get(cond)
            if s is None:
                continue
            def fmt(v: Any, nd: int = 3) -> str:
                return f"{v:.{nd}f}" if isinstance(v, (int, float)) else " - "
            ci = s.get("median_abs_rho_ci")
            ci_str = f" [95% CI {ci[0]:.2f}, {ci[1]:.2f}]" if ci else ""
            print(f"  {cond:<14} n={s['n']:>3}  n_rho={s['n_rho']:>2}  used={fmt(s['frac_used'],2)}  "
                  f"no_report={fmt(s['frac_no_report'],2)}  "
                  f"median|rho|={fmt(s['median_abs_rho'])}{ci_str}  grounded={fmt(s['frac_grounded'],2)}")
        if m["verdict"]:
            print(f"  VERDICT: {m['verdict']}")
        print()
    print("=" * 74)


def _write_csv(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "condition", "n", "frac_used", "median_abs_rho", "frac_grounded"])
        for model, m in result["per_model"].items():
            for cond in CONDITION_ORDER:
                s = m["summaries"].get(cond)
                if s:
                    w.writerow([model, cond, s["n"], s["frac_used"], s["median_abs_rho"], s["frac_grounded"]])


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Analyze the elapsed-time tool experiment.")
    p.add_argument("--input-dir", default="elapsed-tool-results")
    p.add_argument("--output-csv", default=None)
    p.add_argument("--output-json", default=None)
    args = p.parse_args(argv)

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"input dir not found: {input_dir}")

    result = analyze(input_dir)
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
