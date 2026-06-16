"""Tests for the ChronoStack tool-interface (get_current_time) experiment.

Covers the run script's condition config and the analyzer's rho, use-rate
summary, and the "availability != use" diagnosis.
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

import analyze_tool_interface as ana  # noqa: E402
import run_tool_interface as run  # noqa: E402


# ---------- condition config ----------


def test_condition_config() -> None:
    assert run._condition_config("no_tool") == (False, run._NEUTRAL_SYSTEM)
    offer, sysp = run._condition_config("tool")
    assert offer is True and sysp == run._NEUTRAL_SYSTEM
    offer2, sysp2 = run._condition_config("tool_prompted")
    assert offer2 is True and "get_current_time" in sysp2


def test_iso_from_epoch_is_deterministic() -> None:
    # _iso must format from an explicit epoch (no argless datetime.now()).
    assert run._iso(0.0).startswith("1970-01-01T00:00:00")


# ---------- rho ----------


def test_rho() -> None:
    assert ana._rho({"tau_self": 100.0, "tau_wall": 10.0}) == 1.0
    assert ana._rho({"tau_self": 10.0, "tau_wall": 10.0}) == 0.0
    assert ana._rho({"tau_self": None, "tau_wall": 5.0}) is None
    assert ana._rho({"tau_self": 5.0, "tau_wall": 0.0}) is None


# ---------- summary ----------


def _rec(calls: int, tau_self: float, tau_wall: float) -> dict:
    return {"n_tool_calls": calls, "tau_self": tau_self, "tau_wall": tau_wall}


def test_summary_use_rates_and_rho_split() -> None:
    recs = [
        _rec(0, 100.0, 5.0),   # no call, big over-report
        _rec(2, 5.2, 5.0),     # used >=2, grounded
        _rec(2, 4.9, 5.0),     # used >=2, grounded
        _rec(1, 80.0, 5.0),    # one call, still off
    ]
    s = ana._summary(recs)
    assert s["n"] == 4
    assert s["frac_used_1plus"] == 3 / 4
    assert s["frac_used_2plus"] == 2 / 4
    # The >=2 subgroup is near-grounded; the <2 subgroup is way off.
    assert s["median_abs_rho_used2plus"] < 0.1
    assert s["median_abs_rho_under2"] > 1.0


# ---------- diagnosis ----------


def _write(base: Path, model: str, cond: str, recs: list[dict]) -> None:
    d = base / model / cond / "T3.1"
    d.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(recs):
        (d / f"T3.1.{i:03d}.json").write_text(json.dumps(r), encoding="utf-8")


def test_diagnosis_availability_not_use(tmp_path: Path) -> None:
    # tool condition: only 2/10 call the clock >=2x; those are grounded, the rest
    # are way off -> AVAILABILITY != USE.
    recs = [_rec(2, 5.1, 5.0), _rec(2, 4.8, 5.0)]            # grounded
    recs += [_rec(0, 100.0, 5.0) for _ in range(8)]          # never used, off
    _write(tmp_path, "m", "tool", recs)
    res = ana.analyze(tmp_path)
    diag = res["per_model"]["m"]["diagnosis"]
    assert diag is not None and diag.startswith("AVAILABILITY != USE")


def test_diagnosis_tool_suffices(tmp_path: Path) -> None:
    # Most call it correctly and are grounded -> TOOL SUFFICES.
    recs = [_rec(2, 5.1, 5.0) for _ in range(9)] + [_rec(0, 90.0, 5.0)]
    _write(tmp_path, "m", "tool", recs)
    res = ana.analyze(tmp_path)
    assert res["per_model"]["m"]["diagnosis"].startswith("TOOL SUFFICES")
