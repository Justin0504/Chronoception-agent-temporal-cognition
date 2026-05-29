"""Trajectory and Step — the core data objects.

A Trajectory is the unit of analysis for all ChronoBench metrics. It records
the sequence of (state, action, wall-clock timestamp) tuples produced by an
agent on a single task instance, plus the budget under which the task was
run and the parsed self-narrated duration (if any).

References
----------
FRAMING.md §1 (Trajectory and Notation)
FRAMING.md §2 (The Three Times)
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Step", "Trajectory"]


@dataclass(frozen=True)
class Step:
    """A single (state, action, wall-clock timestamp) tuple in a trajectory.

    Attributes
    ----------
    state : str
        Serialized environment state at the start of the step.
    action : str
        The agent's action emitted at this step.
    timestamp : float
        Wall-clock time at which the action was emitted, in seconds, measured
        from an arbitrary origin t_0. Must be non-decreasing across a
        trajectory.
    """

    state: str
    action: str
    timestamp: float


@dataclass
class Trajectory:
    """A complete agent trajectory on a single task instance.

    The three projections of FRAMING.md §2 — tau_wall, tau_step, tau_self —
    are computed from this object by the metrics module.

    Attributes
    ----------
    task_id : str
        Identifier of the task instance.
    agent_id : str
        Identifier of the agent under evaluation.
    steps : list[Step]
        Ordered sequence of steps with non-decreasing timestamps.
    capability_code : str | None
        Code of the sub-capability this trajectory was constructed to probe
        (e.g. "T1.1", "T2.3"). When set, the epsilon aggregator routes the
        trajectory to the single metric appropriate for the capability's
        axis, rather than scoring it against all three metrics. When None,
        all metrics that are computable from the trajectory's fields are
        applied (ad-hoc analysis mode).
    budget : float | None
        Wall-clock budget B in seconds, if any was specified to the agent.
        None means no explicit budget was given.
    budget_kind : str
        "wall" if budget was expressed in wall-clock units; "step" if it was
        expressed in iteration counts; "none" if no budget.
    tau_min : float | None
        Minimum wall-clock duration in seconds required to complete the task.
        Used as the reference floor in the Parkinson coefficient. None if
        unknown.
    self_narrated_duration : float | None
        Agent's self-reported work duration in seconds, parsed from its
        terminal output by the Pi parser (FRAMING §2). None if the agent made
        no such claim or the parser found none.
    metadata : dict
        Arbitrary auxiliary fields (model name, prompt variant, etc.).
    """

    task_id: str
    agent_id: str
    steps: list[Step]
    capability_code: str | None = None
    budget: float | None = None
    budget_kind: str = "none"
    tau_min: float | None = None
    self_narrated_duration: float | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.budget_kind not in {"wall", "step", "none"}:
            raise ValueError(
                f"budget_kind must be 'wall', 'step', or 'none'; got {self.budget_kind!r}"
            )
        if self.budget_kind == "none" and self.budget is not None:
            raise ValueError("budget_kind='none' is inconsistent with budget being set")
        if self.budget_kind != "none" and self.budget is None:
            raise ValueError(
                f"budget_kind={self.budget_kind!r} requires budget to be set"
            )
        if len(self.steps) >= 2:
            for i in range(1, len(self.steps)):
                if self.steps[i].timestamp < self.steps[i - 1].timestamp:
                    raise ValueError(
                        f"timestamps must be non-decreasing; "
                        f"step {i} has {self.steps[i].timestamp} < "
                        f"step {i - 1} {self.steps[i - 1].timestamp}"
                    )

    @property
    def tau_wall(self) -> float:
        """Wall-clock duration t_T - t_0 in seconds (FRAMING §2)."""
        if len(self.steps) < 2:
            return 0.0
        return self.steps[-1].timestamp - self.steps[0].timestamp

    @property
    def tau_step(self) -> int:
        """Step count T (FRAMING §2). Counts the number of agent actions."""
        return len(self.steps)

    @property
    def tau_self(self) -> float | None:
        """Self-narrated duration in seconds (FRAMING §2). None if undefined."""
        return self.self_narrated_duration

    @property
    def mean_step_dt(self) -> float:
        """Average wall-clock per step <delta t> (FRAMING §2 implicit identity)."""
        if self.tau_step <= 1:
            return 0.0
        return self.tau_wall / (self.tau_step - 1)
