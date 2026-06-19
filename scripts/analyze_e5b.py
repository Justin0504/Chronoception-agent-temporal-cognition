#!/usr/bin/env python3
"""E5b analyzer — Reverse-Scaling via reasoning-intensity induction.

This is the analyzer for run_e5b_reasoning_induction.sh. It does the one thing
the original E5 analysis could not: it *verifies the manipulation worked* before
it reports a rho trend.

Two things make E5b different from E5
------------------------------------
1. Reasoning compute is measured, not assumed. For each induction level we
   report median completion tokens (the in-band reasoning of an R1-Distill model
   is counted in completion_tokens) and median tau_wall. The Reverse-Scaling
   Theorem (Paper 1 Thm 2) is a statement about |rho| as a function of reasoning
   compute; if compute does not increase across levels, the experiment cannot
   test the theorem, and this analyzer says so instead of reporting a null.

2. tau_self is parsed from the SURFACE answer only. R1-Distill emits its
   chain-of-thought inline, terminated by "</think>", followed by the final
   answer. We split on "</think>" and parse the self-reported duration from the
   answer alone. This matters for the sign of rho: the theorem's mechanism is
   that tau_self anchors to the surface output while tau_wall absorbs the hidden
   thinking, so tau_self must be read from the surface, not the thinking.

Verdict logic (primary setting = no_injection)
----------------------------------------------
- MANIPULATION FAILED  : median completion tokens not monotone increasing across
                         the ordered levels. Cannot test the theorem (the E5 case).
- RS CONFIRMED         : compute increases AND median |rho| is monotone
                         non-decreasing across levels.
- RS REFUTED           : compute increases but median |rho| decreases.

Usage
-----
    python scripts/analyze_e5b.py --input-dir e5b-results
    python scripts/analyze_e5b.py --input-dir e5b-results --output-csv e5b-results/metrics.csv
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

# Repo-root import so the script runs from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chronoception.bench.parsers import extract_tau_self_retrospective  # noqa: E402

# Induction levels in monotone order of intended reasoning intensity.
LEVEL_ORDER = ("brief", "natural", "thorough")
SETTINGS = ("no_injection", "with_injection")
PRIMARY_SETTING = "no_injection"


def _surface_answer(action: str) -> str:
    """Return the final answer, stripping the inline chain-of-thought.

    R1-Distill terminates its reasoning with "</think>"; the answer follows.
    If no marker is present (e.g. a non-reasoning fallback), the whole string
    is the answer.
    """
    marker = "</think>"
    if marker in action:
        return action.split(marker)[-1]
    return action


def _completion_tokens(traj: dict[str, Any]) -> int | None:
    usage = (
        traj.get("metadata", {})
        .get("response_metadata", {})
        .get("usage")
    )
    if isinstance(usage, dict):
        ct = usage.get("completion_tokens")
        if isinstance(ct, (int, float)):
            return int(ct)
    return None


def _reasoning_chars(action: str) -> int:
    """Length of the chain-of-thought (everything up to and including </think>)."""
    marker = "</think>"
    if marker in action:
        return len(action.split(marker)[0])
    return 0


def _load_level(level_dir: Path, setting: str) -> list[dict[str, Any]]:
    """Load all T3.1 trajectory JSONs for one level under one setting."""
    glob = level_dir.glob(f"**/T3.1/{setting}/*.json")
    out: list[dict[str, Any]] = []
    for p in sorted(glob):
        with p.open(encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def _rho_from_surface(traj: dict[str, Any]) -> float | None:
    """log10(tau_self / tau_wall), with tau_self re-parsed from the answer."""
    action = traj["steps"][-1]["action"]
    tau_self = extract_tau_self_retrospective(_surface_answer(action))
    tau_wall = traj.get("tau_wall")
    if tau_self is None or tau_self <= 0:
        return None
    if not isinstance(tau_wall, (int, float)) or tau_wall <= 0:
        return None
    return math.log10(tau_self / tau_wall)


def _median(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def _summarize(trajs: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-(level, setting) summary row."""
    rhos: list[float] = []
    abs_rhos: list[float] = []
    comp_tokens: list[float] = []
    walls: list[float] = []
    reasoning_chars: list[float] = []
    finish_truncated = 0

    for t in trajs:
        rho = _rho_from_surface(t)
        if rho is not None:
            rhos.append(rho)
            abs_rhos.append(abs(rho))
        ct = _completion_tokens(t)
        if ct is not None:
            comp_tokens.append(ct)
        wall = t.get("tau_wall")
        if isinstance(wall, (int, float)) and wall > 0:
            walls.append(wall)
        reasoning_chars.append(_reasoning_chars(t["steps"][-1]["action"]))
        fr = (
            t.get("metadata", {})
            .get("response_metadata", {})
            .get("finish_reason")
        )
        if fr == "length":
            finish_truncated += 1

    return {
        "n_trajectories": len(trajs),
        "n_rho": len(rhos),
        "median_rho": _median(rhos),
        "median_abs_rho": _median(abs_rhos),
        "median_completion_tokens": _median(comp_tokens),
        "median_tau_wall": _median(walls),
        "median_reasoning_chars": _median(reasoning_chars),
        "n_truncated": finish_truncated,
    }


def _is_monotone_increasing(xs: list[float | None]) -> bool:
    vals = [x for x in xs if x is not None]
    if len(vals) < 2:
        return False
    return all(b > a for a, b in zip(vals, vals[1:]))


