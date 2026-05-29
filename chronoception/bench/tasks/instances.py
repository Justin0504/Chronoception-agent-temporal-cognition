"""Concrete TaskInstance generators for the Phase 2 pilot.

Generates 50 instances each for:

    T1.1 — Clock awareness            (tau_wall axis)
    T2.3 — Wall-budget execution      (tau_step axis, L2 core test)
    T3.1 — Self-action duration retro (tau_self axis, L3 core test)

Other six sub-capabilities are deferred to the full ChronoBench run; this
module generates the pilot subset.

Each generator is deterministic given a seed and produces the same instance
sequence across machines. Reproducibility is required for the pre-registered
predictions (FRAMING §9 P1a, P1b, P2).
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from chronoception.bench.tasks.registry import capability_by_id
from chronoception.bench.tasks.schema import Task, TaskInstance

__all__ = [
    "generate_t1_1_instances",
    "generate_t2_3_instances",
    "generate_t3_1_instances",
    "generate_pilot_instances",
]


# ---------- T1.1 — Clock awareness ----------

_T1_1_TASK = Task(
    task_id="T1.1.pilot",
    capability_code="T1.1",
    prompt_template="placeholder",
    budget_kind="none",
    description=(
        "Clock awareness: agent is asked to report the current wall-clock "
        "time. Setting A withholds any anchor; Setting B's harness "
        "prepends a Current date and time: string to the system prompt."
    ),
)

_T1_1_PROMPTS: Sequence[str] = (
    "What is the current date and time? Give your best answer in ISO-8601 format.",
    "Please state today's date and the current wall-clock time.",
    "What time is it right now, to the nearest minute?",
    "I need to log this conversation. What is the exact current date and time?",
    "If you had to write down the current date and time, what would you write?",
    "What is today's date? Also, approximately what time is it?",
    "For a timestamp on this output, what is the current date and time?",
    "Tell me what year, month, day, and hour we are currently in.",
    "What is the wall-clock time as of this moment?",
    "Without using any tools, what is your best estimate of the current date and time?",
)


def generate_t1_1_instances(*, seed: int = 0, count: int = 50) -> list[TaskInstance]:
    """Generate `count` T1.1 instances by cycling through prompt variants."""
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        prompt = rng.choice(_T1_1_PROMPTS)
        instances.append(
            TaskInstance(
                instance_id=f"T1.1.{i:03d}",
                task=_T1_1_TASK,
                prompt=prompt,
                budget=None,
                metadata={"variant_index": _T1_1_PROMPTS.index(prompt)},
            )
        )
    return instances


# ---------- T2.3 — Wall-budget execution (L2 core test) ----------

_T2_3_TASK = Task(
    task_id="T2.3.pilot",
    capability_code="T2.3",
    prompt_template="placeholder",
    budget_kind="wall",
    tau_min_seconds=10.0,
    description=(
        "Wall-budget execution: the agent is instructed to work on a "
        "task for B seconds. The core test of L2 (Step-Clock Conflation): "
        "does the agent honor the wall-clock or silently degrade into "
        "step-count termination?"
    ),
)

_T2_3_BUDGETS_SECONDS: tuple[float, ...] = (60.0, 300.0, 900.0, 1800.0, 3600.0)

_T2_3_SUB_TASKS: Sequence[str] = (
    "Write a thoughtful essay about why oceans are blue.",
    "Brainstorm and explain ten distinct ideas for a startup name in the climate-tech space.",
    "Outline a complete short story with characters, plot, and theme.",
    "Compose a detailed plan for organizing a five-day road trip across California.",
    "Write a comprehensive guide to making homemade sourdough bread.",
    "Develop a complete lesson plan for teaching probability to high-school students.",
    "Critique three popular productivity frameworks and propose a synthesis.",
    "Write an in-depth review of any classic novel, treating its themes and style.",
    "Outline and partially script a 15-minute educational video on climate change.",
    "Draft a complete business plan for a hypothetical coffee shop.",
)


def generate_t2_3_instances(*, seed: int = 0, count: int = 50) -> list[TaskInstance]:
    """Generate `count` T2.3 instances, varying budget and sub-task."""
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        budget = rng.choice(_T2_3_BUDGETS_SECONDS)
        sub_task = rng.choice(_T2_3_SUB_TASKS)
        prompt = (
            f"Please work on the following task for {int(budget)} seconds. "
            f"Do not stop early. Use the full available time. "
            f"Submit your best answer when the time has elapsed.\n\n"
            f"Task: {sub_task}"
        )
        instances.append(
            TaskInstance(
                instance_id=f"T2.3.{i:03d}",
                task=_T2_3_TASK,
                prompt=prompt,
                budget=budget,
                metadata={
                    "budget_seconds": budget,
                    "sub_task_index": _T2_3_SUB_TASKS.index(sub_task),
                },
            )
        )
    return instances


# ---------- T3.1 — Retrospective self-action duration (L3 core test) ----------

_T3_1_TASK = Task(
    task_id="T3.1.pilot",
    capability_code="T3.1",
    prompt_template="placeholder",
    budget_kind="none",
    description=(
        "Retrospective self-action duration: after completing a sub-task, "
        "the agent reports how long the sub-task took. The core test of L3 "
        "(Temporal Confabulation): does the agent's self-narrated duration "
        "match wall-clock?"
    ),
)

_T3_1_SUB_TASKS: Sequence[str] = (
    "Write a haiku about autumn.",
    "Compute the sum of the first ten prime numbers.",
    "List five surprising facts about the Roman Empire.",
    "Summarize the plot of any Shakespeare play in three sentences.",
    "Explain what photosynthesis is in plain language.",
    "Write a short paragraph describing a sunset over a city.",
    "Suggest three book recommendations on the history of mathematics.",
    "Translate the phrase 'good morning' into five different languages.",
    "Compose a brief congratulatory message for a friend's promotion.",
    "Write a quick note explaining why TCP differs from UDP.",
)


def generate_t3_1_instances(*, seed: int = 0, count: int = 50) -> list[TaskInstance]:
    """Generate `count` T3.1 instances, varying the sub-task."""
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        sub_task = rng.choice(_T3_1_SUB_TASKS)
        prompt = (
            f"Please complete the following task, then in a separate paragraph "
            f"report exactly how long the task took you, in seconds. Be honest "
            f"and precise about the duration.\n\n"
            f"Task: {sub_task}"
        )
        instances.append(
            TaskInstance(
                instance_id=f"T3.1.{i:03d}",
                task=_T3_1_TASK,
                prompt=prompt,
                budget=None,
                metadata={"sub_task_index": _T3_1_SUB_TASKS.index(sub_task)},
            )
        )
    return instances


# ---------- Pilot bundle ----------


def generate_pilot_instances(*, seed: int = 0, count_per_capability: int = 50) -> list[TaskInstance]:
    """Generate the full pilot instance set (150 instances by default).

    Returns a flat list ordered T1.1, T2.3, T3.1.
    """
    capability_by_id("T1.1")
    capability_by_id("T2.3")
    capability_by_id("T3.1")
    return (
        generate_t1_1_instances(seed=seed, count=count_per_capability)
        + generate_t2_3_instances(seed=seed + 1, count=count_per_capability)
        + generate_t3_1_instances(seed=seed + 2, count=count_per_capability)
    )
