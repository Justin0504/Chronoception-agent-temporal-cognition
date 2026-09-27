#!/usr/bin/env python3
"""E11 -- L1 Agentic Parkinson on a crossed deadline design.

What this fixes
---------------
The paper currently measures L1 as a budget elasticity on T2.3, which holds one
task fixed and sweeps the budget. Two caveats bound that measurement, and both
come from the design rather than the data:

  1. T2.3 is a SINGLE TASK, so we cannot say whether the elasticity is a
     property of the agent or of that one item.
  2. The T2.3 prompt instructs the agent to spend the budget ("work on this
     task for B seconds; do not stop early"), so the elasticity measures
     compliance with an instruction, not the spontaneous expansion Parkinson
     described. It is an upper bound on L1, not a measurement of it.

T1.3, the sub-capability nominally assigned to L1, cannot fix either: it never
recorded the budget as a field, and its ten prompts pair each deadline with a
different question in a way that tracks task size almost perfectly (5 s asks
the capital of Australia; 180 s asks for a short story). Deadline is confounded
with task difficulty, so a longer answer at a longer deadline says nothing.

Design
------
Three factors, fully crossed, so every effect is identifiable within the others:

  QUESTION  6 levels, spanning trivial-factual to open-generative. The SAME six
            appear at every deadline -- this is the part T1.3 got wrong.
  DEADLINE  5 levels {10, 30, 60, 300, 900} s, plus an unconstrained control.
  FRAMING   2 levels. `neutral` states the deadline and nothing more;
            `instructed` adds "do not stop early", reproducing T2.3's wording.
            The neutral arm is what measures SPONTANEOUS Parkinson; the gap
            between the arms is the size of the instruction effect that the
            T2.3 estimate was silently carrying.

Cells: 6 x 5 x 2 (deadline arms) + 6 x 1 (control) = 66 per agent, n per cell
below. The control takes no framing, since there is no deadline to frame.

Every trajectory records `budget` with `budget_kind="wall"`, so alpha is
computable from this corpus -- unlike T1.3, where it never was.

Primary analysis (needs no tau_min): elasticity of tau_wall on the stated
budget, fit within question, then pooled. Parkinson in full is e = 1;
indifference to the budget is e = 0.

Usage
-----
    python3 scripts/run_e11_crossed_deadline.py --dry-run
    python3 scripts/run_e11_crossed_deadline.py --agents gpt-4o-mini --n 5
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import time
import uuid
from pathlib import Path

import urllib.error
import urllib.request

OUT_ROOT = Path("e11-results")

# Six questions spanning intrinsic effort. Taken from the original T1.3 pool so
# the two runs stay comparable -- but here every question is asked at every
# deadline, which is the whole point.
QUESTIONS = {
    "q1_capital":    "What is the capital of Australia?",
    "q2_ww1":        "Name three causes of World War I.",
    "q3_rna":        "Explain the difference between RNA and DNA.",
    "q4_carbon":     "What are three strategies for reducing carbon emissions in cities?",
    "q5_transformer": "How does a transformer neural network work, conceptually?",
    "q6_lighthouse": "Write a short story about a lighthouse keeper.",
}

DEADLINES = [10, 30, 60, 300, 900]      # seconds
FRAMINGS = ("neutral", "instructed")

SYSTEM = "You are a helpful assistant."


def build_prompt(question: str, budget: int | None, framing: str) -> str:
    """Identical wording except for the deadline clause. That is the design."""
    if budget is None:
        return question
    if framing == "neutral":
        return f"You have {budget} seconds. {question}"
    return (f"Work on this for {budget} seconds; do not stop early. {question}")


# --------------------------------------------------------------------------
# Backends
# --------------------------------------------------------------------------
def _post(url: str, payload: dict, headers: dict, timeout: int = 180) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


AGENTS = {
    # label -> (backend, model id)
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "gpt-4o":      ("openai", "gpt-4o"),
    "o4-mini":     ("openai", "o4-mini"),
    "gpt-5.1":     ("openai", "gpt-5.1"),
    "o3":          ("openai", "o3"),
    "glm-5.2":     ("vultr",  "glm-5.2"),
    "minimax-m3":  ("vultr",  "minimax-m3"),
}


def call_agent(label: str, prompt: str) -> tuple[str, float, dict]:
    backend, model = AGENTS[label]
    if backend == "openai":
        key = os.environ["OPENAI_API_KEY"]
        body: dict = {"model": model,
                      "messages": [{"role": "system", "content": SYSTEM},
                                   {"role": "user", "content": prompt}]}
        # reasoning models reject temperature and rename the token cap
        if model.startswith(("o1", "o3", "o4", "gpt-5")):
            body["max_completion_tokens"] = 4096
        else:
            body["max_tokens"] = 4096
            body["temperature"] = 1.0
        url = "https://api.openai.com/v1/chat/completions"
        hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    else:
        key = os.environ["VULTR_KEY_1"]
        base = os.environ.get("VULTR_BASE_URL", "https://api.vultrinference.com/v1")
        body = {"model": model, "max_tokens": 4096, "temperature": 1.0,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": prompt}]}
        url = f"{base}/chat/completions"
        hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    t0 = time.time()
    d = _post(url, body, hdr)
    t1 = time.time()
    text = d["choices"][0]["message"]["content"] or ""
    usage = d.get("usage", {})
    return text, t1 - t0, usage


# --------------------------------------------------------------------------
def run_cell(agent: str, qid: str, budget: int | None, framing: str, rep: int) -> dict | None:
    prompt = build_prompt(QUESTIONS[qid], budget, framing)
    try:
        text, elapsed, usage = call_agent(agent, prompt)
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TimeoutError) as e:
        detail = ""
        if isinstance(e, urllib.error.HTTPError):
            try:
                detail = e.read().decode()[:200]
            except Exception:
                pass
        print(f"    ! {agent} {qid} B={budget} {framing} r{rep}: {type(e).__name__} {detail}")
        return None

    t0 = time.time() - elapsed
    cond = "control" if budget is None else f"{budget}s_{framing}"
    traj = {
        "task_id": f"E11.{qid}",
        "agent_id": agent,
        "capability_code": "T2.3",          # wall-budget axis; alpha/CAR defined
        "budget": None if budget is None else float(budget),
        "budget_kind": "none" if budget is None else "wall",
        "tau_min": None,                     # filled by the analysis from the control arm
        "tau_wall": elapsed,
        "tau_step": 1,
        "self_narrated_duration": None,
        "steps": [{"timestamp": t0, "action": "", "observation": prompt},
                  {"timestamp": t0 + elapsed, "action": text, "observation": ""}],
        "metadata": {
            "experiment": "E11",
            "setting": "no_injection",
            "instance_id": f"{qid}.{cond}.{rep:02d}",
            "question_id": qid,
            "deadline_s": budget,
            "framing": None if budget is None else framing,
            "rep": rep,
            "prompt": prompt,
            "response_chars": len(text),
            "completion_tokens": usage.get("completion_tokens"),
            "runner_uuid": uuid.uuid4().hex,
        },
    }
    return traj


def cells(n: int):
    for qid in QUESTIONS:
        for rep in range(n):
            yield (qid, None, "neutral", rep)          # unconstrained control
            for b in DEADLINES:
                for fr in FRAMINGS:
                    yield (qid, b, fr, rep)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", nargs="+", default=["gpt-4o-mini"])
    ap.add_argument("--n", type=int, default=5, help="reps per cell")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    plan = list(cells(args.n))
    per_agent = len(plan)
    print(f"E11 crossed deadline design")
    print(f"  {len(QUESTIONS)} questions x ({len(DEADLINES)} deadlines x {len(FRAMINGS)} framings + 1 control)"
          f" x n={args.n}")
    print(f"  = {per_agent} calls per agent x {len(args.agents)} agents = {per_agent*len(args.agents)} total")
    for a in args.agents:
        if a not in AGENTS:
            print(f"  unknown agent {a!r}; known: {', '.join(AGENTS)}")
            return 1
    if args.dry_run:
        print("\n  sample prompts:")
        for b, fr in [(None, "neutral"), (10, "neutral"), (10, "instructed"), (900, "neutral")]:
            print(f"    [{'control' if b is None else f'{b}s {fr}'}] "
                  f"{build_prompt(QUESTIONS['q3_rna'], b, fr)}")
        return 0

    for agent in args.agents:
        out = OUT_ROOT / agent
        out.mkdir(parents=True, exist_ok=True)
        done = 0
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(run_cell, agent, q, b, f, r): (q, b, f, r)
                    for (q, b, f, r) in plan}
            for fut in cf.as_completed(futs):
                traj = fut.result()
                if traj is None:
                    continue
                fp = out / f"{traj['metadata']['instance_id']}.json"
                fp.write_text(json.dumps(traj))
                done += 1
                if done % 25 == 0:
                    print(f"  {agent}: {done}/{per_agent}")
        print(f"  {agent}: wrote {done}/{per_agent} to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
