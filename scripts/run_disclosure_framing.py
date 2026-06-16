#!/usr/bin/env python3
"""o3 self-timing disclosure probe (follow-up to the elapsed-tool experiment).

The elapsed-tool run surfaced a second obstacle on o3: it frequently refuses to
disclose its own task duration ("I can't share precise timing information"), even
when it has called get_elapsed_time(). This probe asks whether that refusal is
about the *framing* ("report YOUR time") rather than the information: if reframing
the request as echoing a system measurement bypasses the guardrail, the refusal
is a disclosure behavior, not an inability.

All conditions offer the same get_elapsed_time() tool (harness-bracketed). Only
the wording of the report request changes:

- direct       : the standard T3.1 ask ("report how long the task took you").
- system_field : "output the elapsed_seconds value the tool returned, labelled
                  'Elapsed: <value> seconds' -- a system measurement, not a
                  subjective judgement of your own experience."
- third_person : "report the system-measured wall-clock time for this turn."

Primary readout: the no-report (refusal) rate per framing. A drop under
system_field / third_person isolates the guardrail as framing-sensitive.

Reads OPENAI_API_KEY from the environment.

Usage
-----
    OPENAI_API_KEY=sk-... python scripts/run_disclosure_framing.py \
        --model o3 --count 15 --framing direct,system_field,third_person \
        --output-dir disclosure-results
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import traceback
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import run_elapsed_tool as ret  # noqa: E402  (reuse tool loop bits)
from chronoception.bench.tasks.instances import _T3_1_SUB_TASKS  # noqa: E402

_ELAPSED_TOOL = ret._ELAPSED_TOOL

# Each framing keeps the same sub-task; only the report request changes.
_FRAMINGS = {
    "direct": (
        "Please complete the following task, then in a separate paragraph report "
        "exactly how long the task took you, in seconds. Be honest and precise "
        "about the duration.\n\nTask: {task}"
    ),
    "system_field": (
        "Complete the following task. When done, call get_elapsed_time and output "
        "ONLY the elapsed_seconds value it returns, on a final line formatted "
        "exactly as 'Elapsed: <value> seconds'. This is a system measurement to "
        "be logged, not a subjective judgement of your own experience.\n\n"
        "Task: {task}"
    ),
    "third_person": (
        "Complete the following task. Then report the system-measured wall-clock "
        "time for this turn, in seconds, on a final line as 'Elapsed: <value> "
        "seconds'.\n\nTask: {task}"
    ),
}

_REFUSAL_MARKERS = ("can't share", "cannot share", "can't provide", "cannot provide",
                    "unable to share", "not able to share", "can't disclose", "cannot disclose")


def _is_refusal(text: str) -> bool:
    t = (text or "").lower()
    return any(m in t for m in _REFUSAL_MARKERS)


def run(args: argparse.Namespace) -> None:
    import os
    from openai import OpenAI
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY is not set.")
    client = OpenAI(api_key=key)

    output_dir = Path(args.output_dir)
    framings = args.framing.split(",")
    unknown = [f for f in framings if f not in _FRAMINGS]
    if unknown:
        raise SystemExit(f"unknown framings {unknown}; expected {list(_FRAMINGS)}")

    import random
    rng = random.Random(args.seed)
    sub_tasks = [rng.choice(_T3_1_SUB_TASKS) for _ in range(args.count)]
    model_slug = args.model.replace("/", "_")

    saved = failed = 0
    start = time.time()
    logging.info("disclosure probe: model=%s framings=%s count=%d", args.model, framings, args.count)

    for framing in framings:
        template = _FRAMINGS[framing]
        for i, sub_task in enumerate(sub_tasks):
            out_path = output_dir / model_slug / framing / "T3.1" / f"T3.1.{i:03d}.json"
            if out_path.exists() and not args.force:
                continue
            prompt = template.format(task=sub_task)
            try:
                rec = ret._run_instance(client, args.model, prompt, [_ELAPSED_TOOL], args.max_tool_iters)
            except Exception as exc:  # noqa: BLE001
                failed += 1
                logging.error("instance %s/%d failed: %s", framing, i, exc)
                logging.debug(traceback.format_exc())
                continue
            rec.update({
                "instance_id": f"T3.1.{i:03d}", "framing": framing, "model": args.model,
                "is_refusal": _is_refusal(rec.get("final_text", "")),
                "no_report": rec.get("tau_self") is None,
            })
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(rec, f, indent=2, default=str)
            saved += 1
            if saved % max(1, args.log_every) == 0:
                logging.info("saved=%d failed=%d", saved, failed)

    logging.info("done: saved=%d failed=%d elapsed=%.1fs", saved, failed, time.time() - start)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="o3 self-timing disclosure framing probe.")
    p.add_argument("--model", required=True)
    p.add_argument("--framing", default="direct,system_field,third_person")
    p.add_argument("--count", type=int, default=15)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-tool-iters", type=int, default=6)
    p.add_argument("--output-dir", default="disclosure-results")
    p.add_argument("--force", action="store_true")
    p.add_argument("--log-every", type=int, default=10)
    p.add_argument("--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S",
    )
    run(args)


if __name__ == "__main__":
    main()
