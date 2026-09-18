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
    renormalise: bool = True,
) -> float:
    """The central scalar epsilon (FRAMING.md §4).

    epsilon(A; T, B) = E[ w1 * |alpha - 0| + w2 * |CAR - 1| + w3 * |rho| ]

    Each trajectory contributes the terms whose metrics are defined for it.
    Trajectories without wall-clock budget contribute neither alpha nor CAR;
    trajectories without a self-narrated duration contribute no rho.

    The expectation is taken over the trajectories for which each respective
    metric is defined. An axis with no defined trajectories at all is dropped
    and its weight redistributed over the remaining axes, so that epsilon is
    always a weighted mean over the axes actually measured. Pass
    renormalise=False for the pre-2026-09 convention, which instead scored a
    missing axis as 0.0 and left its weight in the denominator.

    Parameters
    ----------
    trajectories : iterable of Trajectory
    weights : tuple (w1, w2, w3)
        Must sum to 1. Reference configuration: (1/3, 1/3, 1/3).
    renormalise : bool
        Redistribute the weight of any axis with no data over the axes that
        have data (default). False reproduces the legacy impute-zero scale.

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

    # An axis with no defined trajectories is DROPPED, not imputed: its weight
    # is redistributed over the axes that do have data, matching the definition
    # given in the paper. Imputing a missing axis as 0.0 and leaving its weight
    # in the denominator (renormalise=False) would credit the agent with a
    # perfect score on an axis that was never measured.
    #
    # This is a NO-OP on the 90-trajectory pilot protocol and on every panel
    # reported in the paper: all three axes carry data there (T2.3 supplies both
    # alpha and CAR -- alpha via tau_min, CAR via the budget -- and T3.1
    # supplies rho), so no published epsilon changes. The branch exists so that
    # a future protocol which omits an axis entirely cannot silently deflate
    # epsilon by the weight of the axis it skipped.
    present = [
        (w1, sum(alpha_terms) / len(alpha_terms)) if alpha_terms else None,
        (w2, sum(car_terms) / len(car_terms)) if car_terms else None,
        (w3, sum(rho_terms) / len(rho_terms)) if rho_terms else None,
    ]
    present = [p for p in present if p is not None]

    if not renormalise:
        return sum(w * m for w, m in present)

    total_w = sum(w for w, _ in present)
    return sum(w * m for w, m in present) / total_w


epsilon = chronoceptive_calibration_error
"""Alias matching FRAMING.md §4 notation."""
