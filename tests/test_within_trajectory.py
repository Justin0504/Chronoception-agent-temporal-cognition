"""Tests for the within-trajectory drift analyzer (P8/P9).

Pins the OLS slope, the sign-test p-value, per-conversation slope extraction,
and the three P8 verdicts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _ROOT / "scripts"
for p in (str(_ROOT), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import analyze_within_trajectory as ana  # noqa: E402


# ---------- OLS slope ----------


def test_ols_slope_known() -> None:
    # y = 2x + 1 -> slope 2.
    assert abs(ana._ols_slope([0, 1, 2, 3], [1, 3, 5, 7]) - 2.0) < 1e-9


def test_ols_slope_undefined() -> None:
    assert ana._ols_slope([1.0], [1.0]) is None          # < 2 points
    assert ana._ols_slope([2, 2, 2], [1, 2, 3]) is None  # zero variance in x


# ---------- sign test ----------


def test_binom_two_sided_p() -> None:
    # All 5 in one direction: 2 * (1/32) = 0.0625.
    assert abs(ana._binom_two_sided_p(5, 5) - 0.0625) < 1e-9
    assert abs(ana._binom_two_sided_p(0, 5) - 0.0625) < 1e-9
    # Even split -> p = 1.0.
    assert abs(ana._binom_two_sided_p(2, 4) - 1.0) < 1e-9
    assert ana._binom_two_sided_p(0, 0) is None


# ---------- per-conversation slope ----------


def _conv(abs_rhos: list[float]) -> dict:
    return {
        "steps": [
            {"step_index": t, "rho_step": r} for t, r in enumerate(abs_rhos)
        ]
    }


def test_conversation_slope_increasing() -> None:
    slope, pts = ana._conversation_slope(_conv([0.1, 0.2, 0.3, 0.4]))
    assert slope is not None and slope > 0
    assert len(pts) == 4


def test_conversation_slope_too_few_points() -> None:
    slope, pts = ana._conversation_slope({"steps": [{"step_index": 0, "rho_step": 0.5}]})
    assert slope is None
    assert len(pts) == 1


def test_conversation_slope_skips_none() -> None:
    # Steps with rho_step None are dropped; only 1 valid point -> no slope.
    slope, pts = ana._conversation_slope(
        {"steps": [{"step_index": 0, "rho_step": None}, {"step_index": 1, "rho_step": 0.5}]}
    )
    assert slope is None
    assert pts == [(1, 0.5)]


# ---------- end-to-end verdicts ----------


def _write_convs(base: Path, agent: str, setting: str, per_conv_rhos: list[list[float]]) -> None:
    d = base / agent / setting
    d.mkdir(parents=True, exist_ok=True)
    for c, abs_rhos in enumerate(per_conv_rhos):
        rec = {
            "conversation_id": f"conv_{c:03d}",
            "agent_id": agent,
            "setting": setting,
            "n_steps": len(abs_rhos),
            "steps": [{"step_index": t, "rho_step": r} for t, r in enumerate(abs_rhos)],
        }
        (d / f"conv_{c:03d}.json").write_text(json.dumps(rec), encoding="utf-8")


def test_verdict_p8_supported(tmp_path: Path) -> None:
    # Six conversations all drift up -> sign test p = 0.03125 < 0.05 -> significant.
    convs = [[0.1, 0.3, 0.5, 0.7, 0.9] for _ in range(6)]
    _write_convs(tmp_path, "reasoner", "no_injection", convs)
    res = ana.analyze(tmp_path, "no_injection", tol=0.02, alpha=0.05)
    a = res["per_agent"]["reasoner"]
    assert a["median_slope"] > 0.02
    assert a["significant_at_alpha"] is True
    assert a["verdict"] == "P8 SUPPORTED"


def test_verdict_p8_refuted(tmp_path: Path) -> None:
    # Six conversations all drift down (the paper's cross-trajectory direction).
    convs = [[0.9, 0.7, 0.5, 0.3, 0.1] for _ in range(6)]
    _write_convs(tmp_path, "model", "no_injection", convs)
    res = ana.analyze(tmp_path, "no_injection", tol=0.02, alpha=0.05)
    a = res["per_agent"]["model"]
    assert a["median_slope"] < -0.02
    assert a["verdict"] == "P8 REFUTED"


def test_verdict_up_trend_not_significant(tmp_path: Path) -> None:
    # A 3-up / 2-down split: direction is up but the sign test is not significant
    # (this is the count=5 case that must NOT be called "supported").
    up = [0.1, 0.3, 0.5, 0.7, 0.9]
    down = [0.9, 0.7, 0.5, 0.3, 0.1]
    convs = [up, up, up, down, down]
    _write_convs(tmp_path, "model", "no_injection", convs)
    res = ana.analyze(tmp_path, "no_injection", tol=0.02, alpha=0.05)
    a = res["per_agent"]["model"]
    assert a["significant_at_alpha"] is False
    assert a["verdict"] == "UP-TREND (not significant)"


def test_verdict_flat(tmp_path: Path) -> None:
    convs = [[0.5, 0.5, 0.5, 0.5, 0.5] for _ in range(6)]
    _write_convs(tmp_path, "model", "no_injection", convs)
    res = ana.analyze(tmp_path, "no_injection", tol=0.02, alpha=0.05)
    assert res["per_agent"]["model"]["verdict"] == "FLAT/INCONCLUSIVE"
