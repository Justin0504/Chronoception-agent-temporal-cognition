#!/usr/bin/env python3
"""Analyzer for the T3.1 paraphrase-robustness experiment.

Answers the reviewer question "is the rho finding an artifact of the prompt
wording?" with two robustness measures:

1. Within-agent stability. For each agent, the spread (max - min) of median
   |rho| across paraphrase variants. If that spread is small relative to the
   Augustine threshold (eps* = 0.20) -- and tiny relative to the paper's
   cross-generation effect (median |rho| 1.12 -> 0.07, a range of ~1.05) --
   the finding is not a wording artifact.

2. Cross-agent rank stability (when >= 2 agents are present). For each pair of
   paraphrase variants, the Spearman rank correlation of the agents' |rho|
   ordering. A high mean correlation means the paper's panel ranking survives
   rewording. Spearman is computed with the standard library only.

Usage
-----
    python scripts/analyze_t31_paraphrase.py --input-dir t31-robustness-results
    python scripts/analyze_t31_paraphrase.py --input-dir t31-robustness-results \
        --setting no_injection --output-csv t31-robustness-results/metrics.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

# Within-agent: spread of median |rho| across variants below this is "robust".
DEFAULT_SPREAD_THRESHOLD = 0.20  # the Augustine threshold eps*
# Cross-agent: mean pairwise Spearman at/above this is "rank-stable".
DEFAULT_RANK_THRESHOLD = 0.80
# Context only: the paper's cross-generation |rho| range.
PAPER_CROSS_GENERATION_RANGE = 1.05


def _rho(traj: dict[str, Any]) -> float | None:
    tau_self = traj.get("self_narrated_duration")
    tau_wall = traj.get("tau_wall")
    if not isinstance(tau_self, (int, float)) or tau_self <= 0:
        return None
    if not isinstance(tau_wall, (int, float)) or tau_wall <= 0:
        return None
    return math.log10(tau_self / tau_wall)


def _median(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def _load(input_dir: Path, setting: str) -> dict[str, dict[str, dict[str, float | int | None]]]:
    """Return {agent: {variant: {median_rho, median_abs_rho, n_rho, n}}}."""
    out: dict[str, dict[str, dict[str, float | int | None]]] = {}
    for agent_dir in sorted(p for p in input_dir.iterdir() if p.is_dir()):
        agent = agent_dir.name
        for variant_dir in sorted(p for p in agent_dir.iterdir() if p.is_dir()):
            variant = variant_dir.name
            files = sorted((variant_dir / "T3.1" / setting).glob("*.json"))
            if not files:
                continue
            rhos: list[float] = []
            n = 0
            for f in files:
                with f.open(encoding="utf-8") as fh:
                    traj = json.load(fh)
                n += 1
                r = _rho(traj)
                if r is not None:
                    rhos.append(r)
            out.setdefault(agent, {})[variant] = {
                "median_rho": _median(rhos),
                "median_abs_rho": _median([abs(r) for r in rhos]),
                "n_rho": len(rhos),
                "n": n,
            }
    return out


# ---------- Spearman (stdlib) ----------


def _rankdata(xs: list[float]) -> list[float]:
    """Average-rank of each element (ties share the mean rank)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # 1-based average rank
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(a: list[float], b: list[float]) -> float | None:
    n = len(a)
    if n < 2:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = math.sqrt(sum((x - ma) ** 2 for x in a))
    vb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if va == 0 or vb == 0:
        return None
    return cov / (va * vb)


def _spearman(a: list[float], b: list[float]) -> float | None:
    return _pearson(_rankdata(a), _rankdata(b))


