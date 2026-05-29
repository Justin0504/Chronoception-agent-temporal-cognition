"""Tests for the eval runner.

Covers the Setting A vs Setting B branching of FRAMING §3.1 and the
trajectory structure produced for downstream metric computation.
"""

from __future__ import annotations

import pytest

from chronoception.bench import (
    EchoBackend,
    EvalSetting,
    FixedResponseBackend,
    Runner,
    Trajectory,
    generate_t1_1_instances,
    generate_t2_3_instances,
    generate_t3_1_instances,
    run_instance,
)


def test_runner_produces_trajectory() -> None:
    instance = generate_t1_1_instances(count=1)[0]
    runner = Runner(agent=EchoBackend(), setting=EvalSetting.NO_INJECTION)
    traj = runner(instance)
    assert isinstance(traj, Trajectory)
    assert traj.agent_id == "echo"
    assert len(traj.steps) == 2
    assert traj.capability_code == "T1.1"
    assert traj.metadata["setting"] == "no_injection"


def test_setting_a_does_not_inject() -> None:
    instance = generate_t1_1_instances(count=1)[0]
    traj = run_instance(
        instance=instance,
        agent=EchoBackend(),
        setting=EvalSetting.NO_INJECTION,
    )
    system = traj.metadata["system_prompt"]
    assert "Current date and time" not in system


def test_setting_b_injects_wall_clock_timestamp() -> None:
    instance = generate_t1_1_instances(count=1)[0]
    traj = run_instance(
        instance=instance,
        agent=EchoBackend(),
        setting=EvalSetting.WITH_INJECTION,
    )
    system = traj.metadata["system_prompt"]
    assert "Current date and time" in system
    assert traj.metadata["setting"] == "with_injection"


def test_runner_preserves_wall_budget_for_t2_3() -> None:
    instance = generate_t2_3_instances(count=1)[0]
    traj = run_instance(
        instance=instance,
        agent=EchoBackend(),
        setting=EvalSetting.NO_INJECTION,
    )
    assert traj.budget == instance.budget
    assert traj.budget_kind == "wall"


def test_runner_records_capability_code_for_metric_routing() -> None:
    """epsilon's axis-routing relies on capability_code being set."""
    for generator, expected_code in (
        (generate_t1_1_instances, "T1.1"),
        (generate_t2_3_instances, "T2.3"),
        (generate_t3_1_instances, "T3.1"),
    ):
        traj = run_instance(
            instance=generator(count=1)[0],
            agent=EchoBackend(),
            setting=EvalSetting.NO_INJECTION,
        )
        assert traj.capability_code == expected_code


def test_fixed_response_backend_with_delay_measures_wall_clock() -> None:
    """Wall-clock between steps must reflect the backend's actual delay."""
    backend = FixedResponseBackend(response="ok", delay_seconds=0.05)
    instance = generate_t3_1_instances(count=1)[0]
    traj = run_instance(
        instance=instance,
        agent=backend,
        setting=EvalSetting.NO_INJECTION,
    )
    assert traj.tau_wall >= 0.05


def test_self_narrated_duration_starts_unset() -> None:
    """The runner does not parse tau_self; that is the parser's job."""
    instance = generate_t3_1_instances(count=1)[0]
    traj = run_instance(
        instance=instance,
        agent=EchoBackend(),
        setting=EvalSetting.NO_INJECTION,
    )
    assert traj.tau_self is None
