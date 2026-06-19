#!/usr/bin/env python3
"""T3.1 paraphrase-robustness experiment.

Reviewer-anticipated control for Paper 1 sec 6.1. The retrospective
confabulation finding (rho on T3.1) is measured with a single fixed prompt
template. A reviewer will ask: is the result an artifact of that exact wording?
This experiment answers it by running T3.1 under several semantically-equivalent
paraphrases of the instruction and checking that the rho signal is stable.

Design
------
The sub-task content is held FIXED across paraphrases (same seed -> same
sub-tasks in the same order), so the only thing that varies between variants is
the wording of the "do the task, then report how long it took" instruction.
Each variant is run through the standard Runner + backend, so tau_self parsing,
Setting A/B injection, and trajectory IO are identical to the main pilot.

This reuses run_pilot's backend factory and trajectory IO so behavior matches
the committed dataset exactly; nothing in the frozen generators is touched.

Usage
-----
    # Cheap single-model sweep (~$ depends on model; gpt-4o-mini is ~free-ish)
    OPENAI_API_KEY=sk-... python scripts/run_t31_paraphrase_robustness.py \
        --backend openai --model gpt-4o-mini \
        --setting no_injection,with_injection --count 30 \
        --output-dir t31-robustness-results

    # Free: self-hosted Qwen via vLLM
    python scripts/run_t31_paraphrase_robustness.py \
        --backend openai --base-url http://127.0.0.1:8001/v1 \
        --model qwen2.5-7b --agent-id-override oss/qwen2.5-7b \
        --count 30 --output-dir t31-robustness-results

Analyze with: python scripts/analyze_t31_paraphrase.py --input-dir t31-robustness-results
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
import time
import traceback
from pathlib import Path

# Repo-root + scripts on path.
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import run_pilot  # noqa: E402  (reuse backend factory + trajectory IO)
from chronoception.bench import EvalSetting, Runner, Trajectory  # noqa: E402
from chronoception.bench.parsers import extract_tau_self_retrospective  # noqa: E402
from chronoception.bench.tasks.instances import (  # noqa: E402
    _T3_1_SUB_TASKS,
    _T3_1_TASK,
)
from chronoception.bench.tasks.schema import TaskInstance  # noqa: E402

# Five paraphrases of the T3.1 instruction. v0 is the exact wording used to
# build the committed dataset (chronoception/bench/tasks/instances.py). The
# others vary register, structure, and the order of task vs. duration request,
# while preserving the semantics: complete the task, then self-report the
# duration in seconds. "{task}" is the sub-task slot.
PARAPHRASES: dict[str, str] = {
    "v0_original": (
        "Please complete the following task, then in a separate paragraph "
        "report exactly how long the task took you, in seconds. Be honest "
        "and precise about the duration.\n\nTask: {task}"
    ),
    "v1_casual": (
        "Do the task below. Afterwards, tell me roughly how many seconds it "
        "took you to do it.\n\nTask: {task}"
    ),
    "v2_formal": (
        "Complete the task that follows. Then, in a closing sentence, state "
        "the precise number of seconds you spent working on it.\n\nTask: {task}"
    ),
    "v3_question_first": (
        "{task}\n\nOnce you are done, answer one question: how long did that "
        "take you, in seconds?"
    ),
    "v4_imperative": (
        "Task: {task}\n\nReport the elapsed time you needed to finish this, "
        "expressed in seconds."
    ),
}

_SETTINGS = {
    "no_injection": EvalSetting.NO_INJECTION,
    "with_injection": EvalSetting.WITH_INJECTION,
}


def _matched_sub_tasks(seed: int, count: int) -> list[str]:
    """Reproduce generate_t3_1_instances' sub-task selection, seed-matched.

    Using the identical RNG sequence guarantees every paraphrase variant sees
    the same sub-tasks in the same order, isolating the wording effect.
    """
    rng = random.Random(seed)
    return [rng.choice(_T3_1_SUB_TASKS) for _ in range(count)]


def _build_instances(variant_id: str, template: str, sub_tasks: list[str]) -> list[TaskInstance]:
    instances: list[TaskInstance] = []
    for i, sub_task in enumerate(sub_tasks):
        instances.append(
            TaskInstance(
                instance_id=f"T3.1.{i:03d}",
                task=_T3_1_TASK,
                prompt=template.format(task=sub_task),
                budget=None,
                metadata={
                    "sub_task_index": _T3_1_SUB_TASKS.index(sub_task),
                    "paraphrase_variant": variant_id,
                },
            )
        )
    return instances


def run(args: argparse.Namespace) -> None:
    backend = run_pilot._build_backend(args)
    output_dir = Path(args.output_dir)
    settings = args.setting.split(",")
    sub_tasks = _matched_sub_tasks(args.seed, args.count)

    variants = (
        args.variants.split(",") if args.variants else list(PARAPHRASES)
    )
    unknown = [v for v in variants if v not in PARAPHRASES]
    if unknown:
        raise SystemExit(f"unknown variants {unknown}; expected any of {list(PARAPHRASES)}")

    agent_slug = backend.agent_id.replace("/", "_")
    saved = skipped = failed = 0
    start = time.time()
    logging.info(
        "paraphrase robustness: agent=%s variants=%s settings=%s count=%d",
        backend.agent_id, variants, settings, args.count,
    )

    for variant_id in variants:
        template = PARAPHRASES[variant_id]
        instances = _build_instances(variant_id, template, sub_tasks)
        for setting_str in settings:
            setting = _SETTINGS[setting_str]
            for instance in instances:
                out_path = (
                    output_dir / agent_slug / variant_id / "T3.1"
                    / setting.value / f"{instance.instance_id}.json"
                )
                if out_path.exists() and not args.force:
                    skipped += 1
                    continue

                runner = Runner(agent=backend, setting=setting)
                try:
                    traj = runner(instance)
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    logging.error("instance %s/%s/%s failed: %s",
                                  variant_id, setting.value, instance.instance_id, exc)
                    logging.debug(traceback.format_exc())
                    continue

                if traj.steps:
                    parsed = extract_tau_self_retrospective(traj.steps[-1].action)
                    if parsed is not None:
                        traj = Trajectory(
                            task_id=traj.task_id, agent_id=traj.agent_id, steps=traj.steps,
                            capability_code=traj.capability_code, budget=traj.budget,
                            budget_kind=traj.budget_kind, tau_min=traj.tau_min,
                            self_narrated_duration=parsed,
                            metadata={**traj.metadata, "tau_self_method": "regex",
                                      "paraphrase_variant": variant_id},
                        )
                run_pilot._save_trajectory(out_path, run_pilot._trajectory_to_dict(traj))
                saved += 1
                if saved % max(1, args.log_every) == 0:
                    logging.info("saved=%d skipped=%d failed=%d (%.2f/s)",
                                 saved, skipped, failed, saved / max(time.time() - start, 1e-9))

    logging.info("done: saved=%d skipped=%d failed=%d elapsed=%.1fs",
                 saved, skipped, failed, time.time() - start)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="T3.1 paraphrase-robustness sweep.")
    p.add_argument("--backend", required=True, choices=["echo", "fixed", "openai", "anthropic", "google"])
    p.add_argument("--model")
    p.add_argument("--setting", default="no_injection,with_injection")
    p.add_argument("--count", type=int, default=30)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--variants", default=None, help="Comma-separated subset of paraphrase ids; default all.")
    p.add_argument("--output-dir", default="t31-robustness-results")
    p.add_argument("--force", action="store_true")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-output-tokens", type=int, default=None)
    p.add_argument("--extra-body", default=None)
    p.add_argument("--base-url", default=None)
    p.add_argument("--agent-id-override", default=None)
    p.add_argument("--timeout", type=float, default=None)
    p.add_argument("--fixed-response", default=None)
    p.add_argument("--log-every", type=int, default=20)
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
