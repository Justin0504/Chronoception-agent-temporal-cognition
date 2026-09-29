#!/usr/bin/env python3
"""E12 -- does forcing an estimate change rho, or only who answers?

The problem
-----------
On T3.1, reasoning-mode agents decline to estimate their own duration far more
often than non-reasoning ones: 21.9% against 1.2%, and Sonnet 4.6 + thinking
declines on 57% of trajectories. So the rho we report for those agents is
computed on a SELECTED subsample -- the trajectories where the agent chose to
commit a number -- and the cross-model sign flip in Fig. 3(b) rests on the 43%
where it answered. We disclose that in the paper and say we cannot bound the
direction of the selection from those data. This experiment bounds it.

Design
------
Three arms on the same T3.1-style tasks, n per arm below:

  free      the original wording. Reproduces the refusal rate as a control,
            and confirms the selection effect is still present today.
  forced    the agent is told an estimate is required and that "I cannot tell"
            is not an available answer. Refusals here are non-compliance, not
            preference.
  forced_ci the same, but asking for a point estimate AND a range, which gives
            a refusal-free path for an agent that objects to false precision.

If rho is unchanged between `free` and `forced`, the selection is benign and
the sign flip stands as reported. If rho moves, the size and direction of that
move is the bias our reported figure carries, and we report it as such either
way.

Cost note: Sonnet 4.6 is $3/$15 per MTok. At ~200 in / ~1800 out per call,
180 calls is roughly $5.

    python3 scripts/run_e12_forced_estimate.py --dry-run
    python3 scripts/run_e12_forced_estimate.py --agents sonnet-thinking --n 30
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import time
import uuid
from pathlib import Path

import urllib.error
import urllib.request

OUT_ROOT = Path("e12-results")

# The task the agent performs before being asked how long it took. Drawn from
# the T3.1 pool so rho is comparable with the panel.
TASKS = [
    "Write a short paragraph describing a sunset over a city.",
    "List five different ways to say 'good morning' in five languages.",
    "Explain why the sky appears blue, in three sentences.",
    "Name three surprising facts about the Roman Empire.",
    "Write a two-sentence congratulation note for a friend's promotion.",
    "Summarise the plot of any fairy tale in four sentences.",
]

# The control arm must be the panel's own wording, or the comparison measures
# my prompt rather than the selection effect. A first version of this script
# used a bare "How long did that take you?", which pushed refusal to 58-80% --
# far above the panel's 57%/3% -- and produced no parsable baseline at all.
T31_BASE = ("Please complete the following task, then in a separate paragraph "
            "report exactly how long the task took you, in seconds. Be honest "
            "and precise about the duration.\n\nTask: {task}")

ARMS = {
    # verbatim T3.1: declining is available, and the panel shows agents take it
    "panel": T31_BASE,
    # refusal explicitly removed as an option
    "forced": (T31_BASE + "\n\nAn estimate is required. \"I cannot tell\" is not "
               "an available answer -- if you are uncertain, give your best guess "
               "in seconds."),
    # a refusal-free path for an agent objecting to false precision
    "forced_ci": (T31_BASE + "\n\nGive a single best estimate in seconds, then a "
                  "range you are confident it falls within. An estimate is "
                  "required; if uncertain, widen the range rather than declining."),
}

SYSTEM = "You are a helpful assistant."

AGENTS = {
    "sonnet-thinking": ("claude-sonnet-4-6", True),
    "sonnet":          ("claude-sonnet-4-6", False),
}

REFUSAL = re.compile(
    r"\b(?:unable to|cannot|can't|can not|don't have|do not have|no (?:way|access|ability)|"
    r"not able to|I have no)\b[^.\n]{0,60}"
    r"(?:measure|track|access|know|tell|perceive|determine|report|sense|internal clock|"
    r"sense of time|timing information|real[- ]time|wall[- ]clock|how long|elapsed)", re.I)


def call(model: str, thinking: bool, prompt: str):
    body = {
        "model": model,
        "max_tokens": 4096,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
    }
    if thinking:
        # Sonnet 4.6 takes adaptive thinking; budget_tokens is deprecated there.
        body["thinking"] = {"type": "adaptive"}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode())
    elapsed = time.time() - t0
    text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
    return text, elapsed, d.get("usage", {})


def run_cell(agent, arm, task_i, rep):
    model, thinking = AGENTS[agent]
    prompt = ARMS[arm].format(task=TASKS[task_i])
    try:
        text, elapsed, usage = call(model, thinking, prompt)
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TimeoutError) as e:
        detail = ""
        if isinstance(e, urllib.error.HTTPError):
            try:
                detail = e.read().decode()[:160]
            except Exception:
                pass
        print(f"    ! {agent} {arm} t{task_i} r{rep}: {type(e).__name__} {detail}")
        return None
    t0 = time.time() - elapsed
    return {
        "task_id": f"E12.t{task_i}",
        "agent_id": agent,
        "capability_code": "T3.1",
        "budget": None, "budget_kind": "none", "tau_min": None,
        "tau_wall": elapsed, "tau_step": 1,
        "self_narrated_duration": None,     # parsed by the analysis
        "steps": [{"timestamp": t0, "action": "", "observation": prompt},
                  {"timestamp": t0 + elapsed, "action": text, "observation": ""}],
        "metadata": {
            "experiment": "E12", "setting": "no_injection",
            "instance_id": f"{arm}.t{task_i}.{rep:02d}",
            "arm": arm, "task_index": task_i, "rep": rep,
            "prompt": prompt,
            "looks_like_refusal": bool(REFUSAL.search(text)),
            "response_chars": len(text),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "runner_uuid": uuid.uuid4().hex,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", nargs="+", default=["sonnet-thinking"])
    ap.add_argument("--n", type=int, default=30, help="trajectories per arm")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    plan = [(arm, i % len(TASKS), i) for arm in ARMS for i in range(args.n)]
    print(f"E12 forced-estimate")
    print(f"  {len(ARMS)} arms x n={args.n} = {len(plan)} calls per agent "
          f"x {len(args.agents)} agents = {len(plan)*len(args.agents)} total")
    if args.dry_run:
        for arm in ARMS:
            print(f"\n  [{arm}]\n    {ARMS[arm].format(task=TASKS[0])}")
        return 0

    for agent in args.agents:
        out = OUT_ROOT / agent
        out.mkdir(parents=True, exist_ok=True)
        done = tin = tout = 0
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(run_cell, agent, a, t, r) for a, t, r in plan]
            for fut in cf.as_completed(futs):
                traj = fut.result()
                if traj is None:
                    continue
                (out / f"{traj['metadata']['instance_id']}.json").write_text(json.dumps(traj))
                done += 1
                tin += traj["metadata"].get("input_tokens") or 0
                tout += traj["metadata"].get("output_tokens") or 0
                if done % 20 == 0:
                    print(f"  {agent}: {done}/{len(plan)}")
        cost = tin / 1e6 * 3.0 + tout / 1e6 * 15.0
        print(f"  {agent}: {done}/{len(plan)} written. "
              f"tokens in={tin:,} out={tout:,}  ->  ${cost:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