def _is_monotone_nondecreasing(xs: list[float | None]) -> bool:
    vals = [x for x in xs if x is not None]
    if len(vals) < 2:
        return False
    return all(b >= a for a, b in zip(vals, vals[1:]))


def analyze(input_dir: Path) -> dict[str, Any]:
    by_level: dict[str, dict[str, dict[str, Any]]] = {}
    for level in LEVEL_ORDER:
        level_dir = input_dir / f"deepseek-r1-14b-{level}"
        if not level_dir.exists():
            continue
        by_level[level] = {}
        for setting in SETTINGS:
            trajs = _load_level(level_dir, setting)
            by_level[level][setting] = _summarize(trajs)

    # Verdict on the primary setting.
    levels_present = [lv for lv in LEVEL_ORDER if lv in by_level]
    comp_series = [
        by_level[lv][PRIMARY_SETTING]["median_completion_tokens"]
        for lv in levels_present
    ]
    wall_series = [
        by_level[lv][PRIMARY_SETTING]["median_tau_wall"] for lv in levels_present
    ]
    absrho_series = [
        by_level[lv][PRIMARY_SETTING]["median_abs_rho"] for lv in levels_present
    ]

    compute_increased = _is_monotone_increasing(comp_series)
    if not compute_increased:
        verdict = "MANIPULATION FAILED"
        detail = (
            "Median completion tokens did not increase monotonically across "
            "levels; reasoning compute was not actually varied, so the "
            "Reverse-Scaling Theorem cannot be tested (this is the E5 outcome)."
        )
    elif _is_monotone_nondecreasing(absrho_series):
        verdict = "REVERSE-SCALING CONFIRMED"
        detail = (
            "Reasoning compute increased monotonically and median |rho| was "
            "monotone non-decreasing across levels, as Theorem 2 predicts."
        )
    else:
        verdict = "REVERSE-SCALING REFUTED"
        detail = (
            "Reasoning compute increased monotonically but median |rho| did "
            "not; the data run against Theorem 2 on this model."
        )

    return {
        "levels_present": levels_present,
        "by_level": by_level,
        "primary_setting": PRIMARY_SETTING,
        "median_completion_tokens_series": comp_series,
        "median_tau_wall_series": wall_series,
        "median_abs_rho_series": absrho_series,
        "compute_increased": compute_increased,
        "verdict": verdict,
        "verdict_detail": detail,
    }


def _write_csv(result: dict[str, Any], path: Path) -> None:
    fields = [
        "agent_id",
        "level",
        "setting",
        "n_trajectories",
        "n_rho",
        "median_rho",
        "median_abs_rho",
        "median_completion_tokens",
        "median_tau_wall",
        "median_reasoning_chars",
        "n_truncated",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for level in result["levels_present"]:
            for setting in SETTINGS:
                row = result["by_level"][level].get(setting)
                if row is None:
                    continue
                w.writerow(
                    {
                        "agent_id": f"oss/deepseek-r1-14b-{level}",
                        "level": level,
                        "setting": setting,
                        **row,
                    }
                )


def _print_report(result: dict[str, Any]) -> None:
    print("=" * 68)
    print("E5b — Reverse-Scaling via reasoning-intensity induction")
    print("=" * 68)
    print(f"Primary setting: {result['primary_setting']}")
    print(f"Levels present : {', '.join(result['levels_present']) or '(none)'}")
    print()
    header = (
        f"{'level':<10}{'setting':<16}{'n':>4}{'n_rho':>7}"
        f"{'med_rho':>10}{'med|rho|':>10}{'med_tok':>10}{'med_wall':>10}"
    )
    print(header)
    print("-" * len(header))
    for level in result["levels_present"]:
        for setting in SETTINGS:
            row = result["by_level"][level].get(setting)
            if row is None:
                continue

            def fmt(v: Any, nd: int = 3) -> str:
                return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "  -  "

            print(
                f"{level:<10}{setting:<16}{row['n_trajectories']:>4}"
                f"{row['n_rho']:>7}{fmt(row['median_rho']):>10}"
                f"{fmt(row['median_abs_rho']):>10}"
                f"{fmt(row['median_completion_tokens'], 0):>10}"
                f"{fmt(row['median_tau_wall'], 1):>10}"
            )
    print()
    print(f"Reasoning compute increased across levels? {result['compute_increased']}")
    print(f"  median completion tokens : {result['median_completion_tokens_series']}")
    print(f"  median tau_wall          : {result['median_tau_wall_series']}")
    print(f"  median |rho|             : {result['median_abs_rho_series']}")
    print()
    print(f"VERDICT: {result['verdict']}")
    print(f"  {result['verdict_detail']}")
    print("=" * 68)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Analyze E5b reasoning-induction runs.")
    parser.add_argument("--input-dir", default="e5b-results", help="E5b results directory.")
    parser.add_argument(
        "--output-csv",
        default=None,
        help="Optional path to write per-(level,setting) metrics CSV.",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional path to write the full result summary as JSON.",
    )
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"input dir not found: {input_dir}")

    result = analyze(input_dir)
    _print_report(result)

    if args.output_csv:
        _write_csv(result, Path(args.output_csv))
        print(f"\nWrote metrics CSV: {args.output_csv}")
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Wrote summary JSON: {args.output_json}")


if __name__ == "__main__":
    main()