def analyze(input_dir: Path, setting: str, spread_threshold: float, rank_threshold: float) -> dict[str, Any]:
    data = _load(input_dir, setting)
    agents = sorted(data)
    # Variant set = union, but use the intersection for rank comparisons.
    all_variants = sorted({v for a in data.values() for v in a})

    # 1. Within-agent spread.
    within: dict[str, dict[str, Any]] = {}
    for agent in agents:
        vals = [
            data[agent][v]["median_abs_rho"]
            for v in all_variants
            if v in data[agent] and data[agent][v]["median_abs_rho"] is not None
        ]
        if len(vals) >= 2:
            spread = max(vals) - min(vals)
            within[agent] = {
                "median_abs_rho_by_variant": {
                    v: data[agent][v]["median_abs_rho"] for v in all_variants if v in data[agent]
                },
                "spread": spread,
                "mean": statistics.mean(vals),
                "robust": spread < spread_threshold,
            }

    # 2. Cross-agent rank stability. Needs >= 3 agents: ranking 2 agents is
    # degenerate (Spearman is always +/-1), so we gate this on 3+ and use the
    # cross-model profile measure below for the 2-agent case.
    rank_stability: dict[str, Any] = {}
    if len(agents) >= 3:
        common = [v for v in all_variants if all(v in data[a] and data[a][v]["median_abs_rho"] is not None for a in agents)]
        pair_corrs: list[float] = []
        per_pair: dict[str, float | None] = {}
        for v1, v2 in combinations(common, 2):
            x = [data[a][v1]["median_abs_rho"] for a in agents]
            y = [data[a][v2]["median_abs_rho"] for a in agents]
            rho = _spearman(x, y)
            per_pair[f"{v1}~{v2}"] = rho
            if rho is not None:
                pair_corrs.append(rho)
        rank_stability = {
            "common_variants": common,
            "per_pair_spearman": per_pair,
            "mean_pairwise_spearman": statistics.mean(pair_corrs) if pair_corrs else None,
            "rank_stable": (statistics.mean(pair_corrs) >= rank_threshold) if pair_corrs else None,
        }

    # Cross-model wording-effect consistency: do models agree on WHICH
    # paraphrases elicit higher |rho|? For each agent pair, Spearman of their
    # variant |rho| profiles. This is the meaningful cross-model robustness
    # measure when only 2 agents are available (rank_stability above is
    # degenerate with < 3 agents); it needs >= 3 common variants.
    cross_model_profile: dict[str, Any] = {}
    if len(agents) >= 2:
        common_v = [
            v for v in all_variants
            if all(v in data[a] and data[a][v]["median_abs_rho"] is not None for a in agents)
        ]
        if len(common_v) >= 3:
            pair_profile: dict[str, float | None] = {}
            corrs: list[float] = []
            for a1, a2 in combinations(agents, 2):
                p1 = [data[a1][v]["median_abs_rho"] for v in common_v]
                p2 = [data[a2][v]["median_abs_rho"] for v in common_v]
                c = _spearman(p1, p2)
                pair_profile[f"{a1}~{a2}"] = c
                if c is not None:
                    corrs.append(c)
            cross_model_profile = {
                "common_variants": common_v,
                "per_pair_spearman": pair_profile,
                "mean_spearman": statistics.mean(corrs) if corrs else None,
                "consistent": (statistics.mean(corrs) >= rank_threshold) if corrs else None,
            }

    # Verdict.
    within_robust = [a for a, w in within.items() if w["robust"]]
    if within and len(within_robust) == len(within):
        within_verdict = "ROBUST"
    elif within_robust:
        within_verdict = "MOSTLY ROBUST"
    elif within:
        within_verdict = "NOT ROBUST"
    else:
        within_verdict = "INSUFFICIENT DATA"

    return {
        "setting": setting,
        "agents": agents,
        "variants": all_variants,
        "within_agent": within,
        "within_verdict": within_verdict,
        "rank_stability": rank_stability,
        "cross_model_profile": cross_model_profile,
        "spread_threshold": spread_threshold,
        "rank_threshold": rank_threshold,
        "paper_cross_generation_range": PAPER_CROSS_GENERATION_RANGE,
    }


def _print_report(result: dict[str, Any]) -> None:
    print("=" * 70)
    print("T3.1 paraphrase robustness")
    print("=" * 70)
    print(f"Setting : {result['setting']}")
    print(f"Agents  : {', '.join(result['agents']) or '(none)'}")
    print(f"Variants: {', '.join(result['variants']) or '(none)'}")
    print()
    print("Within-agent stability (median |rho| across paraphrases)")
    print("-" * 70)
    for agent, w in result["within_agent"].items():
        by_v = w["median_abs_rho_by_variant"]
        cells = "  ".join(f"{v.split('_')[0]}={val:.3f}" for v, val in by_v.items())
        flag = "robust" if w["robust"] else "NOT robust"
        print(f"  {agent}")
        print(f"    {cells}")
        print(f"    spread={w['spread']:.3f} (threshold {result['spread_threshold']:.2f}) -> {flag}")
        print(f"    context: paper cross-generation range ~{result['paper_cross_generation_range']:.2f}")
    print()
    rs = result["rank_stability"]
    if rs:
        print("Cross-agent rank stability (Spearman over paraphrase pairs)")
        print("-" * 70)
        mp = rs["mean_pairwise_spearman"]
        print(f"  mean pairwise Spearman = {mp:.3f}" if mp is not None else "  (insufficient)")
        if rs.get("rank_stable") is not None:
            print(f"  rank-stable (>= {result['rank_threshold']:.2f})? {rs['rank_stable']}")
    else:
        print("Cross-agent rank stability: needs >= 3 agents (ranking 2 is degenerate).")
    print()
    cm = result.get("cross_model_profile") or {}
    if cm:
        print("Cross-model wording-effect consistency (Spearman of variant profiles)")
        print("-" * 70)
        for pair, c in cm["per_pair_spearman"].items():
            print(f"  {pair}: {c:.3f}" if c is not None else f"  {pair}: n/a")
        ms = cm["mean_spearman"]
        if ms is not None:
            print(f"  mean = {ms:.3f}  -> models agree on the wording effect? {cm['consistent']}")
        print()
    print(f"VERDICT (within-agent): {result['within_verdict']}")
    print("=" * 70)


def _write_csv(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["agent", "variant", "median_abs_rho", "spread", "robust"])
        for agent, wd in result["within_agent"].items():
            for variant, val in wd["median_abs_rho_by_variant"].items():
                w.writerow([agent, variant, val, wd["spread"], wd["robust"]])


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Analyze T3.1 paraphrase robustness.")
    p.add_argument("--input-dir", default="t31-robustness-results")
    p.add_argument("--setting", default="no_injection")
    p.add_argument("--spread-threshold", type=float, default=DEFAULT_SPREAD_THRESHOLD)
    p.add_argument("--rank-threshold", type=float, default=DEFAULT_RANK_THRESHOLD)
    p.add_argument("--output-csv", default=None)
    p.add_argument("--output-json", default=None)
    args = p.parse_args(argv)

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"input dir not found: {input_dir}")

    result = analyze(input_dir, args.setting, args.spread_threshold, args.rank_threshold)
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
