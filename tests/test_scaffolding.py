"""Tests for the ChronoStack scaffolding budget-honoring experiment.

Covers the run script's control-line parsing and the analyzer's Mann-Whitney
test, per-condition summary, and HELPS / HURTS / NO EFFECT verdicts.
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

import analyze_scaffolding as ana  # noqa: E402
import run_scaffolding_budget as run  # noqa: E402


# ---------- control-line parsing ----------


def test_parse_control() -> None:
    assert run._parse_control("did work\nCONTROL: DONE") == "DONE"
    assert run._parse_control("more to do\nCONTROL: CONTINUE") == "CONTINUE"
    assert run._parse_control("control: done") == "DONE"
    # Default when no control line is present: keep going.
    assert run._parse_control("no marker here") == "CONTINUE"


def test_user_turn_scaffold_vs_plain() -> None:
    plain = run._user_turn(False, budget=30, elapsed=10, step=3)
    scaf = run._user_turn(True, budget=30, elapsed=10, step=3)
    assert plain == "Continue working."
    assert "remaining 20.0s" in scaf and "step 3" in scaf


# ---------- Mann-Whitney ----------


def test_mann_whitney_separated_groups() -> None:
    a = [0.9, 0.95, 1.0, 1.05, 1.1, 0.92, 0.98, 1.02]
    b = [0.1, 0.15, 0.2, 0.05, 0.12, 0.18, 0.08, 0.14]
    p = ana._mann_whitney_p(a, b)
    assert p is not None and p < 0.05


def test_mann_whitney_identical_groups() -> None:
    a = [0.5, 0.5, 0.5, 0.5]
    p = ana._mann_whitney_p(a, list(a))
    assert p == 1.0


def test_mann_whitney_empty() -> None:
    assert ana._mann_whitney_p([], [1.0]) is None


# ---------- end-to-end verdicts ----------


def _write(base: Path, agent: str, cond: str, cars: list[float]) -> None:
    d = base / agent / cond
    d.mkdir(parents=True, exist_ok=True)
    for i, car in enumerate(cars):
        rec = {
            "condition": cond,
            "budget": 30.0,
            "n_steps": 8,
            "wall_at_stop": car * 30.0,
            "car": car,
            "stop_reason": "voluntary_done",
        }
        (d / f"conv_{i:03d}.json").write_text(json.dumps(rec), encoding="utf-8")


def test_verdict_scaffold_helps(tmp_path: Path) -> None:
    # off stops early (CAR ~0.15); on honors the budget (CAR ~1.0).
    _write(tmp_path, "m", "scaffold_off", [0.1, 0.15, 0.2, 0.12, 0.18, 0.14, 0.16, 0.11])
    _write(tmp_path, "m", "scaffold_on", [0.95, 1.0, 1.05, 0.98, 1.02, 0.97, 1.03, 1.0])
    res = ana.analyze(tmp_path, alpha=0.05)
    c = res["per_agent"]["m"]["comparison"]
    assert c["significant"] is True
    assert c["verdict"] == "SCAFFOLD HELPS"


def test_summary_dispersion_fields(tmp_path: Path) -> None:
    # Wide spread with two overruns -> nonzero stdev and frac_overrun = 2/5.
    _write(tmp_path, "m", "scaffold_off", [0.5, 0.9, 1.5, 0.6, 1.2])
    res = ana.analyze(tmp_path, alpha=0.05)
    s = res["per_agent"]["m"]["scaffold_off"]
    assert s["frac_overrun"] == 2 / 5
    assert s["car_min"] == 0.5 and s["car_max"] == 1.5
    assert s["car_stdev"] is not None and s["car_stdev"] > 0


def test_verdict_no_effect(tmp_path: Path) -> None:
    same = [0.2, 0.25, 0.18, 0.22, 0.19, 0.21, 0.23, 0.17]
    _write(tmp_path, "m", "scaffold_off", same)
    _write(tmp_path, "m", "scaffold_on", list(same))
    res = ana.analyze(tmp_path, alpha=0.05)
    assert res["per_agent"]["m"]["comparison"]["verdict"] == "NO EFFECT"


def test_permutation_dispersion_detects_tightening() -> None:
    # Wide-spread off vs tight on -> permutation test should be significant.
    off = [0.1, 0.4, 0.7, 1.0, 1.3, 1.6, 0.2, 1.5, 0.5, 1.8]
    on = [0.88, 0.90, 0.89, 0.91, 0.90, 0.88, 0.92, 0.89, 0.90, 0.91]
    p = ana._permutation_dispersion_p(on, off)
    assert p is not None and p < 0.05


def test_dispersion_verdict_tightens(tmp_path: Path) -> None:
    # The pilot pattern: off scatters (incl. overruns), on is tight -> TIGHTENS.
    _write(tmp_path, "m", "scaffold_off", [0.55, 0.79, 0.90, 1.51, 0.85, 0.90, 1.90, 1.01, 0.75, 0.90])
    _write(tmp_path, "m", "scaffold_on", [0.89, 0.82, 0.83, 0.89, 0.87, 0.83, 0.89, 0.90, 0.85, 0.82])
    res = ana.analyze(tmp_path, alpha=0.05)
    c = res["per_agent"]["m"]["comparison"]
    assert c["dispersion_verdict"] == "SCAFFOLD TIGHTENS"
    assert c["frac_overrun_off"] > 0 and c["frac_overrun_on"] == 0.0


def test_verdict_scaffold_hurts(tmp_path: Path) -> None:
    # off near ideal; on overruns badly (CAR ~2) -> larger |CAR-1|.
    _write(tmp_path, "m", "scaffold_off", [0.95, 1.0, 1.05, 0.98, 1.02, 0.97, 1.03, 1.0])
    _write(tmp_path, "m", "scaffold_on", [1.9, 2.0, 2.1, 1.95, 2.05, 1.98, 2.02, 2.0])
    res = ana.analyze(tmp_path, alpha=0.05)
    c = res["per_agent"]["m"]["comparison"]
    assert c["significant"] is True
    assert c["verdict"] == "SCAFFOLD HURTS"
