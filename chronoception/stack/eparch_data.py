"""E-ARCH data construction and eval analysis (pure, torch-free).

Route 4 (architectural primitive) trains a model to READ wall-clock from a
dedicated input token rather than estimate it. The defensible test that it is
reading -- not just learning the training distribution like the loss route (A.1)
-- is EXTRAPOLATION: inject elapsed values outside the training range and check
the model still reports them. The pieces here build the training targets and run
that extrapolation analysis; they are deliberately torch-free so they are unit-
testable without the cluster. The torch model/injection lives in `time_token.py`.
"""

from __future__ import annotations

from math import log10
from statistics import median
from typing import Any

from chronoception.stack.time_channel import TimeChannel

__all__ = [
    "time_features_for_elapsed",
    "make_training_example",
    "rho",
    "extrapolation_report",
]


def time_features_for_elapsed(elapsed_s: float) -> list[float]:
    """The time-token feature vector for a single-turn report at `elapsed_s`.

    Derived through TimeChannel so the training input and the inference input
    are produced by the same code path (consistency is the whole point of the
    architectural channel).
    """
    ch = TimeChannel(t0_epoch=0.0)
    return ch.observe(epoch=elapsed_s, step_index=1).feature_vector()


def make_training_example(prompt: str, response: str, tau_wall: float) -> dict[str, Any]:
    """One E-ARCH SFT example.

    Unlike A.1 (which puts a *noisy estimate* in the target so the model learns
    to guess), E-ARCH puts the ACCURATE duration in the target and supplies the
    same value through the time token, so the model learns to read the token and
    verbalize it. The elapsed value varies per example, so the target cannot be
    memorized as a constant -- it must come from the token.
    """
    target = f"{response}\n\nThis task took {tau_wall:.1f} seconds."
    return {
        "prompt": prompt,
        "target": target,
        "tau_wall": tau_wall,
        "time_features": time_features_for_elapsed(tau_wall),
    }


def rho(tau_self: float | None, tau_wall: float | None) -> float | None:
    if not isinstance(tau_self, (int, float)) or tau_self is None or tau_self <= 0:
        return None
    if not isinstance(tau_wall, (int, float)) or tau_wall is None or tau_wall <= 0:
        return None
    return log10(tau_self / tau_wall)


def _median_abs_rho(rows: list[dict[str, Any]]) -> float | None:
    vals = [abs(r) for r in (rho(x.get("tau_self"), x.get("injected_elapsed")) for x in rows) if r is not None]
    return median(vals) if vals else None


def extrapolation_report(
    rows: list[dict[str, Any]], train_lo: float, train_hi: float
) -> dict[str, Any]:
    """Split eval rows by whether the injected elapsed was inside the training
    range, and report median |rho| for each.

    Each row must carry `injected_elapsed` (the value put into the time token at
    eval) and `tau_self` (what the model reported). |rho| is computed against the
    INJECTED elapsed: a model that reads the token reports the injected value, so
    |rho| -> 0 both in- and out-of-range. A model that merely learned the training
    distribution grounds in-range but fails out-of-range.
    """
    in_range = [r for r in rows if train_lo <= r.get("injected_elapsed", -1) <= train_hi]
    out_range = [r for r in rows if not (train_lo <= r.get("injected_elapsed", -1) <= train_hi)]
    return {
        "train_range": [train_lo, train_hi],
        "n_in_range": len(in_range),
        "n_out_range": len(out_range),
        "median_abs_rho_in_range": _median_abs_rho(in_range),
        "median_abs_rho_out_range": _median_abs_rho(out_range),
        # Reads the channel if it grounds OUT of range too (the discriminating test).
        "reads_channel": (
            (_median_abs_rho(out_range) is not None and _median_abs_rho(out_range) < 0.3)
        ),
    }
