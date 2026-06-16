#!/usr/bin/env python3
"""Analyzer for the ChronoStack tool-interface (get_current_time) MVP.

For each (model, condition) it reports:
- tool-use rates: fraction of trajectories that called the clock at all, and the
  fraction that called it >= 2 times (the minimum to measure a duration);
- the confabulation error |rho| = |log10(tau_self / tau_wall)|;
- for the tool conditions, |rho| split by whether the agent called the clock
  >= 2 times -- the test of "availability != use".

The story it is built to surface: a tool gives the agent ACCESS to wall-clock
time, but if it does not spontaneously call it (twice) it stays as ungrounded as
the no-tool baseline; when it does use it correctly, |rho| should collapse.

Usage
-----
    python scripts/analyze_tool_interface.py --input-dir tool-interface-results
    python scripts/analyze_tool_interface.py --input-dir tool-interface-results \
        --output-csv tool-interface-results/summary.csv
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

CONDITION_ORDER = ("no_tool", "tool", "tool_prompted")


def _rho(rec: dict[str, Any]) -> float | None:
    ts = rec.get("tau_self")
    tw = rec.get("tau_wall")
    if not isinstance(ts, (int, float)) or ts <= 0:
        return None
    if not isinstance(tw, (int, float)) or tw <= 0:
        return None
    return math.log10(ts / tw)


def _median(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def _load(input_dir: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for model_dir in sorted(p for p in input_dir.iterdir() if p.is_dir()):
        for cond_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
            files = sorted((cond_dir / "T3.1").glob("*.json"))
            if not files:
                continue
            recs = [json.loads(f.read_text(encoding="utf-8")) for f in files]
            out.setdefault(model_dir.name, {})[cond_dir.name] = recs
    return out


def _summary(recs: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(recs)
    calls = [r.get("n_tool_calls", 0) or 0 for r in recs]
    used_1 = sum(1 for c in calls if c >= 1)
    used_2 = sum(1 for c in calls if c >= 2)
    abs_rhos = [abs(r) for r in (_rho(x) for x in recs) if r is not None]
    rhos = [r for r in (_rho(x) for x in recs) if r is not None]
    # |rho| split by correct-use (>= 2 calls).
    abs_used2 = [abs(r) for x in recs if (x.get("n_tool_calls", 0) or 0) >= 2 and (r := _rho(x)) is not None]
    abs_not2 = [abs(r) for x in recs if (x.get("n_tool_calls", 0) or 0) < 2 and (r := _rho(x)) is not None]
    return {
        "n": n,
        "frac_used_1plus": used_1 / n if n else None,
        "frac_used_2plus": used_2 / n if n else None,
        "median_calls": _median([float(c) for c in calls]),
        "median_abs_rho": _median(abs_rhos),
        "median_rho": _median(rhos),
        "n_rho": len(rhos),
        "median_abs_rho_used2plus": _median(abs_used2),
        "n_used2plus": len(abs_used2),
        "median_abs_rho_under2": _median(abs_not2),
        "n_under2": len(abs_not2),
    }


def analyze(input_dir: Path) -> dict[str, Any]:
    data = _load(input_dir)
    per_model: dict[str, Any] = {}
    for model, conds in data.items():
        summaries = {c: _summary(conds[c]) for c in CONDITION_ORDER if c in conds}
        # Diagnosis: is the bottleneck "availability != use"?
        diagnosis = None
        tool = summaries.get("tool")
        if tool is not None:
            low_spontaneous_use = (tool["frac_used_2plus"] or 0) < 0.5
            grounds_when_used = (
                tool["median_abs_rho_used2plus"] is not None
                and tool["median_abs_rho_used2plus"] < 0.3
            )
            if low_spontaneous_use and grounds_when_used:
                diagnosis = ("AVAILABILITY != USE: the tool grounds the report when called >=2x, "
                             "but the agent rarely calls it that way on its own.")
            elif not low_spontaneous_use and grounds_when_used:
                diagnosis = "TOOL SUFFICES: the agent spontaneously calls it correctly and |rho| collapses."
            elif tool["median_abs_rho_used2plus"] is not None and tool["median_abs_rho_used2plus"] >= 0.3:
                diagnosis = "USE INSUFFICIENT: even >=2 calls do not ground the report."
        per_model[model] = {"summaries": summaries, "diagnosis": diagnosis}
    return {"per_model": per_model}


def _print_report(result: dict[str, Any]) -> None:
    print("=" * 74)
    print("ChronoStack tool-interface (get_current_time) — T3.1 confabulation")
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
            print(f"  {cond:<14} n={s['n']:>3}  used>=1={fmt(s['frac_used_1plus'],2)}  "
                  f"used>=2={fmt(s['frac_used_2plus'],2)}  median|rho|={fmt(s['median_abs_rho'])}")
            if cond in ("tool", "tool_prompted"):
                print(f"  {'':14}   |rho| when used>=2: {fmt(s['median_abs_rho_used2plus'])} "
                      f"(n={s['n_used2plus']})  |  when <2: {fmt(s['median_abs_rho_under2'])} "
                      f"(n={s['n_under2']})")
        if m["diagnosis"]:
            print(f"  DIAGNOSIS: {m['diagnosis']}")
        print()
    print("=" * 74)


def _write_csv(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "condition", "n", "frac_used_1plus", "frac_used_2plus",
                    "median_abs_rho", "median_abs_rho_used2plus", "median_abs_rho_under2"])
        for model, m in result["per_model"].items():
            for cond in CONDITION_ORDER:
                s = m["summaries"].get(cond)
                if s is None:
                    continue
                w.writerow([model, cond, s["n"], s["frac_used_1plus"], s["frac_used_2plus"],
                            s["median_abs_rho"], s["median_abs_rho_used2plus"], s["median_abs_rho_under2"]])


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Analyze the tool-interface get_current_time MVP.")
    p.add_argument("--input-dir", default="tool-interface-results")
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
