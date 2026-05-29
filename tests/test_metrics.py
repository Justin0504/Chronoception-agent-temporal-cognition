"""Unit tests for the three-law metrics.

Each test pins a single arithmetic property tied to FRAMING.md §5 so that
breaking changes to the metric definitions surface immediately.
"""

from __future__ import annotations

import math

import pytest

from chronoception.bench import (
    Step,
    Trajectory,
    car,
    chronoceptive_calibration_error,
    confabulation_ratio,
    parkinson_coefficient,
)


def _wall_traj(
    *,
    actual_seconds: float,
    budget_seconds: float,
    tau_min_seconds: float | None = None,
    tau_self: float | None = None,
    n_steps: int = 5,
    capability_code: str | None = None,
) -> Trajectory:
    """Build a synthetic Trajectory with a controlled wall-clock duration."""
    steps = [
        Step(state=f"s{i}", action=f"a{i}", timestamp=i * (actual_seconds / max(n_steps - 1, 1)))
        for i in range(n_steps)
    ]
    return Trajectory(
        task_id="t",
        agent_id="A",
        steps=steps,
        capability_code=capability_code,
        budget=budget_seconds,
        budget_kind="wall",
        tau_min=tau_min_seconds,
        self_narrated_duration=tau_self,
    )


# --------------- L1: Agentic Parkinson coefficient ---------------


def test_parkinson_zero_when_actual_equals_tau_min() -> None:
    """alpha = 0 when the agent finished as fast as physically possible."""
    traj = _wall_traj(actual_seconds=60.0, budget_seconds=600.0, tau_min_seconds=60.0)
    assert parkinson_coefficient(traj) == pytest.approx(0.0)


def test_parkinson_one_when_actual_equals_budget() -> None:
    """alpha = 1 when the agent used the entire budget."""
    traj = _wall_traj(actual_seconds=600.0, budget_seconds=600.0, tau_min_seconds=60.0)
    assert parkinson_coefficient(traj) == pytest.approx(1.0)


def test_parkinson_clamped_above_one() -> None:
    """alpha is clamped to [0, 1] when actual exceeds budget."""
    traj = _wall_traj(actual_seconds=900.0, budget_seconds=600.0, tau_min_seconds=60.0)
    assert parkinson_coefficient(traj) == pytest.approx(1.0)


def test_parkinson_clamped_below_zero() -> None:
    """alpha is clamped to [0, 1] when actual undercuts tau_min."""
    traj = _wall_traj(actual_seconds=30.0, budget_seconds=600.0, tau_min_seconds=60.0)
    assert parkinson_coefficient(traj) == pytest.approx(0.0)


def test_parkinson_requires_wall_budget() -> None:
    """alpha is undefined for non-wall budgets."""
    traj = Trajectory(
        task_id="t",
        agent_id="A",
        steps=[Step("s", "a", 0.0), Step("s", "a", 1.0)],
        budget=5.0,
        budget_kind="step",
        tau_min=1.0,
    )
    with pytest.raises(ValueError):
        parkinson_coefficient(traj)


# --------------- L2: Clock-Adherence Ratio ---------------


def test_car_one_when_actual_equals_budget() -> None:
    """CAR = 1 when wall-clock budget is fully honored."""
    traj = _wall_traj(actual_seconds=600.0, budget_seconds=600.0)
    assert car(traj) == pytest.approx(1.0)


def test_car_zero_in_the_limit_of_step_decoupling() -> None:
    """CAR -> 0 when actual is bounded independently of B."""
    traj = _wall_traj(actual_seconds=60.0, budget_seconds=10_800.0)  # 3 hours
    assert car(traj) == pytest.approx(60.0 / 10_800.0)
    assert car(traj) < 0.01  # decoupling signature


def test_car_requires_positive_budget() -> None:
    """CAR requires positive wall-clock budget."""
    traj = Trajectory(
        task_id="t",
        agent_id="A",
        steps=[Step("s", "a", 0.0), Step("s", "a", 1.0)],
        budget=None,
        budget_kind="none",
    )
    with pytest.raises(ValueError):
        car(traj)


# --------------- L3: Temporal Confabulation ratio ---------------


def test_confabulation_zero_when_self_matches_wall() -> None:
    """rho = 0 when self-report equals actual wall-clock."""
    traj = _wall_traj(actual_seconds=60.0, budget_seconds=600.0, tau_self=60.0)
    assert confabulation_ratio(traj) == pytest.approx(0.0)


def test_confabulation_30x_overreport() -> None:
    """rho = log10(30) ~ 1.477 for a 30x over-report."""
    traj = _wall_traj(actual_seconds=10.0, budget_seconds=600.0, tau_self=300.0)
    assert confabulation_ratio(traj) == pytest.approx(math.log10(30.0))


def test_confabulation_negative_when_under_reported() -> None:
    """rho < 0 when self-report under-reports actual."""
    traj = _wall_traj(actual_seconds=60.0, budget_seconds=600.0, tau_self=6.0)
    assert confabulation_ratio(traj) == pytest.approx(-1.0)


def test_confabulation_requires_self_duration() -> None:
    """rho is undefined when no self-narrated duration was parsed."""
    traj = _wall_traj(actual_seconds=60.0, budget_seconds=600.0, tau_self=None)
    with pytest.raises(ValueError):
        confabulation_ratio(traj)


# --------------- epsilon: aggregated calibration error ---------------


def test_epsilon_zero_for_perfectly_calibrated_agent() -> None:
    """An agent with alpha=0, CAR=1, rho=0 has epsilon = 0.

    L1 and L2 normatively disagree on the same trajectory — L1 wants
    actual == tau_min (finish fast), L2 wants actual == B (honor the
    instructed budget). The agent is perfectly calibrated only when each
    trajectory is routed to the metric for its own capability axis. We
    set capability_code accordingly.
    """
    t_l1 = _wall_traj(
        actual_seconds=60.0,
        budget_seconds=600.0,
        tau_min_seconds=60.0,
        tau_self=60.0,
        capability_code="T1.3",  # tau_wall axis; routes to alpha only
    )
    t_l2 = _wall_traj(
        actual_seconds=600.0,
        budget_seconds=600.0,
        tau_self=600.0,
        capability_code="T2.3",  # tau_step axis; routes to CAR only
    )
    t_l3 = _wall_traj(
        actual_seconds=60.0,
        budget_seconds=600.0,
        tau_self=60.0,
        capability_code="T3.1",  # tau_self axis; routes to rho only
    )
    result = chronoceptive_calibration_error([t_l1, t_l2, t_l3])
    assert result == pytest.approx(0.0, abs=1e-9)


def test_epsilon_requires_weights_summing_to_one() -> None:
    traj = _wall_traj(actual_seconds=60.0, budget_seconds=600.0, tau_min_seconds=60.0, tau_self=60.0)
    with pytest.raises(ValueError):
        chronoceptive_calibration_error([traj], weights=(0.5, 0.5, 0.5))


def test_epsilon_picks_up_l3_only_when_l1_l2_undefined() -> None:
    """A trajectory without a wall budget should still contribute via rho."""
    traj = Trajectory(
        task_id="t",
        agent_id="A",
        steps=[Step("s", "a", 0.0), Step("s", "a", 10.0)],
        budget=None,
        budget_kind="none",
        self_narrated_duration=100.0,  # 10x over-report
    )
    result = chronoceptive_calibration_error([traj])
    expected = (1.0 / 3) * abs(math.log10(10.0))
    assert result == pytest.approx(expected)
