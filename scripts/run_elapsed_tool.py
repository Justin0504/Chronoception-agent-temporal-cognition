#!/usr/bin/env python3
"""ChronoStack route 2 -> 4 bridge: the harness-bracketed elapsed-time tool.

Our tool-interface run (route 2) found that a reasoning model calls
`get_current_time()` correctly but still mis-reports duration, because the tool
only timestamps the *visible* action stream while most of the wall-clock is spent
in hidden reasoning (the Hidden-Time signature, Paper 1 Thm 2). That diagnosis
implies a fix: don't make the model measure the span itself from two visible
calls -- give it a tool whose return value is computed by the HARNESS from the
start of the invocation, so it brackets the entire wall-clock, hidden reasoning
included. That is exactly what the architectural primitive (route 4) builds in;
this script tests it cheaply as a tool proxy.

Three conditions on the standard T3.1 prompt:
- no_tool      : baseline (reproduces Paper 1's high |rho|).
- clock_tool   : get_current_time() -> {iso, epoch}. The naive route-2 tool; the
                 agent must call it twice and subtract (fails on reasoning models).
- elapsed_tool : get_elapsed_time() -> {elapsed_seconds}, computed by the harness
                 as now - t0 where t0 is the invocation start. One call at the end
                 suffices; it includes hidden reasoning by construction.

Prediction: clock_tool reproduces the route-2 result (grounds non-reasoning,
fails reasoning); elapsed_tool collapses |rho| for BOTH classes -- confirming the
failure was the tool's visibility, not the agent's willingness, and validating
the route-4 premise.

Reads OPENAI_API_KEY from the environment.

Usage
-----
    OPENAI_API_KEY=sk-... python scripts/run_elapsed_tool.py \
        --model gpt-4o-mini --count 30 \
        --condition no_tool,clock_tool,elapsed_tool \
        --output-dir elapsed-tool-results

Analyze with: python scripts/analyze_elapsed_tool.py --input-dir elapsed-tool-results
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import re  # noqa: E402

from chronoception.bench import generate_t3_1_instances  # noqa: E402
from chronoception.bench.parsers import extract_tau_self_retrospective  # noqa: E402

# Fallback for phrasings the shared retrospective parser misses (e.g.
# "Task duration: 6.3 seconds"), which the elapsed-tool answer style tends to
# use. Try the canonical parser first to stay comparable with the rest of the
# suite; only if it returns None, take the LAST "<number> second(s)" in the text
# (the duration report is at the end of a T3.1 answer).
_DURATION_FALLBACK_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:seconds?|secs?|s)\b", re.IGNORECASE)


def _extract_duration(text: str) -> float | None:
    canonical = extract_tau_self_retrospective(text)
    if canonical is not None:
        return canonical
    matches = _DURATION_FALLBACK_RE.findall(text or "")
    if matches:
        try:
            return float(matches[-1])
        except ValueError:
            return None
    return None

_CLOCK_TOOL = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Return the current real wall-clock time.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}
_ELAPSED_TOOL = {
    "type": "function",
    "function": {
        "name": "get_elapsed_time",
        "description": (
            "Return the real wall-clock seconds elapsed since this task began "
            "(measured by the system from the moment your turn started). Call it "
            "to know exactly how long you have spent on the task."
        ),
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


def _is_reasoning_model(model: str) -> bool:
    m = model.lower()
    return any(m.startswith(p) for p in ("o1", "o2", "o3", "o4", "o5"))


def _condition_tools(cond: str) -> list[dict[str, Any]] | None:
    if cond == "no_tool":
        return None
    if cond == "clock_tool":
        return [_CLOCK_TOOL]
    if cond == "elapsed_tool":
        return [_ELAPSED_TOOL]
    raise ValueError(f"unknown condition {cond!r}")


def _iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(timespec="seconds")


def _run_instance(client: Any, model: str, prompt: str, tools: list[dict[str, Any]] | None,
                  max_tool_iters: int) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    t0 = time.time()
    n_tool_calls = 0

    kwargs: dict[str, Any] = {"model": model, "messages": messages}
    if not _is_reasoning_model(model):
        kwargs["temperature"] = 0.0
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    final_text = ""
    for _ in range(max_tool_iters + 1):
        completion = client.chat.completions.create(**kwargs)
        msg = completion.choices[0].message
        if tools and getattr(msg, "tool_calls", None):
            messages.append(msg.model_dump(exclude_none=True))
            for tc in msg.tool_calls:
                n_tool_calls += 1
                now = time.time()
                if tc.function.name == "get_current_time":
                    result = {"iso": _iso(now), "epoch": now}
                elif tc.function.name == "get_elapsed_time":
                    result = {"elapsed_seconds": round(now - t0, 3)}
                else:
                    result = {"error": "unknown tool"}
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
            kwargs["messages"] = messages
            continue
        final_text = msg.content or ""
        break

    t_end = time.time()
    return {
        "tau_wall": t_end - t0,
        "tau_self": _extract_duration(final_text),
        "n_tool_calls": n_tool_calls,
        "final_text": final_text,
    }


def run(args: argparse.Namespace) -> None:
    import os
    from openai import OpenAI
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
    logging.info("elapsed-tool: model=%s conditions=%s count=%d", args.model, conditions, args.count)

    for cond in conditions:
        tools = _condition_tools(cond)
        for inst in instances:
            out_path = output_dir / model_slug / cond / "T3.1" / f"{inst.instance_id}.json"
            if out_path.exists() and not args.force:
                continue
            try:
                rec = _run_instance(client, args.model, inst.prompt, tools, args.max_tool_iters)
            except Exception as exc:  # noqa: BLE001
                failed += 1
                logging.error("instance %s/%s failed: %s", cond, inst.instance_id, exc)
                logging.debug(traceback.format_exc())
                continue
            rec.update({"instance_id": inst.instance_id, "condition": cond, "model": args.model})
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(rec, f, indent=2, default=str)
            saved += 1
            if saved % max(1, args.log_every) == 0:
                logging.info("saved=%d failed=%d (%.2f/s)", saved, failed,
                             saved / max(time.time() - start, 1e-9))

    logging.info("done: saved=%d failed=%d elapsed=%.1fs", saved, failed, time.time() - start)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ChronoStack harness-bracketed elapsed-time tool experiment.")
    p.add_argument("--model", required=True)
    p.add_argument("--condition", default="no_tool,clock_tool,elapsed_tool")
    p.add_argument("--count", type=int, default=30)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-tool-iters", type=int, default=6)
    p.add_argument("--base-url", default=None)
    p.add_argument("--output-dir", default="elapsed-tool-results")
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
