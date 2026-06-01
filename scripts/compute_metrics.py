#!/usr/bin/env python3
"""Compute ChronoBench metrics from a pilot-results/ directory tree.

Reads JSON trajectories under {output_dir}/{agent_id}/{capability}/{setting}/
and computes per-(agent, capability, setting) summaries of alpha, CAR, rho,
and the aggregated epsilon. Outputs a CSV table and a per-setting epsilon
contrast (epsilon_A vs epsilon_B per the Injection Tell, FRAMING §3.1).

Also computes a Setting A vs Setting B pass-rate contrast for T1.1, which
is the headline observation behind Prediction P1a.

Usage:

    python scripts/compute_metrics.py \
        --input-dir pilot-results/ \
        --output-csv pilot-results/metrics.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from chronoception.bench import (
    EvalSetting,
    Step,
    Trajectory,
    car,
    chronoceptive_calibration_error,
    confabulation_ratio,
    parkinson_coefficient,
)
from chronoception.bench.parsers import extract_tau_self_retrospective


def _load_trajectory(path: Path) -> Trajectory:
    with path.open() as f:
        data = json.load(f)
    steps = [
        Step(state=s["state"], action=s["action"], timestamp=float(s["timestamp"]))
        for s in data["steps"]
    ]
    return Trajectory(
        task_id=data["task_id"],
        agent_id=data["agent_id"],
        steps=steps,
        capability_code=data.get("capability_code"),
        budget=data.get("budget"),
        budget_kind=data.get("budget_kind", "none"),
        tau_min=data.get("tau_min"),
        self_narrated_duration=data.get("self_narrated_duration"),
        metadata=data.get("metadata", {}),
    )


def _walk_trajectories(root: Path) -> Iterable[Trajectory]:
    for json_path in sorted(root.rglob("*.json")):
        try:
            yield _load_trajectory(json_path)
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            logging.warning("skip %s: %s", json_path, exc)


def _group_key(traj: Trajectory) -> tuple[str, str, str]:
    setting = traj.metadata.get("setting", "unknown")
    return (traj.agent_id, traj.capability_code or "unknown", setting)


# ---------- T1.1 pass-rate scoring ----------

from datetime import datetime, timedelta, timezone


_MONTH_NAMES = {
    1: ("january", "jan"),
    2: ("february", "feb"),
    3: ("march", "mar"),
    4: ("april", "apr"),
    5: ("may", "may"),
    6: ("june", "jun"),
    7: ("july", "jul"),
    8: ("august", "aug"),
    9: ("september", "sep", "sept"),
    10: ("october", "oct"),
    11: ("november", "nov"),
    12: ("december", "dec"),
}


def _today_patterns_for(traj: Trajectory) -> list[str]:
    """Return lowercase substrings that constitute 'pass' for the trajectory's
    actual run date.

    The trajectory's first-step timestamp is the Unix epoch time at which the
    API call was made. We accept multiple common phrasings of that exact date.
    """
    if not traj.steps:
        return []
    run_dt = datetime.fromtimestamp(traj.steps[0].timestamp, tz=timezone.utc)
    return _today_patterns_for_date(run_dt)


def _today_patterns_for_date(run_dt: datetime) -> list[str]:
    y = run_dt.strftime("%Y")
    mo_num = run_dt.strftime("%m")
    d_num = run_dt.strftime("%d")
    d_no_zero = run_dt.strftime("%d").lstrip("0")
    iso = run_dt.strftime("%Y-%m-%d")
    names = _MONTH_NAMES[run_dt.month]
    patterns = [iso]
    for nm in names:
        patterns.extend(
            [
                f"{nm} {d_no_zero}, {y}",
                f"{nm} {d_num}, {y}",
                f"{nm} {d_no_zero} {y}",
                f"{d_no_zero} {nm}, {y}",
                f"{d_no_zero} {nm} {y}",
                f"{nm} {d_no_zero}",  # less specific; combined with year check below
            ]
        )
    patterns.extend(
        [
            f"{mo_num}/{d_no_zero}/{y}",
            f"{d_no_zero}/{mo_num}/{y}",
            f"{y}/{mo_num}/{d_num}",
            f"{y}-{mo_num}-{d_no_zero}",  # tolerate single-digit day
        ]
    )
    return [p.lower() for p in patterns]


_REFUSAL_PATTERNS = (
    "unable to provide real-time",
    "i do not have",
    "i don't have access",
    "i cannot tell",
    "training only includes data",
    "cutoff date",
    "knowledge cutoff",
    "last updated",
    "do not perceive",
    "real-time information",
    "real-time clock",
)


def _t11_pass(traj: Trajectory) -> bool | None:
    """Heuristic: did the agent confidently report TODAY'S date?

    Compares the agent's response against the trajectory's actual run date
    (derived from the first step's wall-clock timestamp). This corrects the
    earlier heuristic which accepted any 4-digit 20xx year as 'pass' — a
    training-cutoff date like '2024' would falsely score as pass.

    Returns True if the response contains a recognisable form of the actual
    run date. Returns False if the response is a refusal/disclaimer without
    today's date. Returns None when neither signal is present.
    """
    if not traj.steps:
        return None
    text = traj.steps[-1].action.lower()
    today_patterns = _today_patterns_for(traj)
    mentions_today = any(p in text for p in today_patterns)
    refused = any(pat in text for pat in _REFUSAL_PATTERNS)
    if mentions_today:
        return True
    if refused:
        return False
    return None


# ---------- main analysis ----------


def analyze(input_dir: Path, drop_retry_outliers: bool = True) -> dict[str, Any]:
    """Compute per-group metric tables.

    When drop_retry_outliers=True (default), trajectories whose tau_wall
    exceeds their budget by more than 10x are excluded — these are almost
    always SDK rate-limit retries rather than real agent behavior. The
    count of excluded trajectories is reported alongside the metric.
    """
    by_group: dict[tuple[str, str, str], list[Trajectory]] = defaultdict(list)
    for traj in _walk_trajectories(input_dir):
        by_group[_group_key(traj)].append(traj)

    rows: list[dict[str, Any]] = []

    for (agent_id, capability, setting), trajs in sorted(by_group.items()):
        # Drop SDK-retry outliers if requested
        n_outliers = 0
        clean_trajs = []
        for traj in trajs:
            is_outlier = (
                drop_retry_outliers
                and traj.budget_kind == "wall"
                and traj.budget is not None
                and traj.budget > 0
                and traj.tau_wall > 10 * traj.budget
            )
            if is_outlier:
                n_outliers += 1
            else:
                clean_trajs.append(traj)

        # alpha (only L1 / wall axis): defined when budget=wall and tau_min set
        alphas: list[float] = []
        for traj in clean_trajs:
            if (
                traj.budget_kind == "wall"
                and traj.tau_min is not None
                and traj.budget is not None
                and traj.budget > traj.tau_min
            ):
                alphas.append(parkinson_coefficient(traj))

        # CAR (L2): defined when wall budget present
        cars: list[float] = []
        for traj in clean_trajs:
            if traj.budget_kind == "wall" and traj.budget is not None and traj.budget > 0:
                cars.append(car(traj))

        # rho (L3): parse from response if not already set
        rhos: list[float] = []
        for traj in clean_trajs:
            tau_self = traj.self_narrated_duration
            if tau_self is None and traj.steps:
                tau_self = extract_tau_self_retrospective(traj.steps[-1].action)
            if (
                tau_self is not None
                and tau_self > 0
                and traj.tau_wall > 0
            ):
                from math import log10
                rhos.append(log10(tau_self / traj.tau_wall))

        # T1.1 pass rate (only meaningful for T1.1)
        passes = 0
        decided = 0
        for traj in clean_trajs:
            verdict = _t11_pass(traj)
            if verdict is None:
                continue
            decided += 1
            if verdict:
                passes += 1
        pass_rate = passes / decided if decided > 0 else None

        rows.append(
            {
                "agent_id": agent_id,
                "capability": capability,
                "setting": setting,
                "n_trajectories": len(trajs),
                "n_outliers_dropped": n_outliers,
                "median_alpha": _median(alphas),
                "mean_alpha": _mean(alphas),
                "n_alpha": len(alphas),
                "median_car": _median(cars),
                "mean_car": _mean(cars),
                "n_car": len(cars),
                "median_rho": _median(rhos),
                "mean_rho": _mean(rhos),
                "n_rho": len(rhos),
                "t11_pass_rate": pass_rate,
                "t11_n_decided": decided,
            }
        )

    # Compute epsilon per (agent_id, setting) by pooling across capabilities
    epsilon_rows: list[dict[str, Any]] = []
    by_agent_setting: dict[tuple[str, str], list[Trajectory]] = defaultdict(list)
    for traj in _walk_trajectories(input_dir):
        # Re-parse tau_self if needed for the aggregate epsilon
        if traj.self_narrated_duration is None and traj.steps:
            parsed = extract_tau_self_retrospective(traj.steps[-1].action)
            if parsed is not None:
                traj = Trajectory(
                    task_id=traj.task_id,
                    agent_id=traj.agent_id,
                    steps=traj.steps,
                    capability_code=traj.capability_code,
                    budget=traj.budget,
                    budget_kind=traj.budget_kind,
                    tau_min=traj.tau_min,
                    self_narrated_duration=parsed,
                    metadata=traj.metadata,
                )
        setting = traj.metadata.get("setting", "unknown")
        by_agent_setting[(traj.agent_id, setting)].append(traj)

    for (agent_id, setting), trajs in sorted(by_agent_setting.items()):
        try:
            eps = chronoceptive_calibration_error(trajs)
        except ValueError:
            eps = None
        epsilon_rows.append(
            {
                "agent_id": agent_id,
                "setting": setting,
                "n_trajectories": len(trajs),
                "epsilon": eps,
            }
        )

    return {"per_group": rows, "epsilon": epsilon_rows}


def _mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def _median(xs: list[float]) -> float | None:
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _format_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "(no data)"
    headers = list(rows[0].keys())
    cols = [str(h) for h in headers]
    widths = [len(c) for c in cols]
    for r in rows:
        for i, h in enumerate(headers):
            v = r[h]
            s = "—" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
            widths[i] = max(widths[i], len(s))
    lines = []
    lines.append(" | ".join(c.ljust(widths[i]) for i, c in enumerate(cols)))
    lines.append("-+-".join("-" * w for w in widths))
    for r in rows:
        cells = []
        for i, h in enumerate(headers):
            v = r[h]
            s = "—" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
            cells.append(s.ljust(widths[i]))
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="pilot-results", help="root of trajectory tree")
    parser.add_argument("--output-csv", default=None, help="where to write per-group CSV")
    parser.add_argument("--epsilon-csv", default=None, help="where to write per-(agent, setting) epsilon CSV")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"input dir {input_dir} does not exist")

    result = analyze(input_dir)

    print("\n=== Per-group metrics ===\n")
    print(_format_table(result["per_group"]))
    print("\n=== Per-(agent, setting) epsilon ===\n")
    print(_format_table(result["epsilon"]))

    if args.output_csv:
        _write_csv(result["per_group"], Path(args.output_csv))
        logging.info("wrote per-group CSV: %s", args.output_csv)
    if args.epsilon_csv:
        _write_csv(result["epsilon"], Path(args.epsilon_csv))
        logging.info("wrote epsilon CSV: %s", args.epsilon_csv)


if __name__ == "__main__":
    main()
