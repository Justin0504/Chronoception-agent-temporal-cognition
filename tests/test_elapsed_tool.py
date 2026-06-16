"""Tests for the harness-bracketed elapsed-time tool experiment (route 2 -> 4)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _ROOT / "scripts"
for p in (str(_ROOT), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import analyze_elapsed_tool as ana  # noqa: E402
import run_elapsed_tool as run  # noqa: E402


def test_condition_tools() -> None:
    assert run._condition_tools("no_tool") is None
    assert run._condition_tools("clock_tool")[0]["function"]["name"] == "get_current_time"
    assert run._condition_tools("elapsed_tool")[0]["function"]["name"] == "get_elapsed_time"


def test_is_reasoning_model() -> None:
    assert run._is_reasoning_model("o4-mini") is True
    assert run._is_reasoning_model("gpt-4o-mini") is False


def test_extract_duration_canonical_and_fallback() -> None:
    # Canonical retrospective phrasing.
    assert run._extract_duration("The task took me 12 seconds.") == 12.0
    # Fallback for the "Task duration: X seconds" phrasing the elapsed-tool
    # answers use, which the canonical parser misses.
    assert run._extract_duration("Here are the books.\n\nTask duration: 6.331 seconds.") == 6.331
    # Takes the LAST number+seconds (the duration report is at the end).
    assert run._extract_duration("step 1 done. Total: 9 seconds.") == 9.0
    assert run._extract_duration("no duration mentioned here") is None


def test_rho() -> None:
    assert ana._rho({"tau_self": 100.0, "tau_wall": 10.0}) == 1.0
    assert ana._rho({"tau_self": None, "tau_wall": 5.0}) is None


def test_summary() -> None:
    recs = [
        {"n_tool_calls": 0, "tau_self": 100.0, "tau_wall": 5.0},  # |rho| ~1.3
        {"n_tool_calls": 1, "tau_self": 5.1, "tau_wall": 5.0},    # grounded
        {"n_tool_calls": 1, "tau_self": 4.9, "tau_wall": 5.0},    # grounded
    ]
    s = ana._summary(recs)
    assert s["n"] == 3
    assert s["frac_used"] == 2 / 3
    assert s["frac_grounded"] == 2 / 3


def _write(base: Path, model: str, cond: str, recs: list[dict]) -> None:
    d = base / model / cond / "T3.1"
    d.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(recs):
        (d / f"T3.1.{i:03d}.json").write_text(json.dumps(r), encoding="utf-8")


def test_verdict_elapsed_fixes_it(tmp_path: Path) -> None:
    # clock_tool stays ungrounded (Hidden-Time); elapsed_tool collapses |rho|.
    _write(tmp_path, "o4-mini", "clock_tool",
           [{"n_tool_calls": 2, "tau_self": 3.0, "tau_wall": 20.0} for _ in range(10)])  # |rho|~0.82
    _write(tmp_path, "o4-mini", "elapsed_tool",
           [{"n_tool_calls": 1, "tau_self": 19.5, "tau_wall": 20.0} for _ in range(10)])  # ~grounded
    res = ana.analyze(tmp_path)
    assert res["per_model"]["o4-mini"]["verdict"].startswith("ELAPSED TOOL FIXES IT")
