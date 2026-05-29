"""Tests for the pilot task-instance generators.

The pre-registered predictions of FRAMING §9 depend on reproducible instance
generation. These tests pin the structural properties so they cannot drift.
"""

from __future__ import annotations

from collections import Counter

import pytest

from chronoception.bench import (
    generate_pilot_instances,
    generate_t1_1_instances,
    generate_t2_3_instances,
    generate_t3_1_instances,
)
from chronoception.bench.tasks import TemporalAxis, axis_for


def test_pilot_default_size() -> None:
    instances = generate_pilot_instances()
    assert len(instances) == 150


def test_each_capability_produces_50_default() -> None:
    assert len(generate_t1_1_instances()) == 50
    assert len(generate_t2_3_instances()) == 50
    assert len(generate_t3_1_instances()) == 50


def test_generators_are_deterministic() -> None:
    """Same seed must yield identical instance IDs and prompts."""
    a = generate_pilot_instances(seed=42)
    b = generate_pilot_instances(seed=42)
    assert [i.instance_id for i in a] == [i.instance_id for i in b]
    assert [i.prompt for i in a] == [i.prompt for i in b]


def test_generators_vary_with_seed() -> None:
    """Different seeds should yield different prompt distributions."""
    a = generate_pilot_instances(seed=0)
    b = generate_pilot_instances(seed=1)
    assert [i.prompt for i in a] != [i.prompt for i in b]


def test_t1_1_axis() -> None:
    for instance in generate_t1_1_instances():
        assert axis_for(instance.task.capability_code) is TemporalAxis.WALL
        assert instance.budget is None
        assert instance.task.budget_kind == "none"


def test_t2_3_axis_and_budgets() -> None:
    for instance in generate_t2_3_instances():
        assert axis_for(instance.task.capability_code) is TemporalAxis.STEP
        assert instance.budget is not None
        assert instance.budget > 0
        assert instance.task.budget_kind == "wall"


def test_t3_1_axis() -> None:
    for instance in generate_t3_1_instances():
        assert axis_for(instance.task.capability_code) is TemporalAxis.SELF
        assert instance.budget is None
        assert instance.task.budget_kind == "none"


def test_t2_3_budgets_cover_design_range() -> None:
    """T2.3 budgets must span at least 60s to 3600s for L2 regime analysis."""
    budgets = {i.budget for i in generate_t2_3_instances(count=200)}
    assert min(budgets) <= 60.0
    assert max(budgets) >= 3600.0


def test_instance_ids_unique_within_capability() -> None:
    for generator in (generate_t1_1_instances, generate_t2_3_instances, generate_t3_1_instances):
        instances = generator()
        codes = [i.instance_id for i in instances]
        assert len(codes) == len(set(codes))


def test_t2_3_prompts_mention_budget_seconds() -> None:
    """The wall-budget execution prompt must surface the budget."""
    for instance in generate_t2_3_instances(count=20):
        assert f"{int(instance.budget)} seconds" in instance.prompt


def test_pilot_bundle_capability_distribution() -> None:
    instances = generate_pilot_instances()
    by_code = Counter(i.task.capability_code for i in instances)
    assert by_code["T1.1"] == 50
    assert by_code["T2.3"] == 50
    assert by_code["T3.1"] == 50
