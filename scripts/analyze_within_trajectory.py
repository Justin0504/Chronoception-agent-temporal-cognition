#!/usr/bin/env python3
"""Analyzer for the within-trajectory drift harness (P8 / P9).

For each multi-turn conversation it fits the slope of |rho_t| against step index
t. P8 predicts a positive slope (drift grows along a single trajectory). The
paper's cross-trajectory proxy ran against that direction; this is the direct
within-trajectory test the proxy could not be.

Outputs, per (agent, setting):
- per-conversation OLS slope of |rho_t| vs t
- median slope across conversations
- a sign test on slope direction (how many conversations drift up vs down)
- median |rho| at each step position (a quick eye-check of the trend)

Verdict on P8 (per agent, primary setting):
- P8 SUPPORTED  : median slope > +tol AND a majority of conversations drift up
- P8 REFUTED    : median slope < -tol AND a majority drift down (matches the
                  paper's cross-trajectory negative, now within-trajectory)
- FLAT/INCONCLUSIVE : |median slope| <= tol or no clear majority

Usage
-----
    python scripts/analyze_within_trajectory.py --input-dir within-trajectory-results
    python scripts/analyze_within_trajectory.py --input-dir within-trajectory-results \
        --setting no_injection --output-csv within-trajectory-results/slopes.csv
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

DEFAULT_SLOPE_TOL = 0.02  # |median slope| within this band is "flat"


def _ols_slope(xs: list[float], ys: list[float]) -> float | None:
    """Least-squares slope of y on x; None if undefined (< 2 pts or flat x)."""
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    var_x = sum((x - mx) ** 2 for x in xs)
    if var_x == 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / var_x


def _binom_two_sided_p(k: int, n: int) -> float | None:
    """Two-sided sign-test p-value under p=0.5 (exact). None if n == 0."""
    if n == 0:
        return None
    k = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def _conversation_slope(conv: dict[str, Any]) -> tuple[float | None, list[tuple[int, float]]]:
    """Return (slope of |rho_t| vs t, [(t, |rho_t|) used])."""
    pts: list[tuple[int, float]] = []
    for s in conv.get("steps", []):
        rho = s.get("rho_step")
        if isinstance(rho, (int, float)):
            pts.append((s["step_index"], abs(rho)))
    if len(pts) < 2:
        return None, pts
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return _ols_slope(xs, ys), pts


def _load(input_dir: Path, setting: str) -> dict[str, list[dict[str, Any]]]:
    """Return {agent: [conversation_record, ...]} for one setting."""
    out: dict[str, list[dict[str, Any]]] = {}
    for agent_dir in sorted(p for p in input_dir.iterdir() if p.is_dir()):
        files = sorted((agent_dir / setting).glob("*.json"))
        if not files:
            continue
        convs = []
        for f in files:
            with f.open(encoding="utf-8") as fh:
                convs.append(json.load(fh))
        out[agent_dir.name] = convs
    return out


def analyze(input_dir: Path, setting: str, tol: float, alpha: float = 0.05) -> dict[str, Any]:
    data = _load(input_dir, setting)
    per_agent: dict[str, Any] = {}

    for agent, convs in data.items():
        slopes: list[float] = []
        # Accumulate |rho| by step position across conversations for an eye-check.
        by_step: dict[int, list[float]] = {}
        for conv in convs:
            slope, pts = _conversation_slope(conv)
            if slope is not None:
                slopes.append(slope)
            for t, abs_rho in pts:
                by_step.setdefault(t, []).append(abs_rho)

        n = len(slopes)
        n_up = sum(1 for s in slopes if s > 0)
        n_down = sum(1 for s in slopes if s < 0)
        median_slope = statistics.median(slopes) if slopes else None
        sign_p = _binom_two_sided_p(n_up, n_up + n_down)

        # A directional verdict requires BOTH a slope beyond the tolerance band
        # AND a significant sign test. Without significance we report the trend
        # but refuse to call P8 supported/refuted -- this is what stops a 3-vs-2
        # split (p=1.0) from being mislabeled "supported".
        significant = sign_p is not None and sign_p < alpha
        if median_slope is None:
            verdict = "INSUFFICIENT DATA"
        elif median_slope > tol and n_up > n_down:
            verdict = "P8 SUPPORTED" if significant else "UP-TREND (not significant)"
        elif median_slope < -tol and n_down > n_up:
            verdict = "P8 REFUTED" if significant else "DOWN-TREND (not significant)"
        else:
            verdict = "FLAT/INCONCLUSIVE"

        per_agent[agent] = {
            "n_conversations_with_slope": n,
            "median_slope": median_slope,
            "mean_slope": statistics.mean(slopes) if slopes else None,
            "n_up": n_up,
            "n_down": n_down,
            "sign_test_p": sign_p,
            "significant_at_alpha": significant,
            "median_abs_rho_by_step": {
                t: statistics.median(v) for t, v in sorted(by_step.items())
            },
            "verdict": verdict,
        }

    return {"setting": setting, "slope_tol": tol, "alpha": alpha, "per_agent": per_agent}


def _print_report(result: dict[str, Any]) -> None:
    print("=" * 70)
    print("Within-trajectory drift (P8 / P9)")
    print("=" * 70)
    print(f"Setting   : {result['setting']}")
    print(f"Slope tol : {result['slope_tol']}")
    print(f"Alpha     : {result.get('alpha', 0.05)}")
    print()
    if not result["per_agent"]:
        print("(no data)")
        print("=" * 70)
        return
    for agent, a in result["per_agent"].items():
        print(f"Agent: {agent}")
        ms = a["median_slope"]
        print(f"  conversations with a slope : {a['n_conversations_with_slope']}")
        print(f"  median slope |rho_t| vs t  : {ms:.4f}" if ms is not None else "  median slope: n/a")
        print(f"  drift up / down            : {a['n_up']} / {a['n_down']}", end="")
        if a["sign_test_p"] is not None:
            print(f"  (sign-test p = {a['sign_test_p']:.3f})")
        else:
            print()
        bs = a["median_abs_rho_by_step"]
        if bs:
            trail = "  ".join(f"t{t}={v:.2f}" for t, v in bs.items())
            print(f"  median |rho| by step       : {trail}")
        print(f"  VERDICT                    : {a['verdict']}")
        print()
    print("=" * 70)


def _write_csv(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["agent", "median_slope", "mean_slope", "n_up", "n_down", "sign_test_p", "verdict"])
        for agent, a in result["per_agent"].items():
            w.writerow([agent, a["median_slope"], a["mean_slope"], a["n_up"],
                        a["n_down"], a["sign_test_p"], a["verdict"]])


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Analyze within-trajectory drift (P8/P9).")
    p.add_argument("--input-dir", default="within-trajectory-results")
    p.add_argument("--setting", default="no_injection")
    p.add_argument("--slope-tol", type=float, default=DEFAULT_SLOPE_TOL)
    p.add_argument("--alpha", type=float, default=0.05,
                   help="Significance level for the sign test on slope direction.")
    p.add_argument("--output-csv", default=None)
    p.add_argument("--output-json", default=None)
    args = p.parse_args(argv)

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"input dir not found: {input_dir}")

    result = analyze(input_dir, args.setting, args.slope_tol, args.alpha)
    _print_report(result)

    if args.output_csv:
        _write_csv(result, Path(args.output_csv))
        print(f"\nWrote slopes CSV: {args.output_csv}")
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Wrote summary JSON: {args.output_json}")


if __name__ == "__main__":
    main()
