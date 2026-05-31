#!/usr/bin/env python3
"""Pilot runner CLI for ChronoBench Phase 2.

Iterates a slice of the (model x capability x setting x instance) grid,
sends each TaskInstance through the runner, parses tau_self where
applicable, and saves each Trajectory as JSON under an output directory.

Usage examples
--------------

Echo smoke check (no API key required):

    python scripts/run_pilot.py \
        --backend echo \
        --capability T3.1 \
        --setting no_injection \
        --count 5 \
        --output-dir pilot-results/

GPT-4o pilot on T1.1, Setting B (with-injection):

    OPENAI_API_KEY=sk-... python scripts/run_pilot.py \
        --backend openai \
        --model gpt-4o \
        --capability T1.1 \
        --setting with_injection \
        --count 50 \
        --output-dir pilot-results/

Multi-capability run:

    python scripts/run_pilot.py \
        --backend anthropic \
        --model claude-opus-4-7 \
        --capability T1.1,T2.3,T3.1 \
        --setting no_injection,with_injection \
        --count 50 \
        --output-dir pilot-results/

Resume support: previously-saved trajectories under output-dir are
skipped (idempotent re-runs).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import traceback
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from chronoception.bench import (
    EvalSetting,
    Runner,
    Trajectory,
    generate_t1_1_instances,
    generate_t2_3_instances,
    generate_t3_1_instances,
)
from chronoception.bench.eval.agents import (
    EchoBackend,
    FixedResponseBackend,
    Message,
)
from chronoception.bench.parsers import extract_tau_self_retrospective
from chronoception.bench.tasks.schema import TaskInstance

# -------------- generators --------------

_GENERATORS = {
    "T1.1": generate_t1_1_instances,
    "T2.3": generate_t2_3_instances,
    "T3.1": generate_t3_1_instances,
}

_SETTINGS = {
    "no_injection": EvalSetting.NO_INJECTION,
    "with_injection": EvalSetting.WITH_INJECTION,
}


# -------------- backend factory --------------


def _build_backend(args: argparse.Namespace):
    """Construct an AgentBackend from CLI args."""
    if args.backend == "echo":
        return EchoBackend()
    if args.backend == "fixed":
        return FixedResponseBackend(response=args.fixed_response or "ok")
    if args.backend == "openai":
        from chronoception.bench.eval.agents import OpenAIBackend
        return OpenAIBackend(
            model=args.model,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            extra_body=_json_or_none(args.extra_body),
            base_url=args.base_url,
            agent_id_override=args.agent_id_override,
            timeout=args.timeout,
        )
    if args.backend == "anthropic":
        from chronoception.bench.eval.agents import AnthropicBackend
        return AnthropicBackend(
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_output_tokens or 4096,
            extra_body=_json_or_none(args.extra_body),
        )
    if args.backend == "google":
        from chronoception.bench.eval.agents import GoogleBackend
        return GoogleBackend(
            model=args.model,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            generation_config=_json_or_none(args.extra_body),
        )
    raise ValueError(f"unknown backend {args.backend!r}")


def _json_or_none(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(
            f"--extra-body must be valid JSON; got {text!r} ({exc})"
        ) from exc


# -------------- trajectory IO --------------


def _trajectory_to_dict(traj: Trajectory) -> dict[str, Any]:
    """Convert a Trajectory into a JSON-serializable dict."""
    return {
        "task_id": traj.task_id,
        "agent_id": traj.agent_id,
        "capability_code": traj.capability_code,
        "budget": traj.budget,
        "budget_kind": traj.budget_kind,
        "tau_min": traj.tau_min,
        "self_narrated_duration": traj.self_narrated_duration,
        "tau_wall": traj.tau_wall,
        "tau_step": traj.tau_step,
        "steps": [
            {"state": s.state, "action": s.action, "timestamp": s.timestamp}
            for s in traj.steps
        ],
        "metadata": traj.metadata,
    }


def _output_path(
    output_dir: Path,
    backend_id: str,
    capability_code: str,
    setting_value: str,
    instance_id: str,
) -> Path:
    safe_backend = backend_id.replace("/", "_")
    return (
        output_dir
        / safe_backend
        / capability_code
        / setting_value
        / f"{instance_id}.json"
    )


def _save_trajectory(path: Path, traj_dict: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(traj_dict, f, indent=2, default=str)


# -------------- pilot loop --------------


def _iter_grid(
    capabilities: Iterable[str],
    settings: Iterable[str],
    seed: int,
    count: int,
) -> Iterable[tuple[str, EvalSetting, TaskInstance]]:
    for capability_code in capabilities:
        generator = _GENERATORS[capability_code]
        instances = generator(seed=seed, count=count)
        for setting_str in settings:
            setting = _SETTINGS[setting_str]
            for instance in instances:
                yield capability_code, setting, instance


def run_pilot(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    backend = _build_backend(args)
    capabilities = args.capability.split(",")
    settings = args.setting.split(",")

    invalid_caps = [c for c in capabilities if c not in _GENERATORS]
    if invalid_caps:
        raise SystemExit(
            f"unknown capability codes {invalid_caps}; expected any of {list(_GENERATORS)}"
        )
    invalid_settings = [s for s in settings if s not in _SETTINGS]
    if invalid_settings:
        raise SystemExit(
            f"unknown settings {invalid_settings}; expected any of {list(_SETTINGS)}"
        )

    total = len(capabilities) * len(settings) * args.count
    saved = 0
    skipped = 0
    failed = 0
    start_time = time.time()

    logging.info(
        "pilot start: backend=%s capabilities=%s settings=%s count=%d total=%d",
        backend.agent_id,
        capabilities,
        settings,
        args.count,
        total,
    )

    for cap_code, setting, instance in _iter_grid(
        capabilities=capabilities,
        settings=settings,
        seed=args.seed,
        count=args.count,
    ):
        out_path = _output_path(
            output_dir=output_dir,
            backend_id=backend.agent_id,
            capability_code=cap_code,
            setting_value=setting.value,
            instance_id=instance.instance_id,
        )
        if out_path.exists() and not args.force:
            skipped += 1
            logging.debug("skip existing: %s", out_path)
            continue

        runner = Runner(agent=backend, setting=setting)
        try:
            traj = runner(instance)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            logging.error(
                "instance %s failed under %s/%s: %s",
                instance.instance_id,
                cap_code,
                setting.value,
                exc,
            )
            logging.debug(traceback.format_exc())
            continue

        # Parser stage 1: extract tau_self for L3 capabilities.
        if cap_code == "T3.1" and traj.steps:
            response_text = traj.steps[-1].action
            parsed_seconds = extract_tau_self_retrospective(response_text)
            if parsed_seconds is not None:
                traj = Trajectory(
                    task_id=traj.task_id,
                    agent_id=traj.agent_id,
                    steps=traj.steps,
                    capability_code=traj.capability_code,
                    budget=traj.budget,
                    budget_kind=traj.budget_kind,
                    tau_min=traj.tau_min,
                    self_narrated_duration=parsed_seconds,
                    metadata={**traj.metadata, "tau_self_method": "regex"},
                )

        _save_trajectory(out_path, _trajectory_to_dict(traj))
        saved += 1
        if saved % max(1, args.log_every) == 0:
            elapsed = time.time() - start_time
            rate = saved / elapsed if elapsed > 0 else 0.0
            logging.info(
                "progress: saved=%d skipped=%d failed=%d / total=%d (%.2f traj/s)",
                saved,
                skipped,
                failed,
                total,
                rate,
            )

    elapsed = time.time() - start_time
    logging.info(
        "pilot done: saved=%d skipped=%d failed=%d total=%d elapsed=%.1fs",
        saved,
        skipped,
        failed,
        total,
        elapsed,
    )


# -------------- argparse --------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_pilot",
        description="Run a slice of the ChronoBench Phase 2 pilot grid.",
    )
    parser.add_argument(
        "--backend",
        required=True,
        choices=["echo", "fixed", "openai", "anthropic", "google"],
    )
    parser.add_argument(
        "--model",
        help="Model id passed to the backend. Required for openai/anthropic/google.",
    )
    parser.add_argument(
        "--capability",
        default="T1.1,T2.3,T3.1",
        help="Comma-separated capability codes from {T1.1, T2.3, T3.1}.",
    )
    parser.add_argument(
        "--setting",
        default="no_injection,with_injection",
        help="Comma-separated settings from {no_injection, with_injection}.",
    )
    parser.add_argument("--count", type=int, default=50, help="Instances per capability.")
    parser.add_argument("--seed", type=int, default=0, help="Generator seed.")
    parser.add_argument(
        "--output-dir",
        default="pilot-results",
        help="Directory under which trajectories are saved.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing trajectory files rather than skipping them.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (provider backends).",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=None,
        help="Per-response output token cap.",
    )
    parser.add_argument(
        "--extra-body",
        default=None,
        help="JSON string passed to provider backends (e.g. reasoning_effort).",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help=(
            "OpenAI-compatible endpoint URL (e.g. http://10.136.20.188:8000/v1) "
            "for routing through vLLM / Ollama / Together AI etc. When set, the "
            "OpenAI backend uses base_url and the agent_id is prefixed with oss/ "
            "instead of openai/."
        ),
    )
    parser.add_argument(
        "--agent-id-override",
        default=None,
        help=(
            "Explicit agent_id, e.g. oss/qwen3-8b-vllm-jetstream. Overrides the "
            "auto-generated identifier and determines the pilot-results/ subdir."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Per-request timeout in seconds (provider backends).",
    )
    parser.add_argument(
        "--fixed-response",
        default=None,
        help="Canned response for backend=fixed.",
    )
    parser.add_argument(
        "--log-every",
        type=int,
        default=10,
        help="Log progress after every N saved trajectories.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging.",
    )
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    if args.backend in ("openai", "anthropic", "google") and not args.model:
        raise SystemExit(f"--model is required when --backend={args.backend}")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _validate_args(args)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    run_pilot(args)


if __name__ == "__main__":
    main()
