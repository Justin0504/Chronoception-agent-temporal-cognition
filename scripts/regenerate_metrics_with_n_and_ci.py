#!/usr/bin/env python3
"""Regenerate per-cell metrics with effective N + bootstrap CIs + Wilson intervals.

Fixes reviewer P1-1 / P1-2:
  - All rho cells get n_rho + bootstrap 95% CI on median |rho|
  - All T1.1 cells get n_decided + Wilson 95% CI on pass rate
  - Underpowered cells (n < 10) flagged

Output: pilot-results/metrics_with_ci.csv
"""
from __future__ import annotations
import argparse, csv, json
from math import log10, sqrt
from pathlib import Path
from statistics import median
import random

import numpy as np
from scipy.stats import binomtest


def bootstrap_ci(values, n_iter=10000, ci=0.95, stat=lambda v: median(map(abs, v)), seed=0):
    """Returns (point, low, high) for stat(v) via percentile bootstrap."""
    if not values:
        return None, None, None
    rng = random.Random(seed)
    n = len(values)
    samples = []
    for _ in range(n_iter):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(stat(sample))
    samples.sort()
    alpha = (1 - ci) / 2
    low = samples[int(alpha * n_iter)]
    high = samples[int((1 - alpha) * n_iter)]
    return stat(values), low, high


def wilson_ci(successes, n, alpha=0.05):
    """Wilson score interval for a proportion."""
    if n == 0:
        return None, None
    z = 1.96  # 95% normal quantile
    p_hat = successes / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    half = (z * sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2))) / denom
    return max(0, center - half), min(1, center + half)


def load_trajectories(root):
    """Yield trajectory dicts from a *-results directory."""
    for p in Path(root).rglob("*.json"):
        try:
            yield json.loads(p.read_text())
        except Exception:
            continue


def parse_t11_pass(action: str, run_date_iso: str) -> bool | None:
    """Mirror existing T1.1 parser logic (simplified)."""
    if not action:
        return None
    a = action.lower()
    # explicit refusal/cutoff disclosure
    if any(kw in a for kw in ["i do not know", "training data", "training cutoff",
                              "cannot determine", "no access to", "i don't have access"]):
        return False
    # try to find run_date string in action
    if run_date_iso[:10] in action or run_date_iso[:10].replace("-", "/") in action:
        return True
    # accept "current year" matches around run year
    yyyy = run_date_iso[:4]
    if yyyy in action:
        return True
    return None  # undecided


def extract_rho(traj):
    steps = traj.get("steps") or []
    if not steps:
        return None
    tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
    ts = traj.get("self_narrated_duration")
    if ts is None or ts <= 0 or tw <= 0:
        return None
    return log10(ts / tw)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dirs", nargs="+",
                   default=["pilot-results", "e1-results", "e2-results",
                            "e3-results", "e5-results"])
    p.add_argument("--output", default="pilot-results/metrics_with_ci.csv")
    args = p.parse_args()

    # Group trajectories by (agent_id, capability, setting)
    groups = {}
    for d in args.input_dirs:
        if not Path(d).exists():
            continue
        for traj in load_trajectories(d):
            key = (traj["agent_id"],
                   traj.get("capability_code", "unknown"),
                   traj.get("metadata", {}).get("setting", "unknown"))
            groups.setdefault(key, []).append(traj)

    rows = []
    for (agent, cap, setting), trajs in sorted(groups.items()):
        n_total = len(trajs)
        row = {
            "agent_id": agent, "capability": cap, "setting": setting,
            "n_total": n_total,
        }

        if cap == "T1.1":
            n_decided = 0
            passes = 0
            for t in trajs:
                steps = t.get("steps") or []
                if not steps: continue
                action = steps[-1].get("action", "")
                run_date = ""
                try:
                    from datetime import datetime, timezone
                    run_date = datetime.fromtimestamp(
                        float(steps[0]["timestamp"]), tz=timezone.utc
                    ).isoformat()
                except Exception:
                    pass
                v = parse_t11_pass(action, run_date)
                if v is None: continue
                n_decided += 1
                if v: passes += 1
            row["n_decided"] = n_decided
            row["pass_rate"] = passes / n_decided if n_decided else None
            lo, hi = wilson_ci(passes, n_decided)
            row["pass_rate_ci_low"] = lo
            row["pass_rate_ci_high"] = hi
            row["underpowered"] = n_decided < 10

        else:
            rhos = [extract_rho(t) for t in trajs]
            rhos = [r for r in rhos if r is not None]
            row["n_rho"] = len(rhos)
            if rhos:
                med_signed, lo_s, hi_s = bootstrap_ci(rhos, stat=lambda v: median(v))
                med_abs, lo_a, hi_a = bootstrap_ci(rhos, stat=lambda v: median(abs(r) for r in v))
                row["median_rho"] = med_signed
                row["median_rho_ci_low"] = lo_s
                row["median_rho_ci_high"] = hi_s
                row["median_abs_rho"] = med_abs
                row["median_abs_rho_ci_low"] = lo_a
                row["median_abs_rho_ci_high"] = hi_a
            row["underpowered"] = len(rhos) < 10

        rows.append(row)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        cols = sorted({k for r in rows for k in r.keys()})
        with out_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"Wrote {len(rows)} rows to {out_path}")

    # Print underpowered cells summary
    under = [r for r in rows if r.get("underpowered")]
    print(f"\n{'='*70}\nUNDERPOWERED CELLS (n < 10), flagged in CSV:")
    print(f"{'='*70}")
    for r in under:
        cap = r['capability']
        n_field = r.get("n_rho", r.get("n_decided", "?"))
        print(f"  {r['agent_id']:35s} {cap:6s} {r['setting']:15s} n={n_field}")


if __name__ == "__main__":
    main()
