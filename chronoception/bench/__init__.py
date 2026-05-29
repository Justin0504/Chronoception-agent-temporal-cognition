"""ChronoBench — diagnostic benchmark for agent temporal cognition.

Re-exports the public API. All definitions trace back to FRAMING.md.
"""

from chronoception.bench.metrics import (
    car,
    chronoceptive_calibration_error,
    confabulation_ratio,
    epsilon,
    parkinson_coefficient,
)
from chronoception.bench.trajectory import (
    Step,
    Trajectory,
)

__all__ = [
    # trajectory
    "Step",
    "Trajectory",
    # metrics
    "parkinson_coefficient",
    "car",
    "confabulation_ratio",
    "chronoceptive_calibration_error",
    "epsilon",  # alias
]
