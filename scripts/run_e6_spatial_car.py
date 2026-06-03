#!/usr/bin/env python3
"""E6 — Spatial-CAR test on SWE-Bench Lite (Paper 3 / Future Work).

The temporal mirror is T2.3 (wall-budget execution). This is its spatial
analog: agents are given a SPATIAL budget (max number of files to touch)
and asked to solve a code task. Expected pattern per Theorem 3 (SIT):
agents silently degrade the spatial budget into a step-count terminator,
just as they do with wall-clock budgets.

Spatial-CAR is defined as:
    SAR = sigma_world / S
where sigma_world is the number of distinct files the agent actually
touched, and S is the budget given to it.

Hypothesis (SL2 Visit-Step Conflation):
    SAR << 1 for budgets larger than the minimum file-set required to
    solve the task.

This is a scaffold. Running E6 requires:
  1. SWE-Bench Lite task set (300 issues)
  2. An agent harness that exposes file-edit / file-read tool calls
     trackable by the runner (so we can count distinct files touched)
  3. The standard ChronoBench result + epsilon pipeline

Without those, this script just describes the experiment design and
prints a stub trajectory schema.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

SPATIAL_BUDGETS = [2, 5, 10, 30, "unlimited"]


def design_e6() -> dict:
    """Return the E6 experimental design as a JSON-serialisable dict."""
    return {
        "experiment_id": "E6",
        "name": "Spatial-CAR on SWE-Bench Lite",
        "framework_section": "FRAMING.md §14.6 (v2.5)",
        "paper_section": "paper1/arxiv-v0/sections/12_future_work.tex",
        "hypothesis": "SL2 Visit-Step Conflation: spatial budgets are degraded to step terminators by CIT-regime agents",
        "panel": [
            "openai/gpt-4o-mini", "openai/gpt-4o", "openai/gpt-5.1",
            "openai/o3", "openai/o4-mini",
            "anthropic/claude-haiku-4-5", "anthropic/claude-sonnet-4-6",
            "oss/qwen2.5-7b-instruct", "oss/deepseek-r1-distill-qwen-14b",
        ],
        "task_source": "SWE-Bench Lite (300 issues)",
        "task_sample_size": 30,  # per (agent, budget) cell
        "spatial_budgets": SPATIAL_BUDGETS,
        "instrumentation": {
            "track": "distinct file paths touched by file-edit or file-read tool calls",
            "harness_requirement": "tool-use compatible (must surface file open/edit events)",
        },
        "metrics": {
            "primary": {
                "SAR(S, A)": "sigma_world_star / S, median across instances",
                "step_count_at_termination": "number of steps before stop",
                "task_success_rate": "SWE-Bench standard pass@1 score",
            },
            "secondary": {
                "rho_spatial": "log10(sigma_self / sigma_world) parsed from agent's post-task self-report of files touched",
                "elapsed_time_when_budget_exhausted": "wall-clock at the step where sigma_visit = S",
            },
        },
        "pre_registered_prediction_status": "P13 — Agentic Frontier (FRAMING §14.4)",
        "expected_pattern": {
            "non_reasoning_agents": "SAR < 0.2 for S >= 5 across all tasks",
            "reasoning_agents": "same SAR pattern; but possibly higher sigma_self (cartographic over-report)",
        },
        "estimated_cost": {
            "openai_total_usd": 250.0,
            "anthropic_total_usd": 180.0,
            "oss_compute_gpu_hours": 30.0,
            "wall_clock_runtime_hours": 30.0,
        },
        "deferred_to": "Paper 3 (The Agentic Frontier)",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--print-design", action="store_true",
                   help="Print the experiment design JSON and exit.")
    p.add_argument("--validate-harness", action="store_true",
                   help="Stub: check whether the SWE-Bench harness is installed.")
    args = p.parse_args()

    design = design_e6()

    if args.print_design:
        json.dump(design, sys.stdout, indent=2)
        print()
        return

    if args.validate_harness:
        # SWE-Bench harness check (stub)
        try:
            import swebench  # type: ignore[import-not-found]
            print("[E6] swebench harness available:", swebench.__version__)
        except ImportError:
            print("[E6] swebench not installed; install via `pip install swebench` to run E6.")
        return

    # Default: print short summary
    print(f"E6 — {design['name']}")
    print(f"  hypothesis: {design['hypothesis']}")
    print(f"  panel: {len(design['panel'])} agents")
    print(f"  budgets: {design['spatial_budgets']}")
    print(f"  estimated total cost: ${design['estimated_cost']['openai_total_usd'] + design['estimated_cost']['anthropic_total_usd']:.0f}")
    print(f"  deferred to: {design['deferred_to']}")
    print()
    print("Run with --print-design for the full JSON design document.")


if __name__ == "__main__":
    main()
