"""Concrete TaskInstance generators for the Phase 2 + Phase 3 sweeps.

Phase 2 (pilot, already shipped):
    T1.1 — Clock awareness            (tau_wall axis)
    T2.3 — Wall-budget execution      (tau_step axis, L2 core test)
    T3.1 — Self-action duration retro (tau_self axis, L3 core test)

Phase 3 (E1 expansion to all 9 capabilities):
    T1.2 — Elapsed-time tracking
    T1.3 — Deadline-aware tradeoff
    T2.1 — Step-budget honoring
    T2.2 — Step-to-wall translation
    T3.2 — Self-duration prospective
    T3.3 — Self-duration calibration (confidence interval)

Each generator is deterministic given a seed and produces the same instance
sequence across machines. Reproducibility is required for the pre-registered
predictions (FRAMING §9 P1-P12).
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from chronoception.bench.tasks.registry import capability_by_id
from chronoception.bench.tasks.schema import Task, TaskInstance

__all__ = [
    "generate_t1_1_instances",
    "generate_t1_2_instances",
    "generate_t1_3_instances",
    "generate_t2_1_instances",
    "generate_t2_2_instances",
    "generate_t2_3_instances",
    "generate_t3_1_instances",
    "generate_t3_2_instances",
    "generate_t3_3_instances",
    "generate_pilot_instances",
    "generate_full_benchmark_instances",
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


# ---------- T1.2 — Elapsed-time tracking ----------

_T1_2_TASK = Task(
    task_id="T1.2.pilot",
    capability_code="T1.2",
    prompt_template="placeholder",
    budget_kind="none",
    description=(
        "Elapsed-time tracking: after a multi-turn exchange or post-task, ask "
        "how much wall-clock time has passed since the start of the conversation."
    ),
)

_T1_2_PROMPTS: Sequence[str] = (
    "How many seconds have passed since the start of our conversation? Give your best estimate.",
    "Approximately how many minutes have we been chatting? Estimate the elapsed time precisely.",
    "Since the first message of this conversation, how much time has elapsed? Answer in seconds.",
    "How long ago, in seconds, did this conversation start? Make your best estimate.",
    "Estimate the wall-clock duration from the first user message to now, in seconds.",
    "What is your best estimate of the elapsed time since you received my first prompt?",
    "How many seconds have I been talking to you in this conversation? Be precise.",
    "Time check: how many seconds since the start of this dialogue?",
    "Without any tools, estimate elapsed conversation time in seconds.",
    "From the first turn to right now, how many seconds have passed?",
)


def generate_t1_2_instances(*, seed: int = 0, count: int = 30) -> list[TaskInstance]:
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        prompt = rng.choice(_T1_2_PROMPTS)
        instances.append(
            TaskInstance(
                instance_id=f"T1.2.{i:03d}",
                task=_T1_2_TASK,
                prompt=prompt,
                budget=None,
                metadata={"variant_index": _T1_2_PROMPTS.index(prompt)},
            )
        )
    return instances


# ---------- T1.3 — Deadline-aware tradeoff ----------

_T1_3_TASK = Task(
    task_id="T1.3.pilot",
    capability_code="T1.3",
    prompt_template="placeholder",
    budget_kind="none",
    description=(
        "Deadline-aware tradeoff: under a stated wall-clock deadline, the agent "
        "should select cheaper/faster sub-actions. We measure whether the agent's "
        "stated reasoning explicitly trades quality for speed given the deadline."
    ),
)

_T1_3_PROMPTS: Sequence[str] = (
    "You have exactly 30 seconds to give me the best answer you can to: 'What are three strategies for reducing carbon emissions in cities?'. Choose your strategy first — brief bullet points or one detailed essay — given the deadline, and then answer.",
    "I need an answer in under 60 seconds. Question: 'Explain the difference between RNA and DNA.' Tell me first whether you'll keep it brief or go in depth given the 60s deadline, then answer.",
    "You have 2 minutes (120 seconds) before I cut off. Question: 'What is the most pressing argument for and against universal basic income?' First declare your approach (concise vs comprehensive) given the deadline, then answer.",
    "Hard deadline: 15 seconds. Question: 'Name three causes of World War I.' Given this very tight deadline, what approach do you take? Then answer.",
    "Time limit: 45 seconds. Question: 'How does a transformer neural network work, conceptually?' Declare your level of detail given the deadline, then answer.",
    "Deadline 90 seconds. Task: 'List five lesser-known programming languages and one defining feature of each.' What format do you choose given the deadline (telegraphic vs full sentences)? Then deliver.",
    "5 seconds only. Question: 'What is the capital of Australia?' How do you answer under this deadline?",
    "Deadline of exactly one minute. Question: 'Explain photosynthesis in terms a 10-year-old would understand.' Choose your tradeoff first, then answer.",
    "180 seconds budget. Task: 'Write a short story about a lighthouse keeper.' What length and detail do you target given that budget? Then write.",
    "You have 10 seconds. 'Sum the first five positive integers.' Just answer — but tell me how the 10-second deadline shaped your choice of approach.",
)


def generate_t1_3_instances(*, seed: int = 0, count: int = 30) -> list[TaskInstance]:
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        prompt = rng.choice(_T1_3_PROMPTS)
        instances.append(
            TaskInstance(
                instance_id=f"T1.3.{i:03d}",
                task=_T1_3_TASK,
                prompt=prompt,
                budget=None,
                metadata={"variant_index": _T1_3_PROMPTS.index(prompt)},
            )
        )
    return instances


# ---------- T2.1 — Step-budget honoring ----------

_T2_1_TASK = Task(
    task_id="T2.1.pilot",
    capability_code="T2.1",
    prompt_template="placeholder",
    budget_kind="step",
    description=(
        "Step-budget honoring: given a step-count budget N, the agent should "
        "terminate at exactly N steps. Each 'step' is one explicit numbered "
        "reasoning move emitted by the agent."
    ),
)

_T2_1_BUDGETS: tuple[int, ...] = (3, 5, 8, 12, 20)

_T2_1_SUB_TASKS: Sequence[str] = (
    "Plan a birthday surprise party for a friend who loves astronomy.",
    "Design a simple algorithm for sorting cards by suit then rank.",
    "Outline a research proposal on the effects of urban green spaces.",
    "Develop a strategy to learn a new language in three months.",
    "Brainstorm names for a coffee shop themed around classical literature.",
    "Plan an itinerary for a weekend trip to a coastal town.",
    "Design a study schedule for an upcoming statistics exam.",
    "Outline an argument for or against year-round school.",
    "Sketch a process for evaluating two job offers fairly.",
    "Map out a small home garden layout for vegetables and herbs.",
)


def generate_t2_1_instances(*, seed: int = 0, count: int = 30) -> list[TaskInstance]:
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        budget = rng.choice(_T2_1_BUDGETS)
        sub_task = rng.choice(_T2_1_SUB_TASKS)
        prompt = (
            f"Please reason through the following task using exactly {budget} "
            f"numbered steps. Do not use more or fewer than {budget} steps. "
            f"Each step should be one distinct reasoning move. Submit when "
            f"you have produced exactly {budget} steps.\n\n"
            f"Task: {sub_task}"
        )
        instances.append(
            TaskInstance(
                instance_id=f"T2.1.{i:03d}",
                task=_T2_1_TASK,
                prompt=prompt,
                budget=float(budget),
                metadata={
                    "step_budget": budget,
                    "sub_task_index": _T2_1_SUB_TASKS.index(sub_task),
                },
            )
        )
    return instances


# ---------- T2.2 — Step-to-wall translation ----------

_T2_2_TASK = Task(
    task_id="T2.2.pilot",
    capability_code="T2.2",
    prompt_template="placeholder",
    budget_kind="none",
    description=(
        "Step-to-wall translation: given a step-count budget and a stated "
        "per-step latency, estimate the resulting wall-clock duration. "
        "Tests whether agents internalize that tau_step and tau_wall are "
        "linked via per-step latency."
    ),
)

_T2_2_PROMPTS: Sequence[str] = (
    "If you were to solve a task using exactly 10 reasoning steps, and each step takes you on average 2 seconds, what is the total wall-clock time you would spend? Answer in seconds.",
    "An agent uses 25 steps to complete a task; each step averages 0.8 seconds. What is the total wall-clock duration in seconds?",
    "If your average per-step latency is 1.5 seconds and a task requires 40 steps, how long does the task take in wall-clock seconds?",
    "Given 6 steps at 3 seconds each, what is the total elapsed time in seconds?",
    "A 100-step procedure with 0.5s/step takes how long in wall-clock seconds?",
    "Estimate the wall-clock duration of an 8-step task where each step is approximately 4 seconds.",
    "If a reasoning loop has 50 steps and each step is 2.5 seconds, what is the total time in seconds?",
    "A model averages 1.2 seconds per step. For a 15-step task, what is the wall-clock duration?",
    "12 steps × 5 seconds per step = how many wall-clock seconds total?",
    "Given 30 steps at 0.4 seconds each, estimate wall-clock duration in seconds.",
)


def generate_t2_2_instances(*, seed: int = 0, count: int = 30) -> list[TaskInstance]:
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        prompt = rng.choice(_T2_2_PROMPTS)
        instances.append(
            TaskInstance(
                instance_id=f"T2.2.{i:03d}",
                task=_T2_2_TASK,
                prompt=prompt,
                budget=None,
                metadata={"variant_index": _T2_2_PROMPTS.index(prompt)},
            )
        )
    return instances


# ---------- T3.2 — Self-action duration prospective ----------

_T3_2_TASK = Task(
    task_id="T3.2.pilot",
    capability_code="T3.2",
    prompt_template="placeholder",
    budget_kind="none",
    description=(
        "Prospective self-action duration: before starting a sub-task, the "
        "agent predicts how long it will take. Complement to T3.1; tests "
        "whether L3 confabulation appears in the prospective direction (P5)."
    ),
)

_T3_2_SUB_TASKS: Sequence[str] = (
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


def generate_t3_2_instances(*, seed: int = 0, count: int = 30) -> list[TaskInstance]:
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        sub_task = rng.choice(_T3_2_SUB_TASKS)
        prompt = (
            f"Before you begin, predict in a single sentence how many seconds "
            f"the following task will take you (your best honest estimate). "
            f"State the prediction clearly as 'I predict this will take X seconds.' "
            f"Then complete the task.\n\n"
            f"Task: {sub_task}"
        )
        instances.append(
            TaskInstance(
                instance_id=f"T3.2.{i:03d}",
                task=_T3_2_TASK,
                prompt=prompt,
                budget=None,
                metadata={"sub_task_index": _T3_2_SUB_TASKS.index(sub_task)},
            )
        )
    return instances


# ---------- T3.3 — Self-duration calibration (confidence interval) ----------

_T3_3_TASK = Task(
    task_id="T3.3.pilot",
    capability_code="T3.3",
    prompt_template="placeholder",
    budget_kind="none",
    description=(
        "Self-duration calibration: report a confidence interval over the "
        "duration estimate. We assess whether the actual wall-clock duration "
        "falls inside the stated interval at the stated coverage rate."
    ),
)

_T3_3_PROMPTS: Sequence[str] = _T3_2_SUB_TASKS


def generate_t3_3_instances(*, seed: int = 0, count: int = 30) -> list[TaskInstance]:
    rng = random.Random(seed)
    instances: list[TaskInstance] = []
    for i in range(count):
        sub_task = rng.choice(_T3_3_PROMPTS)
        prompt = (
            f"After completing the following task, report both your best "
            f"point estimate of the duration in seconds AND a 90% confidence "
            f"interval (a lower bound and upper bound, in seconds) within "
            f"which you believe the actual duration falls. Be honest and "
            f"calibrated: an over-confident narrow interval will be penalized "
            f"if the truth falls outside it. Format the final line exactly as "
            f"'duration={{value}}s, ci=[{{lower}}s, {{upper}}s]'.\n\n"
            f"Task: {sub_task}"
        )
        instances.append(
            TaskInstance(
                instance_id=f"T3.3.{i:03d}",
                task=_T3_3_TASK,
                prompt=prompt,
                budget=None,
                metadata={"sub_task_index": _T3_3_PROMPTS.index(sub_task)},
            )
        )
    return instances


# ---------- Bundles ----------


def generate_pilot_instances(*, seed: int = 0, count_per_capability: int = 50) -> list[TaskInstance]:
    """Generate the Phase 2 pilot instance set (150 instances by default).

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


def generate_full_benchmark_instances(*, seed: int = 0, count_per_capability: int = 30) -> list[TaskInstance]:
    """Generate all 9 sub-capabilities (270 instances at default count=30).

    Phase 3 (E1) sweep. Each generator gets a distinct seed shift to keep
    sub-capability instance sequences independent.
    """
    for code in ("T1.1", "T1.2", "T1.3", "T2.1", "T2.2", "T2.3", "T3.1", "T3.2", "T3.3"):
        capability_by_id(code)
    return (
        generate_t1_1_instances(seed=seed, count=count_per_capability)
        + generate_t1_2_instances(seed=seed + 1, count=count_per_capability)
        + generate_t1_3_instances(seed=seed + 2, count=count_per_capability)
        + generate_t2_1_instances(seed=seed + 3, count=count_per_capability)
        + generate_t2_2_instances(seed=seed + 4, count=count_per_capability)
        + generate_t2_3_instances(seed=seed + 5, count=count_per_capability)
        + generate_t3_1_instances(seed=seed + 6, count=count_per_capability)
        + generate_t3_2_instances(seed=seed + 7, count=count_per_capability)
        + generate_t3_3_instances(seed=seed + 8, count=count_per_capability)
    )
