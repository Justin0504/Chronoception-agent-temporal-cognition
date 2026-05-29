"""Metrics for the three laws of agent temporal failure.

Implements the four quantities defined in FRAMING.md §4 and §5:

- alpha     — Agentic Parkinson coefficient   (L1, tau_wall axis)
- CAR       — Clock-Adherence Ratio           (L2, tau_step axis)
- rho       — Temporal Confabulation ratio    (L3, tau_self axis)
- epsilon   — Chronoceptive Calibration Error (central scalar)

All four are deterministic functions of a single Trajectory or an iterable of
Trajectory objects. They make no calls to models or external services; they
purely score what the agent did.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

from chronoception.bench.tasks.registry import capability_by_id
from chronoception.bench.tasks.schema import TemporalAxis
from chronoception.bench.trajectory import Trajectory

__all__ = [
    "parkinson_coefficient",
    "car",
    "confabulation_ratio",
    "chronoceptive_calibration_error",
    "epsilon",
]


def parkinson_coefficient(traj: Trajectory) -> float:
    """L1 — Agentic Parkinson's Law: alpha = (tau_wall* - tau_min) / (B - tau_min).

    Defined when:
        - traj.budget_kind == "wall"
        - traj.tau_min is not None
        - traj.budget > traj.tau_min

    alpha = 0 means the agent finished as fast as physically possible;
    alpha = 1 means the agent used the entire budget regardless of need.
    Clamped to [0, 1].

    References
    ----------
    FRAMING.md §5 L1.
    """
    if traj.budget_kind != "wall":
        raise ValueError(
            f"alpha is defined only for wall-clock budgets; got budget_kind={traj.budget_kind!r}"
        )
    if traj.budget is None or traj.tau_min is None:
        raise ValueError("alpha requires both budget and tau_min to be set")
    if traj.budget <= traj.tau_min:
        raise ValueError(
            f"budget {traj.budget} must exceed tau_min {traj.tau_min} for alpha to be defined"
        )
    raw = (traj.tau_wall - traj.tau_min) / (traj.budget - traj.tau_min)
    return max(0.0, min(1.0, raw))


def car(traj: Trajectory) -> float:
    """L2 — Step-Clock Conflation: CAR = tau_wall* / B.

    Defined when traj.budget_kind == "wall" and traj.budget > 0.

    CAR ~ 1 means the agent honored the wall-clock budget.
    CAR -> 0 means the agent silently degraded into a step-count terminator.

    References
    ----------
    FRAMING.md §5 L2.
    """
    if traj.budget_kind != "wall":
        raise ValueError(
            f"CAR is defined only for wall-clock budgets; got budget_kind={traj.budget_kind!r}"
        )
    if traj.budget is None or traj.budget <= 0:
        raise ValueError("CAR requires a positive wall-clock budget")
    return traj.tau_wall / traj.budget


def confabulation_ratio(traj: Trajectory) -> float:
    """L3 — Temporal Confabulation: rho = log10(tau_self / tau_wall).

    Defined when traj.tau_self is not None and both tau_self, tau_wall > 0.

    rho = 0 means the agent's self-report matches actual duration.
    rho > 0 means the agent over-reports its own work duration.

    References
    ----------
    FRAMING.md §5 L3.
    """
    if traj.tau_self is None:
        raise ValueError("rho is undefined when self_narrated_duration is None")
    if traj.tau_self <= 0:
        raise ValueError(f"tau_self must be positive; got {traj.tau_self}")
    if traj.tau_wall <= 0:
        raise ValueError(
            f"rho requires positive tau_wall; got {traj.tau_wall}. "
            "A trajectory with zero wall-clock duration cannot be self-confabulated."
        )
    return math.log10(traj.tau_self / traj.tau_wall)


def chronoceptive_calibration_error(
    trajectories: Iterable[Trajectory],
    weights: tuple[float, float, float] = (1.0 / 3, 1.0 / 3, 1.0 / 3),
) -> float:
    """The central scalar epsilon (FRAMING.md §4).

    epsilon(A; T, B) = E[ w1 * |alpha - 0| + w2 * |CAR - 1| + w3 * |rho| ]

    Each trajectory contributes the terms whose metrics are defined for it.
    Trajectories without wall-clock budget contribute neither alpha nor CAR;
    trajectories without a self-narrated duration contribute no rho.

    The expectation is taken over the trajectories for which each respective
    metric is defined; missing terms are dropped rather than imputed.

    Parameters
    ----------
    trajectories : iterable of Trajectory
    weights : tuple (w1, w2, w3)
        Must sum to 1. Reference configuration: (1/3, 1/3, 1/3).

    Returns
    -------
    float
        The aggregated epsilon. Range: roughly [0, ~1.5] in practice;
        chronoceptively perfect agents satisfy epsilon ~ 0.
    """
    w1, w2, w3 = weights
    if not math.isclose(w1 + w2 + w3, 1.0, abs_tol=1e-6):
        raise ValueError(f"weights must sum to 1; got {w1 + w2 + w3}")

    alpha_terms: list[float] = []
    car_terms: list[float] = []
    rho_terms: list[float] = []

    for traj in trajectories:
        primary_axis: TemporalAxis | None = None
        if traj.capability_code is not None:
            primary_axis = capability_by_id(traj.capability_code).axis

        def _route_to(axis: TemporalAxis) -> bool:
            return primary_axis is None or primary_axis is axis

        if (
            _route_to(TemporalAxis.WALL)
            and traj.budget_kind == "wall"
            and traj.tau_min is not None
            and traj.budget is not None
            and traj.budget > traj.tau_min
        ):
            alpha_terms.append(abs(parkinson_coefficient(traj) - 0.0))
        if (
            _route_to(TemporalAxis.STEP)
            and traj.budget_kind == "wall"
            and traj.budget is not None
            and traj.budget > 0
        ):
            car_terms.append(abs(car(traj) - 1.0))
        if (
            _route_to(TemporalAxis.SELF)
            and traj.tau_self is not None
            and traj.tau_self > 0
            and traj.tau_wall > 0
        ):
            rho_terms.append(abs(confabulation_ratio(traj)))

    if not (alpha_terms or car_terms or rho_terms):
        raise ValueError(
            "no trajectories had any of the three metrics defined; epsilon undefined"
        )

    mean_alpha = sum(alpha_terms) / len(alpha_terms) if alpha_terms else 0.0
    mean_car = sum(car_terms) / len(car_terms) if car_terms else 0.0
    mean_rho = sum(rho_terms) / len(rho_terms) if rho_terms else 0.0

    return w1 * mean_alpha + w2 * mean_car + w3 * mean_rho


epsilon = chronoceptive_calibration_error
"""Alias matching FRAMING.md §4 notation."""
