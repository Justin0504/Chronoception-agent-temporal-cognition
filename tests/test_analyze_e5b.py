"""Tests for the E5b analyzer (scripts/analyze_e5b.py).

The analyzer's job is to refuse to report a Reverse-Scaling trend unless the
reasoning-intensity manipulation actually moved reasoning compute. These tests
pin that verdict logic and the surface-answer / rho extraction it depends on.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add scripts/ to the import path so we can import analyze_e5b as a module.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import analyze_e5b  # noqa: E402


# ---------- surface-answer stripping ----------


def test_surface_answer_strips_chain_of_thought() -> None:
    action = "Let me think hard about this.</think>\n\nThe task took me 12 seconds."
    assert analyze_e5b._surface_answer(action) == "\n\nThe task took me 12 seconds."


def test_surface_answer_passthrough_when_no_marker() -> None:
    action = "The task took me 12 seconds."
    assert analyze_e5b._surface_answer(action) == action


def test_reasoning_chars_counts_only_thinking() -> None:
    action = "abcde</think>final answer here"
    assert analyze_e5b._reasoning_chars(action) == len("abcde")
    assert analyze_e5b._reasoning_chars("no marker") == 0


# ---------- completion-token extraction ----------


def test_completion_tokens_reads_usage() -> None:
    traj = {"metadata": {"response_metadata": {"usage": {"completion_tokens": 742}}}}
    assert analyze_e5b._completion_tokens(traj) == 742


def test_completion_tokens_missing_returns_none() -> None:
    assert analyze_e5b._completion_tokens({"metadata": {}}) is None


# ---------- rho is parsed from the surface, not the thinking ----------


def test_rho_uses_surface_answer_not_thinking() -> None:
    # The chain-of-thought mentions 999 s; the answer says 5 s. tau_wall = 50 s.
    # rho must use the answer (log10(5/50) = -1), not the thinking.
    traj = {
        "tau_wall": 50.0,
        "steps": [
            {"state": "u", "action": "task"},
            {
                "state": "a",
                "action": "I estimate maybe 999 seconds of work.</think>\n\nThe task took me 5 seconds.",
            },
        ],
    }
    rho = analyze_e5b._rho_from_surface(traj)
    assert rho is not None
    assert abs(rho - (-1.0)) < 1e-6


def test_rho_none_when_no_duration_claim() -> None:
    traj = {
        "tau_wall": 50.0,
        "steps": [{"state": "u", "action": "t"}, {"state": "a", "action": "done</think>\n\nno number"}],
    }
    assert analyze_e5b._rho_from_surface(traj) is None


# ---------- monotonicity helpers ----------


def test_monotone_increasing() -> None:
    assert analyze_e5b._is_monotone_increasing([1.0, 2.0, 3.0])
    assert not analyze_e5b._is_monotone_increasing([1.0, 1.0, 3.0])
    assert not analyze_e5b._is_monotone_increasing([3.0, 2.0, 1.0])


def test_monotone_nondecreasing() -> None:
    assert analyze_e5b._is_monotone_nondecreasing([1.0, 1.0, 3.0])
    assert not analyze_e5b._is_monotone_nondecreasing([3.0, 2.0, 1.0])


# ---------- end-to-end verdicts on synthetic fixtures ----------


def _write_level(
    base: Path, level: str, *, tau_wall: float, comp_tokens: int, reported_s: float
) -> None:
    for setting in ("no_injection", "with_injection"):
        d = base / f"deepseek-r1-14b-{level}" / "oss_x" / "T3.1" / setting
        d.mkdir(parents=True, exist_ok=True)
        action = f"{'think ' * comp_tokens}</think>\n\nThe task took me {reported_s} seconds."
        for i in range(5):
            traj = {
                "task_id": f"T3.1.{i:03d}",
                "tau_wall": tau_wall,
                "steps": [
                    {"state": "u", "action": "task"},
                    {"state": "a", "action": action},
                ],
                "metadata": {
                    "setting": setting,
                    "response_metadata": {
                        "finish_reason": "stop",
                        "usage": {"completion_tokens": comp_tokens},
                    },
                },
            }
            (d / f"T3.1.{i:03d}.json").write_text(json.dumps(traj), encoding="utf-8")


def test_verdict_confirmed(tmp_path: Path) -> None:
    # tau_self anchored low (5 s); wall grows with compute -> |rho| grows.
    _write_level(tmp_path, "brief", tau_wall=8.0, comp_tokens=300, reported_s=5)
    _write_level(tmp_path, "natural", tau_wall=20.0, comp_tokens=900, reported_s=5)
    _write_level(tmp_path, "thorough", tau_wall=45.0, comp_tokens=2200, reported_s=5)
    result = analyze_e5b.analyze(tmp_path)
    assert result["compute_increased"] is True
    assert result["verdict"] == "REVERSE-SCALING CONFIRMED"


def test_verdict_manipulation_failed(tmp_path: Path) -> None:
    # Flat compute across levels -> cannot test the theorem (the E5 outcome).
    _write_level(tmp_path, "brief", tau_wall=18.0, comp_tokens=700, reported_s=30)
    _write_level(tmp_path, "natural", tau_wall=18.0, comp_tokens=700, reported_s=30)
    _write_level(tmp_path, "thorough", tau_wall=18.0, comp_tokens=700, reported_s=30)
    result = analyze_e5b.analyze(tmp_path)
    assert result["compute_increased"] is False
    assert result["verdict"] == "MANIPULATION FAILED"


def test_verdict_refuted(tmp_path: Path) -> None:
    # Compute grows but tau_self tracks wall (reported ~= wall) -> |rho| ~ 0,
    # and here we force |rho| to fall by anchoring tau_self above wall early.
    _write_level(tmp_path, "brief", tau_wall=8.0, comp_tokens=300, reported_s=80)
    _write_level(tmp_path, "natural", tau_wall=20.0, comp_tokens=900, reported_s=22)
    _write_level(tmp_path, "thorough", tau_wall=45.0, comp_tokens=2200, reported_s=46)
    result = analyze_e5b.analyze(tmp_path)
    assert result["compute_increased"] is True
    assert result["verdict"] == "REVERSE-SCALING REFUTED"
