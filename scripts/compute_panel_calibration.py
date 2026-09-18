#!/usr/bin/env python3
"""T3.3 coverage of the agent's own stated 90% CI, computed from trajectories.

Companion to compute_panel_epsilon.py, and it exists for the same reason: the
calibration leaderboard carried a hardcoded table that nothing re-derived, so
nothing could tell you when it went stale against the corpus.

Reuses `t3_3_score` from analyze_e1.py so the figure, the appendix table and
the analysis script cannot disagree about what "covered" means.

    python3 scripts/compute_panel_calibration.py           # print + write CSV
    python3 scripts/compute_panel_calibration.py --check    # exit 1 if stale
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import sys
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_e1 import t3_3_score  # noqa: E402

OUT = Path("pilot-results/panel_calibration.csv")

# label -> T3.3 globs. "{s}" is the setting; coverage is reported per setting
# because injection changes what the agent says even where it cannot change
# what the agent knows, and pooling would hide that.
PANEL: dict[str, list[str]] = {
    "Claude Sonnet 4.6 + thinking": ["e3-results/claude-sonnet-4-6-thinking/**/T3.3/{s}/*.json"],
    "Kimi-K2.6":                    ["vultr-results/kimi-k2.6/**/T3.3/{s}/*.json"],
    "o4-mini (reasoning)":          ["e1-results/o4-mini/**/T3.3/{s}/*.json"],
    "Claude Sonnet 4.6":            ["pilot-results/anthropic_claude-sonnet-4-6/T3.3/{s}/*.json",
                                     "e1-results/claude-sonnet-4-6/**/T3.3/{s}/*.json"],
    "MiniMax-M2.7":                 ["vultr-results/minimax-m2.7/**/T3.3/{s}/*.json"],
    "Qwen3.6-27B":                  ["vultr-results/qwen3.6-27b/**/T3.3/{s}/*.json"],
    "o3 (reasoning)":               ["pilot-results/openai_o3/T3.3/{s}/*.json",
                                     "e1-results/o3/**/T3.3/{s}/*.json"],
    "gpt-5.1":                      ["pilot-results/openai_gpt-5.1/T3.3/{s}/*.json",
                                     "e1-results/gpt-5.1/**/T3.3/{s}/*.json"],
    "gpt-4o-mini":                  ["pilot-results/openai_gpt-4o-mini/T3.3/{s}/*.json",
                                     "e1-results/gpt-4o-mini/**/T3.3/{s}/*.json"],
    "Claude Haiku 4.5":             ["pilot-results/anthropic_claude-haiku-4-5/T3.3/{s}/*.json",
                                     "e1-results/claude-haiku-4-5/**/T3.3/{s}/*.json"],
    "gpt-4o":                       ["pilot-results/openai_gpt-4o/T3.3/{s}/*.json",
                                     "e1-results/gpt-4o/**/T3.3/{s}/*.json"],
    "GLM-5.2-FP8":                  ["vultr-results/glm-5.2-fp8/**/T3.3/{s}/*.json"],
}

FIELDS = ["agent", "setting", "coverage_pct", "n_decided", "median_ci_width_s", "median_tau_wall_s"]


def row_for(label: str, patterns: list[str], setting: str) -> dict:
    in_ci, widths, walls = [], [], []
    for pat in patterns:
        for fp in glob.glob(pat.format(s=setting), recursive=True):
            try:
                d = json.load(open(fp))
            except (OSError, json.JSONDecodeError):
                continue
            steps = d.get("steps") or []
            if not steps:
                continue
            tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
            r = t3_3_score(steps[-1].get("action", ""), tw)
            if r["in_ci"] is not None:
                in_ci.append(r["in_ci"])
                walls.append(tw)
            if r["width"] is not None:
                widths.append(r["width"])
    return {
        "agent": label,
        "setting": "A" if setting == "no_injection" else "B",
        "coverage_pct": round(100.0 * sum(in_ci) / len(in_ci), 1) if in_ci else None,
        "n_decided": len(in_ci),
        "median_ci_width_s": round(median(widths), 1) if widths else None,
        "median_tau_wall_s": round(median(walls), 1) if walls else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows = [row_for(k, v, st) for k, v in PANEL.items()
            for st in ("no_injection", "with_injection")]
    rows = [r for r in rows if r["coverage_pct"] is not None]
    best: dict[str, float] = {}
    for r in rows:
        best[r["agent"]] = max(best.get(r["agent"], 0.0), r["coverage_pct"])
    rows.sort(key=lambda r: (-best[r["agent"]], r["agent"], r["setting"]))

    w = max(len(r["agent"]) for r in rows)
    print(f"{'agent':<{w}}  set  {'cov%':>6}  {'n':>4}  {'CI width':>9}  {'tau_wall':>9}")
    for r in rows:
        print(f"{r['agent']:<{w}}   {r['setting']}   {r['coverage_pct']:6.1f}  {r['n_decided']:4d}"
              f"  {r['median_ci_width_s']:9.1f}  {r['median_tau_wall_s']:9.1f}")

    if args.check:
        if not OUT.exists():
            print(f"\n{OUT} missing"); return 1
        disk = list(csv.DictReader(open(OUT)))
        same = len(disk) == len(rows) and all(
            str(d[k]) == str(r[k]) for d, r in zip(disk, rows) for k in FIELDS)
        print("\nCSV up to date" if same else f"\n{OUT} is STALE -- rerun without --check")
        return 0 if same else 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=FIELDS)
        wr.writeheader()
        wr.writerows(rows)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
