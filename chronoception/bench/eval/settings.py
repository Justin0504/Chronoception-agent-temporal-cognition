"""Evaluation settings and grouped aggregation (FRAMING.md §3.1).

Two settings partition every ChronoBench evaluation:

    Setting A — no-injection: the agent receives no harness-supplied
                wall-clock signal. Baseline API behavior.
    Setting B — with-injection: the agent receives a system-prompt or
                tool-supplied "Current time" string before the task begins,
                mirroring the default behavior of frontier closed-system
                harnesses.

Prediction P1 (FRAMING §9) is a comparison between these two settings.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import Enum

from chronoception.bench.metrics import chronoceptive_calibration_error
from chronoception.bench.trajectory import Trajectory

__all__ = ["EvalSetting", "epsilon_by_setting"]


class EvalSetting(str, Enum):
    """Evaluation setting per FRAMING.md §3.1."""

    NO_INJECTION = "no_injection"
    WITH_INJECTION = "with_injection"


def epsilon_by_setting(
    trajectories: Iterable[Trajectory],
    weights: tuple[float, float, float] = (1.0 / 3, 1.0 / 3, 1.0 / 3),
) -> dict[EvalSetting, float]:
    """Compute chronoceptive calibration error per evaluation setting.

    Trajectories with no setting recorded are excluded (rather than pooled),
    since the Injection Tell partitioning depends on knowing the setting.
    """
    buckets: dict[EvalSetting, list[Trajectory]] = {}
    for traj in trajectories:
        setting_str = traj.metadata.get("setting") if isinstance(traj.metadata, dict) else None
        if setting_str is None:
            continue
        try:
            setting = EvalSetting(setting_str)
        except ValueError as exc:
            raise ValueError(
                f"trajectory {traj.task_id!r} has unrecognized setting {setting_str!r}; "
                f"expected one of {[s.value for s in EvalSetting]}"
            ) from exc
        buckets.setdefault(setting, []).append(traj)

    return {
        setting: chronoceptive_calibration_error(trajs, weights=weights)
        for setting, trajs in buckets.items()
    }
