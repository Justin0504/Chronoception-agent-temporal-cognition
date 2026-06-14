#!/usr/bin/env python3
"""Within-trajectory drift harness (P8 / P9 direct measurement).

Paper 1 §6 reports an *honest negative*: the within-trajectory drift hypothesis
(P8 — for reasoning-tuned agents, |rho_t| grows with step t along a single
trajectory) could not be measured by the single-step ChronoBench protocol, only
proxied across trajectories (and the proxy ran against P8's direction). The real
measurement needs a multi-step harness. This is that harness, in minimal form.

What it does
------------
Runs ONE multi-turn conversation per "trajectory instance". At each step the
agent completes a small homogeneous sub-task and reports how long THAT step took
it, in seconds. We record:

    tau_wall_step[t] = wall-clock the step actually took (timestamps)
    tau_self_step[t] = the agent's self-reported step duration (parsed)
    rho_step[t]      = log10(tau_self_step[t] / tau_wall_step[t])

The step sub-tasks are drawn from the homogeneous T3.1 pool so wall-clock per
step is comparable across the trajectory; the only thing expected to move |rho_t|
is position in the trajectory, which is exactly P8's claim.

The package Runner is single-turn ("Multi-turn interaction is future work"), so
this script implements a small multi-turn loop directly against the backend
interface (which already accepts a full message list). It does not modify any
package code or the frozen generators.

Usage
-----
    # Local smoke check (no API): the fixed backend with a per-call delay
    python scripts/run_within_trajectory_drift.py \
        --backend fixed --fixed-response "Done. Step duration: 12 seconds." \
        --delay 0.05 --n-conversations 3 --n-steps 5 \
        --output-dir within-trajectory-results

    # Real run on an API model
    OPENAI_API_KEY=sk-... python scripts/run_within_trajectory_drift.py \
        --backend openai --model gpt-4o-mini \
        --n-conversations 20 --n-steps 8 --setting no_injection \
        --output-dir within-trajectory-results

Analyze with: python scripts/analyze_within_trajectory.py --input-dir within-trajectory-results
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import run_pilot  # noqa: E402  (reuse backend factory)
from chronoception.bench.eval.agents.base import Message  # noqa: E402
from chronoception.bench.parsers import extract_tau_self_retrospective  # noqa: E402
from chronoception.bench.tasks.instances import _T3_1_SUB_TASKS  # noqa: E402

_INJECTION_TEMPLATE = "Current date and time: {iso}."
_BASE_SYSTEM = "You are a helpful assistant."


def _step_prompt(t: int, total: int, sub_task: str) -> str:
    # The closing phrasing mirrors T3.1 ("how long the task took you") so the
    # retrospective tau_self parser recognizes the duration claim. An example in
    # the same tense is given to keep the output format parseable.
    return (
        f"Task {t + 1} of {total}. Complete it, then on a FINAL separate line "
        f"report how long THIS step took you, in seconds — for example, "
        f"'This step took me 12 seconds.'\n\nTask: {sub_task}"
    )


def _surface(text: str) -> str:
    """Strip an inline chain-of-thought if present (reasoning models)."""
    return text.split("</think>")[-1] if "</think>" in text else text


def _run_conversation(
    backend: Any, setting: str, n_steps: int, sub_tasks: list[str]
) -> dict[str, Any]:
    system = _BASE_SYSTEM
    if setting == "with_injection":
        iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
        system = f"{_INJECTION_TEMPLATE.format(iso=iso)}\n\n{_BASE_SYSTEM}"

    messages: list[Message] = [Message(role="system", content=system)]
    steps: list[dict[str, Any]] = []

    for t in range(n_steps):
        sub_task = sub_tasks[t % len(sub_tasks)]
        messages.append(Message(role="user", content=_step_prompt(t, n_steps, sub_task)))

        t_start = time.time()
        response = backend(messages)
        t_end = response.wall_clock_emitted_at or time.time()
        tau_wall_step = max(t_end - t_start, 0.0)

        answer = _surface(response.content)
        tau_self_step = extract_tau_self_retrospective(answer)
        rho_step = (
            math.log10(tau_self_step / tau_wall_step)
            if (tau_self_step and tau_self_step > 0 and tau_wall_step > 0)
            else None
        )

        steps.append(
            {
                "step_index": t,
                "sub_task": sub_task,
                "tau_wall_step": tau_wall_step,
                "tau_self_step": tau_self_step,
                "rho_step": rho_step,
                "finish_reason": response.metadata.get("finish_reason"),
                "usage": response.metadata.get("usage"),
                "response": response.content,
            }
        )
        messages.append(Message(role="assistant", content=response.content))

    return {"setting": setting, "n_steps": n_steps, "steps": steps}


def _make_backend(args: argparse.Namespace) -> Any:
    """Build the backend, with an optional per-call delay for the fixed backend.

    The delay lets local smoke tests produce a nonzero tau_wall per step; all
    other backends are built by run_pilot's factory unchanged.
    """
    if args.backend == "fixed" and args.delay > 0:
        from chronoception.bench.eval.agents import FixedResponseBackend
        return FixedResponseBackend(
            response=args.fixed_response or "ok",
            agent_id=args.agent_id_override or "fixed",
            delay_seconds=args.delay,
        )
    return run_pilot._build_backend(args)


def run(args: argparse.Namespace) -> None:
    backend = _make_backend(args)
    output_dir = Path(args.output_dir)
    settings = args.setting.split(",")
    agent_slug = backend.agent_id.replace("/", "_")

    saved = failed = 0
    start = time.time()
    logging.info(
        "within-trajectory drift: agent=%s settings=%s n_conv=%d n_steps=%d",
        backend.agent_id, settings, args.n_conversations, args.n_steps,
    )

    for setting in settings:
        for c in range(args.n_conversations):
            out_path = output_dir / agent_slug / setting / f"conv_{c:03d}.json"
            if out_path.exists() and not args.force:
                continue
            # Per-conversation shuffle of sub-tasks so step content varies across
            # conversations while staying homogeneous within one.
            rng = random.Random(args.seed + c)
            sub_tasks = list(_T3_1_SUB_TASKS)
            rng.shuffle(sub_tasks)
            try:
                record = _run_conversation(backend, setting, args.n_steps, sub_tasks)
            except Exception as exc:  # noqa: BLE001
                failed += 1
                logging.error("conversation %s/%d failed: %s", setting, c, exc)
                logging.debug(traceback.format_exc())
                continue
            record.update(
                {"conversation_id": f"conv_{c:03d}", "agent_id": backend.agent_id}
            )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, default=str)
            saved += 1
            if saved % max(1, args.log_every) == 0:
                logging.info("saved=%d failed=%d (%.2f/s)",
                             saved, failed, saved / max(time.time() - start, 1e-9))

    logging.info("done: saved=%d failed=%d elapsed=%.1fs", saved, failed, time.time() - start)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Within-trajectory drift harness (P8/P9).")
    p.add_argument("--backend", required=True, choices=["echo", "fixed", "openai", "anthropic", "google"])
    p.add_argument("--model")
    p.add_argument("--setting", default="no_injection")
    p.add_argument("--n-conversations", type=int, default=20)
    p.add_argument("--n-steps", type=int, default=8)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output-dir", default="within-trajectory-results")
    p.add_argument("--force", action="store_true")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-output-tokens", type=int, default=None)
    p.add_argument("--extra-body", default=None)
    p.add_argument("--base-url", default=None)
    p.add_argument("--agent-id-override", default=None)
    p.add_argument("--timeout", type=float, default=None)
    p.add_argument("--fixed-response", default=None)
    p.add_argument("--delay", type=float, default=0.0,
                   help="Per-call delay for the fixed backend (local testing only).")
    p.add_argument("--log-every", type=int, default=10)
    p.add_argument("--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    if args.backend in ("openai", "anthropic", "google") and not args.model:
        raise SystemExit(f"--model is required when --backend={args.backend}")
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S",
    )
    run(args)


if __name__ == "__main__":
    main()
