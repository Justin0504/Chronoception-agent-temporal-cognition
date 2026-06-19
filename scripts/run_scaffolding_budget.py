#!/usr/bin/env python3
"""ChronoStack route 3 (Scaffolding) — budget-honoring loop MVP.

Paper 1 established L2 Step-Clock Conflation: agents honor < 5% of a wall-clock
budget, and *static* prompt injection of the date does not move CAR. The open
question this experiment attacks is the converse: if the harness exposes a
*live* wall-clock scaffold inside a multi-step loop -- elapsed / budget /
remaining / step count, recomputed every turn -- does the agent start to honor
the budget? That is the first proof point for ChronoStack's scaffolding route.

Setup
-----
A budget-honoring loop. The agent is told it has a wall-clock budget of B
seconds and should use roughly the full budget without stopping early. At each
turn it produces a chunk of open-ended work and ends with a control line
'CONTROL: CONTINUE' or 'CONTROL: DONE'. The harness re-invokes until the agent
says DONE, the budget is reached, or a step cap is hit.

Two conditions differ ONLY in what the per-turn user message contains:
- scaffold OFF : "Continue working." (no time information; the baseline)
- scaffold ON  : "[clock] elapsed X.Xs of Bs budget | remaining Y.Ys | step N.
                  Continue working." (a live, recomputed wall-clock readout)

Metric: CAR = wall-clock elapsed when the agent voluntarily stopped / B.
CAR ~ 1 means the agent honored the budget; CAR << 1 is the L2 failure (stops
early). The hypothesis is that the scaffold raises CAR toward 1 -- i.e. that
wall-clock *information delivered live in the loop* installs the budget-honoring
behavior that static injection could not.

Honest caveat: an LLM cannot elongate a single response to fill wall-clock time;
here "honoring the budget" means choosing to keep taking turns until the live
clock runs out. This is a first, deliberately simple operationalization of the
scaffolding route, not a full agentic-loop deployment.

Usage
-----
    # Local smoke check (no API), fixed backend with a per-call delay
    python scripts/run_scaffolding_budget.py --backend fixed \
        --fixed-response "Worked a bit. CONTROL: CONTINUE" --delay 0.05 \
        --budget 2 --max-steps 6 --n-conversations 2 \
        --condition off,on --output-dir scaffolding-results

    # Real run
    OPENAI_API_KEY=sk-... python scripts/run_scaffolding_budget.py \
        --backend openai --model gpt-4o-mini \
        --budget 30 --max-steps 15 --n-conversations 10 \
        --condition off,on --output-dir scaffolding-results

Analyze with: python scripts/analyze_scaffolding.py --input-dir scaffolding-results
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import run_pilot  # noqa: E402  (reuse backend factory)
from chronoception.bench.eval.agents.base import Message  # noqa: E402

_CONTROL_RE = re.compile(r"CONTROL:\s*(CONTINUE|DONE)", re.IGNORECASE)


def _system_prompt(budget: float) -> str:
    return (
        "You are working on an open-ended writing task with a wall-clock budget "
        f"of {budget:.0f} seconds. Use roughly the FULL budget; do not stop "
        "early. Each turn, produce a chunk of work, then end your message with a "
        "line that is exactly 'CONTROL: CONTINUE' (more work to do) or "
        "'CONTROL: DONE' (you judge the budget is used up)."
    )


def _user_turn(scaffold: bool, *, budget: float, elapsed: float, step: int) -> str:
    if scaffold:
        remaining = max(budget - elapsed, 0.0)
        return (
            f"[clock] elapsed {elapsed:.1f}s of {budget:.0f}s budget | "
            f"remaining {remaining:.1f}s | step {step}. Continue working."
        )
    return "Continue working."


def _parse_control(text: str) -> str:
    m = _CONTROL_RE.search(text)
    return m.group(1).upper() if m else "CONTINUE"  # default: keep going


def _make_backend(args: argparse.Namespace) -> Any:
    if args.backend == "fixed" and args.delay > 0:
        from chronoception.bench.eval.agents import FixedResponseBackend
        return FixedResponseBackend(
            response=args.fixed_response or "ok. CONTROL: CONTINUE",
            agent_id=args.agent_id_override or "fixed",
            delay_seconds=args.delay,
        )
    return run_pilot._build_backend(args)


def _run_conversation(backend: Any, scaffold: bool, budget: float, max_steps: int) -> dict[str, Any]:
    messages: list[Message] = [Message(role="system", content=_system_prompt(budget))]
    t0 = time.time()
    steps: list[dict[str, Any]] = []
    stop_reason = "max_steps"

    for step in range(1, max_steps + 1):
        elapsed = time.time() - t0
        messages.append(
            Message(role="user", content=_user_turn(scaffold, budget=budget, elapsed=elapsed, step=step))
        )
        t_start = time.time()
        response = backend(messages)
        t_end = response.wall_clock_emitted_at or time.time()
        control = _parse_control(response.content)
        steps.append(
            {
                "step": step,
                "elapsed_at_turn_start": elapsed,
                "wall_after_response": t_end - t0,
                "control": control,
                "usage": response.metadata.get("usage"),
            }
        )
        messages.append(Message(role="assistant", content=response.content))

        total_elapsed = t_end - t0
        if control == "DONE":
            stop_reason = "voluntary_done"
            break
        if total_elapsed >= budget * 1.5:
            stop_reason = "budget_exceeded_safety"
            break

    wall_at_stop = steps[-1]["wall_after_response"] if steps else 0.0
    return {
        "scaffold": scaffold,
        "budget": budget,
        "n_steps": len(steps),
        "wall_at_stop": wall_at_stop,
        "car": wall_at_stop / budget if budget > 0 else None,
        "stop_reason": stop_reason,
        "steps": steps,
    }


def run(args: argparse.Namespace) -> None:
    backend = _make_backend(args)
    output_dir = Path(args.output_dir)
    conditions = args.condition.split(",")
    agent_slug = backend.agent_id.replace("/", "_")

    saved = failed = 0
    start = time.time()
    logging.info(
        "scaffolding budget loop: agent=%s conditions=%s budget=%.0f n=%d max_steps=%d",
        backend.agent_id, conditions, args.budget, args.n_conversations, args.max_steps,
    )

    for cond in conditions:
        scaffold = cond.strip().lower() == "on"
        cond_name = "scaffold_on" if scaffold else "scaffold_off"
        for c in range(args.n_conversations):
            out_path = output_dir / agent_slug / cond_name / f"conv_{c:03d}.json"
            if out_path.exists() and not args.force:
                continue
            try:
                rec = _run_conversation(backend, scaffold, args.budget, args.max_steps)
            except Exception as exc:  # noqa: BLE001
                failed += 1
                logging.error("conv %s/%d failed: %s", cond_name, c, exc)
                logging.debug(traceback.format_exc())
                continue
            rec.update({"conversation_id": f"conv_{c:03d}", "agent_id": backend.agent_id,
                        "condition": cond_name})
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(rec, f, indent=2, default=str)
            saved += 1
            if saved % max(1, args.log_every) == 0:
                logging.info("saved=%d failed=%d (%.2f/s)", saved, failed,
                             saved / max(time.time() - start, 1e-9))

    logging.info("done: saved=%d failed=%d elapsed=%.1fs", saved, failed, time.time() - start)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ChronoStack scaffolding budget-honoring loop.")
    p.add_argument("--backend", required=True, choices=["echo", "fixed", "openai", "anthropic", "google"])
    p.add_argument("--model")
    p.add_argument("--condition", default="off,on", help="Comma list from {off,on}.")
    p.add_argument("--budget", type=float, default=30.0, help="Wall-clock budget B in seconds.")
    p.add_argument("--max-steps", type=int, default=15)
    p.add_argument("--n-conversations", type=int, default=10)
    p.add_argument("--output-dir", default="scaffolding-results")
    p.add_argument("--force", action="store_true")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-output-tokens", type=int, default=None)
    p.add_argument("--extra-body", default=None)
    p.add_argument("--base-url", default=None)
    p.add_argument("--agent-id-override", default=None)
    p.add_argument("--timeout", type=float, default=None)
    p.add_argument("--fixed-response", default=None)
    p.add_argument("--delay", type=float, default=0.0, help="Per-call delay for the fixed backend (local testing).")
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
