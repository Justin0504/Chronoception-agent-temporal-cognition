"""Task schema and registry for ChronoBench.

The benchmark covers nine sub-capabilities organized as three per axis:

tau_wall:
    T1.1  Clock awareness            — "what time is it now?"
    T1.2  Elapsed-time tracking      — "how long since we started?"
    T1.3  Deadline-aware tradeoff    — switch to cheaper action near deadline

tau_step:
    T2.1  Step-budget honoring       — "do exactly N iterations"
    T2.2  Step-to-wall translation   — "given N steps, how long?"
    T2.3  Wall-budget execution      — "work for B hours" (the L2 core test)

tau_self:
    T3.1  Self-action duration       — "how long did that take?"
    T3.2  Future self-action duration— "how long will this take?"
    T3.3  Self-duration calibration  — confidence intervals on self-reports

See FRAMING.md §5 for the law-axis correspondence.
"""

from chronoception.bench.tasks.registry import CAPABILITIES, axis_for, capability_by_id
from chronoception.bench.tasks.schema import (
    Capability,
    Task,
    TaskInstance,
    TemporalAxis,
)

__all__ = [
    "Capability",
    "Task",
    "TaskInstance",
    "TemporalAxis",
    "CAPABILITIES",
    "axis_for",
    "capability_by_id",
]
