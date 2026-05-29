"""The fixed registry of ChronoBench sub-capabilities (nine, three per axis).

This is the framework's taxonomic anchor — the entries here mirror the
structure of FRAMING.md §5 and chronoception/bench/tasks/__init__.py.
Adding or removing entries is a framework-revision change, not a casual
patch.
"""

from __future__ import annotations

from chronoception.bench.tasks.schema import Capability, TemporalAxis

__all__ = ["CAPABILITIES", "capability_by_id", "axis_for"]


CAPABILITIES: tuple[Capability, ...] = (
    # ----- tau_wall axis -----
    Capability(
        code="T1.1",
        name="Clock awareness",
        axis=TemporalAxis.WALL,
        description=(
            "Given the current wall-clock time at the start of an interaction, "
            "report the wall-clock time at a later point during the interaction."
        ),
    ),
    Capability(
        code="T1.2",
        name="Elapsed-time tracking",
        axis=TemporalAxis.WALL,
        description=(
            "Track the elapsed wall-clock time since a designated reference event "
            "within the interaction."
        ),
    ),
    Capability(
        code="T1.3",
        name="Deadline-aware tradeoff",
        axis=TemporalAxis.WALL,
        description=(
            "Under a stated wall-clock deadline, select cheaper / faster actions "
            "as the deadline approaches."
        ),
    ),
    # ----- tau_step axis -----
    Capability(
        code="T2.1",
        name="Step-budget honoring",
        axis=TemporalAxis.STEP,
        description=(
            "Given a step-count budget N, terminate at exactly N steps."
        ),
    ),
    Capability(
        code="T2.2",
        name="Step-to-wall translation",
        axis=TemporalAxis.STEP,
        description=(
            "Given a step-count budget N and a known per-step latency, estimate "
            "the resulting wall-clock duration."
        ),
    ),
    Capability(
        code="T2.3",
        name="Wall-budget execution",
        axis=TemporalAxis.STEP,
        description=(
            "Given a wall-clock budget B, continue working until B is exhausted "
            "rather than degrading to a fixed step-count terminator. "
            "This is the core test of L2 (Step-Clock Conflation)."
        ),
    ),
    # ----- tau_self axis -----
    Capability(
        code="T3.1",
        name="Self-action duration estimation (retrospective)",
        axis=TemporalAxis.SELF,
        description=(
            "After completing a sub-task, report how long the sub-task took. "
            "The core test of L3 (Temporal Confabulation)."
        ),
    ),
    Capability(
        code="T3.2",
        name="Self-action duration estimation (prospective)",
        axis=TemporalAxis.SELF,
        description=(
            "Before starting a sub-task, predict how long it will take."
        ),
    ),
    Capability(
        code="T3.3",
        name="Self-duration calibration",
        axis=TemporalAxis.SELF,
        description=(
            "Report a confidence interval over the duration estimate; assess "
            "whether the actual duration falls within the stated interval at "
            "the stated rate."
        ),
    ),
)


_BY_ID: dict[str, Capability] = {c.code: c for c in CAPABILITIES}


def capability_by_id(code: str) -> Capability:
    """Look up a capability by its code (e.g. "T1.1")."""
    if code not in _BY_ID:
        raise KeyError(f"unknown capability code {code!r}")
    return _BY_ID[code]


def axis_for(code: str) -> TemporalAxis:
    """Return the temporal axis for a capability code."""
    return capability_by_id(code).axis
