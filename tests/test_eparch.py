"""Tests for the torch-free E-ARCH data/eval logic (chronoception.stack.eparch_data).

The torch model (time_token.py) is validated by its own smoke_test() on the
cluster; here we pin the data construction and the extrapolation analysis that
make the route-4 claim falsifiable.
"""

from __future__ import annotations

from math import log10

from chronoception.stack.eparch_data import (
    extrapolation_report,
    make_training_example,
    rho,
    time_features_for_elapsed,
)
from chronoception.stack.time_channel import FEATURE_NAMES


def test_time_features_for_elapsed() -> None:
    f = time_features_for_elapsed(12.0)
    assert len(f) == len(FEATURE_NAMES)
    # elapsed_s and delta_s both equal the single-turn elapsed; no budget -> -1.
    assert f[FEATURE_NAMES.index("elapsed_s")] == 12.0
    assert f[FEATURE_NAMES.index("delta_s")] == 12.0
    assert f[FEATURE_NAMES.index("step_index")] == 1.0
    assert f[FEATURE_NAMES.index("remaining_frac")] == -1.0


def test_make_training_example_accurate_target() -> None:
    ex = make_training_example("do X", "here is X", 7.3)
    assert ex["tau_wall"] == 7.3
    assert "7.3 seconds" in ex["target"]          # accurate, not noisy
    assert ex["time_features"][0] == 7.3          # the token carries the same value
    assert "here is X" in ex["target"]


def test_rho() -> None:
    assert rho(100.0, 10.0) == log10(10.0)
    assert rho(10.0, 10.0) == 0.0
    assert rho(None, 5.0) is None
    assert rho(5.0, 0.0) is None


def test_extrapolation_report_reads_channel() -> None:
    # A model that READS the token: tau_self ~= injected_elapsed in AND out of range.
    rows = []
    for e in [5, 10, 15, 20]:        # in-range (train 5..20)
        rows.append({"injected_elapsed": e, "tau_self": e * 1.02})
    for e in [60, 90, 120]:          # out-of-range
        rows.append({"injected_elapsed": e, "tau_self": e * 0.98})
    rep = extrapolation_report(rows, train_lo=5, train_hi=20)
    assert rep["n_in_range"] == 4 and rep["n_out_range"] == 3
    assert rep["median_abs_rho_out_range"] < 0.3
    assert rep["reads_channel"] is True


def test_extrapolation_report_memorized_distribution() -> None:
    # A model that learned the TRAINING distribution (~12s) ignores the token:
    # grounded in-range by luck, way off out-of-range.
    rows = [{"injected_elapsed": e, "tau_self": 12.0} for e in [10, 12, 14]]      # in-range
    rows += [{"injected_elapsed": e, "tau_self": 12.0} for e in [90, 120, 150]]   # out-of-range
    rep = extrapolation_report(rows, train_lo=8, train_hi=16)
    assert rep["median_abs_rho_out_range"] > 0.3   # fails out of range
    assert rep["reads_channel"] is False
