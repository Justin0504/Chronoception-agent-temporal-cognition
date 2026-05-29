"""Tests for the A/B Injection Tell evaluation setting.

Pins the structure required by FRAMING.md §3.1 and Prediction P1.
"""

from __future__ import annotations

import math

import pytest

from chronoception.bench import (
    EvalSetting,
    Step,
    Trajectory,
    epsilon_by_setting,
)


def _traj(
    *,
    setting: EvalSetting | None,
    actual: float,
    self_dur: float,
    capability_code: str = "T3.1",
) -> Trajectory:
    steps = [Step("s0", "a0", 0.0), Step("s1", "a1", actual)]
    meta: dict = {}
    if setting is not None:
        meta["setting"] = setting.value
    return Trajectory(
        task_id="t",
        agent_id="A",
        steps=steps,
        capability_code=capability_code,
        self_narrated_duration=self_dur,
        metadata=meta,
    )


def test_eval_setting_enum_values() -> None:
    """The two settings are exactly the FRAMING §3.1 partition."""
    assert {s.value for s in EvalSetting} == {"no_injection", "with_injection"}


def test_epsilon_by_setting_splits_correctly() -> None:
    """epsilon is computed per setting, not pooled."""
    # NO_INJECTION agent confabulates 10x
    t_a = _traj(setting=EvalSetting.NO_INJECTION, actual=10.0, self_dur=100.0)
    # WITH_INJECTION agent confabulates 2x
    t_b = _traj(setting=EvalSetting.WITH_INJECTION, actual=10.0, self_dur=20.0)
    result = epsilon_by_setting([t_a, t_b])
    assert set(result.keys()) == {EvalSetting.NO_INJECTION, EvalSetting.WITH_INJECTION}
    expected_a = (1.0 / 3) * abs(math.log10(10.0))
    expected_b = (1.0 / 3) * abs(math.log10(2.0))
    assert result[EvalSetting.NO_INJECTION] == pytest.approx(expected_a)
    assert result[EvalSetting.WITH_INJECTION] == pytest.approx(expected_b)


def test_epsilon_by_setting_skips_unlabeled_trajectories() -> None:
    """Trajectories without a setting label are excluded, not pooled."""
    labeled = _traj(setting=EvalSetting.NO_INJECTION, actual=10.0, self_dur=10.0)
    unlabeled = _traj(setting=None, actual=10.0, self_dur=100.0)
    result = epsilon_by_setting([labeled, unlabeled])
    assert set(result.keys()) == {EvalSetting.NO_INJECTION}
    assert result[EvalSetting.NO_INJECTION] == pytest.approx(0.0, abs=1e-9)


def test_epsilon_by_setting_rejects_unknown_setting_string() -> None:
    """An unrecognized setting metadata raises rather than silently dropping."""
    steps = [Step("s0", "a0", 0.0), Step("s1", "a1", 10.0)]
    bad = Trajectory(
        task_id="t",
        agent_id="A",
        steps=steps,
        capability_code="T3.1",
        self_narrated_duration=10.0,
        metadata={"setting": "with_clock_god_mode"},
    )
    with pytest.raises(ValueError, match="unrecognized setting"):
        epsilon_by_setting([bad])
