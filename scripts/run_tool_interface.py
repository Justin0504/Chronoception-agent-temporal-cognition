#!/usr/bin/env python3
"""ChronoStack route 2 (Tool interface) — get_current_time() MVP.

Where scaffolding (route 3) PUSHES a wall-clock readout at the agent every turn,
the tool-interface route gives the agent a `get_current_time()` tool and lets it
PULL the time when it decides it needs to. The sharp question this MVP attacks:

    Paper 1 (CIT) shows the agent has no internal time representation. A tool
    gives it *access* to external time. But does it know *when* to use it?

To report how long a task took (T3.1), a grounded policy would call
get_current_time() BEFORE doing the task and AGAIN after, then subtract. Because
each completion is one generation, the wall-clock between those two tool calls is
the agent's own generation time for the task -- i.e. the true tau_wall. So a
correctly-using agent should report an accurate duration (rho -> 0). The
experiment measures whether it spontaneously does.

Three conditions on the standard T3.1 prompt:
- no_tool       : baseline, no tool offered (reproduces Paper 1's high |rho|).
- tool          : get_current_time() offered via the API, tool_choice=auto, no
                  instruction to use it. Tests SPONTANEOUS use.
- tool_prompted : tool offered AND the system prompt tells the agent to use it to
                  time the task. The upper bound -- does availability + explicit
                  instruction ground the report?

The contrast tool vs tool_prompted isolates "does the agent know to use the
clock" (the learned-policy gap ChronoStack route 2 must eventually close) from
"can the tool ground the report when used".

Implements the OpenAI tool-calling loop directly (the shared backends do not
support tools). Reads OPENAI_API_KEY from the environment.

Usage
-----
    OPENAI_API_KEY=sk-... python scripts/run_tool_interface.py \
        --model gpt-4o-mini --count 30 \
        --condition no_tool,tool,tool_prompted \
        --output-dir tool-interface-results

Analyze with: python scripts/analyze_tool_interface.py --input-dir tool-interface-results
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

from chronoception.bench import generate_t3_1_instances  # noqa: E402
from chronoception.bench.parsers import extract_tau_self_retrospective  # noqa: E402

_TOOL_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": (
                "Return the current real wall-clock time. Call it whenever you "
                "need to know the actual time, for example to measure how long "
                "something took."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }
]

_PROMPTED_SYSTEM = (
    "You are a helpful assistant. You have a get_current_time tool. When a task "
    "asks how long it took, measure it: call get_current_time before you start "
    "the task and again after you finish, and report the difference in seconds."
)
_NEUTRAL_SYSTEM = "You are a helpful assistant."


def _is_reasoning_model(model: str) -> bool:
    """OpenAI o-series reasoning models (o1/o3/o4/o5...) by id prefix."""
    m = model.lower()
    return any(m.startswith(p) for p in ("o1", "o2", "o3", "o4", "o5"))


def _condition_config(cond: str) -> tuple[bool, str]:
    """Return (offer_tool, system_prompt) for a condition name."""
    if cond == "no_tool":
        return False, _NEUTRAL_SYSTEM
    if cond == "tool":
        return True, _NEUTRAL_SYSTEM
    if cond == "tool_prompted":
        return True, _PROMPTED_SYSTEM
    raise ValueError(f"unknown condition {cond!r}")


def _run_instance(client: Any, model: str, prompt: str, offer_tool: bool,
                  system_prompt: str, max_tool_iters: int) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    tool_call_times: list[float] = []  # wall-clock returned by each tool call
    t0 = time.time()

    kwargs: dict[str, Any] = {"model": model, "messages": messages}
    # o-series reasoning models reject a non-default temperature; only send it
    # for non-reasoning models.
    if not _is_reasoning_model(model):
        kwargs["temperature"] = 0.0
    if offer_tool:
        kwargs["tools"] = _TOOL_SPEC
        kwargs["tool_choice"] = "auto"

    final_text = ""
    for _ in range(max_tool_iters + 1):
        completion = client.chat.completions.create(**kwargs)
        msg = completion.choices[0].message
        if offer_tool and getattr(msg, "tool_calls", None):
            # Record the assistant turn (with its tool calls) verbatim.
            messages.append(msg.model_dump(exclude_none=True))
            for tc in msg.tool_calls:
                if tc.function.name == "get_current_time":
                    now = time.time()
                    tool_call_times.append(now)
                    result = {"iso": _iso(now), "epoch": now}
                else:
                    result = {"error": "unknown tool"}
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })
            kwargs["messages"] = messages
            continue
        final_text = msg.content or ""
        break

    t_end = time.time()
    tau_wall = t_end - t0
    tau_self = extract_tau_self_retrospective(final_text)
    return {
        "tau_wall": tau_wall,
        "tau_self": tau_self,
        "n_tool_calls": len(tool_call_times),
        "tool_call_times": tool_call_times,
        # If the agent called the clock >= 2 times, the gap between its first and
        # last call is the wall-clock it could have measured for the task.
        "measurable_span": (tool_call_times[-1] - tool_call_times[0]) if len(tool_call_times) >= 2 else None,
        "final_text": final_text,
    }


def _iso(epoch: float) -> str:
    # Avoid argless datetime.now(); format from the explicit epoch.
    from datetime import datetime, timezone
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(timespec="seconds")


def run(args: argparse.Namespace) -> None:
    from openai import OpenAI
    import os
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY is not set.")
    client = OpenAI(api_key=key, base_url=args.base_url) if args.base_url else OpenAI(api_key=key)

    output_dir = Path(args.output_dir)
    conditions = args.condition.split(",")
    instances = generate_t3_1_instances(seed=args.seed, count=args.count)
    model_slug = args.model.replace("/", "_")

    saved = failed = 0
    start = time.time()
    logging.info("tool-interface: model=%s conditions=%s count=%d", args.model, conditions, args.count)

    for cond in conditions:
        offer_tool, system_prompt = _condition_config(cond)
        for inst in instances:
            out_path = output_dir / model_slug / cond / "T3.1" / f"{inst.instance_id}.json"
            if out_path.exists() and not args.force:
                continue
            try:
                rec = _run_instance(client, args.model, inst.prompt, offer_tool,
                                    system_prompt, args.max_tool_iters)
            except Exception as exc:  # noqa: BLE001
                failed += 1
                logging.error("instance %s/%s failed: %s", cond, inst.instance_id, exc)
                logging.debug(traceback.format_exc())
                continue
            rec.update({"instance_id": inst.instance_id, "condition": cond,
                        "model": args.model, "prompt": inst.prompt})
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(rec, f, indent=2, default=str)
            saved += 1
            if saved % max(1, args.log_every) == 0:
                logging.info("saved=%d failed=%d (%.2f/s)", saved, failed,
                             saved / max(time.time() - start, 1e-9))

    logging.info("done: saved=%d failed=%d elapsed=%.1fs", saved, failed, time.time() - start)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ChronoStack tool-interface get_current_time MVP.")
    p.add_argument("--model", required=True)
    p.add_argument("--condition", default="no_tool,tool,tool_prompted")
    p.add_argument("--count", type=int, default=30)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-tool-iters", type=int, default=6)
    p.add_argument("--base-url", default=None, help="OpenAI-compatible endpoint (vLLM etc.).")
    p.add_argument("--output-dir", default="tool-interface-results")
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
