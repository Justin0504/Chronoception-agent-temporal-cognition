"""Schema dataclasses for ChronoBench tasks.

A Task is a template parameterized by zero or more variables; a TaskInstance
is a Task bound to concrete variable values. Sub-capabilities are grouped
by temporal axis per FRAMING.md §5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__all__ = [
    "TemporalAxis",
    "Capability",
    "Task",
    "TaskInstance",
]


class TemporalAxis(str, Enum):
    """The three projection axes of FRAMING.md §2."""

    WALL = "tau_wall"
    STEP = "tau_step"
    SELF = "tau_self"


@dataclass(frozen=True)
class Capability:
    """A sub-capability of agent chronoception (one of the nine in §5 / tasks/__init__.py)."""

    code: str  # e.g. "T1.1"
    name: str  # e.g. "Clock awareness"
    axis: TemporalAxis
    description: str


@dataclass(frozen=True)
class Task:
    """A task template. Concrete benchmark items are TaskInstances of a Task."""

    task_id: str
    capability_code: str
    prompt_template: str
    budget_kind: str = "none"  # "wall", "step", or "none"
    tau_min_seconds: float | None = None
    description: str = ""


@dataclass
class TaskInstance:
    """A Task bound to concrete variable values, ready to send to an agent."""

    instance_id: str
    task: Task
    prompt: str
    budget: float | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.task.budget_kind != "none" and self.budget is None:
            raise ValueError(
                f"task {self.task.task_id} declares budget_kind={self.task.budget_kind!r} "
                "but instance has no budget set"
            )
        if self.task.budget_kind == "none" and self.budget is not None:
            raise ValueError(
                f"task {self.task.task_id} declares budget_kind='none' but instance has a budget"
            )
