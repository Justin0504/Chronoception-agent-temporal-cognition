"""Tests for the run_pilot CLI.

Use the echo backend so the tests do not depend on real model API keys.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add scripts/ to the import path so we can import run_pilot as a module.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import run_pilot  # noqa: E402


def test_echo_run_creates_trajectories(tmp_path: Path) -> None:
    run_pilot.main(
        [
            "--backend",
            "echo",
            "--capability",
            "T1.1",
            "--setting",
            "no_injection",
            "--count",
            "3",
            "--output-dir",
            str(tmp_path),
        ]
    )
    files = list(tmp_path.rglob("*.json"))
    assert len(files) == 3


def test_echo_run_writes_valid_trajectory_json(tmp_path: Path) -> None:
    run_pilot.main(
        [
            "--backend",
            "echo",
            "--capability",
            "T2.3",
            "--setting",
            "with_injection",
            "--count",
            "2",
            "--output-dir",
            str(tmp_path),
        ]
    )
    files = sorted(tmp_path.rglob("*.json"))
    assert files, "no trajectories written"
    payload = json.loads(files[0].read_text())
    assert payload["capability_code"] == "T2.3"
    assert payload["budget_kind"] == "wall"
    assert payload["metadata"]["setting"] == "with_injection"
    assert "tau_wall" in payload
    assert "tau_step" in payload
    assert "steps" in payload and len(payload["steps"]) == 2


def test_resume_skips_existing(tmp_path: Path) -> None:
    args = [
        "--backend",
        "echo",
        "--capability",
        "T1.1",
        "--setting",
        "no_injection",
        "--count",
        "2",
        "--output-dir",
        str(tmp_path),
    ]
    run_pilot.main(args)
    files_first = sorted(tmp_path.rglob("*.json"))
    mtimes_first = {p: p.stat().st_mtime_ns for p in files_first}
    run_pilot.main(args)
    files_second = sorted(tmp_path.rglob("*.json"))
    assert files_first == files_second
    mtimes_second = {p: p.stat().st_mtime_ns for p in files_second}
    assert mtimes_first == mtimes_second, "resume should not rewrite files"


def test_force_overwrites_existing(tmp_path: Path) -> None:
    base_args = [
        "--backend",
        "echo",
        "--capability",
        "T1.1",
        "--setting",
        "no_injection",
        "--count",
        "2",
        "--output-dir",
        str(tmp_path),
    ]
    run_pilot.main(base_args)
    files_first = sorted(tmp_path.rglob("*.json"))
    mtimes_first = {p: p.stat().st_mtime_ns for p in files_first}
    run_pilot.main([*base_args, "--force"])
    mtimes_second = {p: p.stat().st_mtime_ns for p in sorted(tmp_path.rglob("*.json"))}
    assert any(mtimes_second[p] > mtimes_first[p] for p in mtimes_first)


def test_unknown_capability_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run_pilot.main(
            [
                "--backend",
                "echo",
                "--capability",
                "T9.9",
                "--setting",
                "no_injection",
                "--count",
                "1",
                "--output-dir",
                str(tmp_path),
            ]
        )


def test_unknown_setting_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run_pilot.main(
            [
                "--backend",
                "echo",
                "--capability",
                "T1.1",
                "--setting",
                "weird_mode",
                "--count",
                "1",
                "--output-dir",
                str(tmp_path),
            ]
        )


def test_openai_requires_model_arg(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run_pilot.main(
            [
                "--backend",
                "openai",
                "--capability",
                "T1.1",
                "--setting",
                "no_injection",
                "--count",
                "1",
                "--output-dir",
                str(tmp_path),
            ]
        )


def test_t3_1_runs_parse_tau_self_via_fixed_backend(tmp_path: Path) -> None:
    """End-to-end check: fixed-response backend whose output contains a
    retrospective duration is parsed and surfaced as self_narrated_duration.
    """
    run_pilot.main(
        [
            "--backend",
            "fixed",
            "--fixed-response",
            "Done. The whole task took 30 seconds.",
            "--capability",
            "T3.1",
            "--setting",
            "no_injection",
            "--count",
            "1",
            "--output-dir",
            str(tmp_path),
        ]
    )
    files = list(tmp_path.rglob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text())
    assert payload["self_narrated_duration"] == 30.0
    assert payload["metadata"]["tau_self_method"] == "regex"
