"""Tests for the architectural time primitive interface (ChronoStack route 4)."""

from __future__ import annotations

import pytest

from chronoception.stack.time_channel import (
    FEATURE_NAMES,
    TimeChannel,
    TimeObservation,
)


def test_elapsed_and_delta_tracking() -> None:
    ch = TimeChannel(t0_epoch=1000.0)
    o1 = ch.observe(epoch=1003.0, step_index=1)
    assert o1.elapsed_s == 3.0
    assert o1.delta_s == 3.0  # first delta is from t0
    o2 = ch.observe(epoch=1010.0, step_index=2)
    assert o2.elapsed_s == 10.0
    assert o2.delta_s == 7.0  # since the previous observation
    assert o2.step_index == 2


def test_budget_remaining_and_overrun() -> None:
    ch = TimeChannel(t0_epoch=0.0, budget_s=60.0)
    mid = ch.observe(epoch=15.0, step_index=1)
    assert mid.remaining_s == 45.0
    assert mid.remaining_frac == pytest.approx(0.75)
    assert mid.over_budget is False
    over = ch.observe(epoch=90.0, step_index=2)
    assert over.remaining_s == -30.0
    assert over.over_budget is True


def test_no_budget_sentinel() -> None:
    ch = TimeChannel(t0_epoch=0.0)
    o = ch.observe(epoch=5.0, step_index=1)
    assert o.budget_s is None
    assert o.remaining_frac is None
    # The feature vector encodes "no budget" as -1.0.
    fv = o.feature_vector()
    assert len(fv) == len(FEATURE_NAMES)
    assert fv[FEATURE_NAMES.index("remaining_frac")] == -1.0


def test_feature_vector_order_matches_schema() -> None:
    ch = TimeChannel(t0_epoch=0.0, budget_s=100.0)
    o = ch.observe(epoch=20.0, step_index=3)
    fv = o.feature_vector()
    assert fv == [20.0, 20.0, 3.0, pytest.approx(0.8)]
    assert FEATURE_NAMES == ("elapsed_s", "delta_s", "step_index", "remaining_frac")


def test_render_structured_string() -> None:
    ch = TimeChannel(t0_epoch=0.0, budget_s=60.0)
    assert ch.observe(epoch=12.0, step_index=2).render() == (
        "<time elapsed=12.0s step=2 budget=60s remaining=48.0s>"
    )
    # Overrun is flagged in the rendered form too.
    assert "OVER_BUDGET" in ch.observe(epoch=75.0, step_index=3).render()
    # No-budget rendering omits budget fields.
    nb = TimeChannel(t0_epoch=0.0).observe(epoch=5.0, step_index=1).render()
    assert nb == "<time elapsed=5.0s step=1>"


def test_validation() -> None:
    with pytest.raises(ValueError):
        TimeChannel(t0_epoch=0.0, budget_s=-1.0)
    ch = TimeChannel(t0_epoch=100.0)
    with pytest.raises(ValueError):
        ch.observe(epoch=50.0, step_index=1)  # epoch before t0
    with pytest.raises(ValueError):
        ch.observe(epoch=100.0, step_index=-1)  # negative step
