#!/usr/bin/env python3
"""Back-parse ``self_narrated_duration`` on already-saved trajectories.

The runner writes ``self_narrated_duration=None`` and expects a downstream
parser pass to fill it. Post Route B-1 we had ~950 rho-candidate trajectories
(reasoning-model T3.1 + Sonnet-thinking T3.1/T3.2/T3.3) sitting at None because
the parser never ran on them.

This script walks every T3.1 / T3.2 / T3.3 JSON under given result dirs,
extracts tau_self using:
  1. project regex parser (fast, deterministic)
  2. Anthropic Claude Haiku LLM-judge fallback (when regex returns None)
and writes the value back into the same JSON file. Existing non-None values
are preserved.

Usage:
    python scripts/backparse_tau_self.py \\
        --dirs e3-results/claude-sonnet-4-6-thinking e1-results/o3 e1-results/o4-mini \\
        --caps T3.1 T3.2 T3.3
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path

from chronoception.bench.parsers.tau_self import (
    extract_tau_self_retrospective,
    extract_tau_self_prospective,
)

JUDGE_MODEL = "claude-haiku-4-5"
JUDGE_PROMPT = (
    "You will be given the terminal output of an AI agent that just completed a task. "
    "Your job: extract the duration the agent reports its work took, in seconds. "
    "If the agent gave a numeric duration (e.g. '3.2 seconds', 'about 2 minutes'), "
    "output ONLY the number of seconds (float). If the agent hedged ('a few', 'moments'), "
    "map to a rough seconds estimate. If the agent refused to estimate or the output "
    "contains no duration self-report, output ONLY the string NONE.\n\n"
    "Agent output:\n---\n{action}\n---\n"
    "Duration in seconds (a number or NONE):"
)


def make_client():
    import anthropic  # deferred so --caps-only runs don't require the SDK
    return anthropic.Anthropic()


def llm_judge(client, action: str) -> float | None:
    if not action:
        return None
    try:
        resp = client.messages.create(
            model=JUDGE_MODEL,
            max_tokens=32,
            temperature=0.0,
            messages=[{"role": "user", "content": JUDGE_PROMPT.format(action=action[:8000])}],
        )
    except Exception as e:
        print(f"    [judge error] {e}", file=sys.stderr)
        return None
    text = "".join(b.text for b in resp.content if hasattr(b, "text")).strip()
    if text.upper().startswith("NONE"):
        return None
    try:
        return float(text.split()[0])
    except Exception:
        return None


def parse_one(traj: dict, capability: str, client=None) -> tuple[float | None, str]:
    """Returns (value_or_None, source_tag)."""
    steps = traj.get("steps") or []
    if not steps:
        return None, "no_steps"
    action = steps[-1].get("action", "") or ""

    if capability == "T3.2":
        parser = extract_tau_self_prospective
    else:  # T3.1, T3.3 both use retrospective phrasing
        parser = extract_tau_self_retrospective

    v = parser(action)
    if v is not None:
        return v, "regex"
    if client is None:
        return None, "regex_none"
    v = llm_judge(client, action)
    if v is not None:
        return v, "judge"
    return None, "judge_none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--caps", nargs="+", default=["T3.1", "T3.2", "T3.3"])
    ap.add_argument("--no-judge", action="store_true",
                    help="Regex only; skip LLM-judge fallback (no API cost).")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    client = None if args.no_judge else make_client()

    tally = {"regex": 0, "judge": 0, "regex_none": 0, "judge_none": 0,
             "no_steps": 0, "preserved": 0, "written": 0, "seen": 0}
    files_by_cap = {c: [] for c in args.caps}

    for d in args.dirs:
        for p in Path(d).rglob("*.json"):
            try:
                t = json.loads(p.read_text())
            except Exception:
                continue
            cap = t.get("capability_code")
            if cap not in args.caps:
                continue
            files_by_cap[cap].append(p)

    for cap, paths in files_by_cap.items():
        print(f"\n=== {cap}: {len(paths)} candidate files ===")
        for i, p in enumerate(paths, 1):
            tally["seen"] += 1
            t = json.loads(p.read_text())
            if t.get("self_narrated_duration") is not None:
                tally["preserved"] += 1
                continue
            v, src = parse_one(t, cap, client=client)
            tally[src] += 1
            if v is not None and not args.dry_run:
                t["self_narrated_duration"] = v
                p.write_text(json.dumps(t, ensure_ascii=False, indent=2))
                tally["written"] += 1
            if i % 25 == 0:
                print(f"  [{cap}] {i}/{len(paths)}  regex={tally['regex']} "
                      f"judge={tally['judge']} miss={tally['regex_none']+tally['judge_none']}")

    print("\n=== summary ===")
    for k, v in tally.items():
        print(f"  {k:14s} {v}")


if __name__ == "__main__":
    main()
