"""Sanity tests on the capability registry.

The benchmark's taxonomic claim (FRAMING.md §5) is that there are exactly nine
sub-capabilities organized as three per axis, with one named law per axis.
These tests pin that structure so it cannot drift silently.
"""

from __future__ import annotations

from collections import Counter

from chronoception.bench.tasks import CAPABILITIES, TemporalAxis, capability_by_id


def test_nine_capabilities_total() -> None:
    assert len(CAPABILITIES) == 9


def test_three_capabilities_per_axis() -> None:
    by_axis = Counter(c.axis for c in CAPABILITIES)
    assert by_axis[TemporalAxis.WALL] == 3
    assert by_axis[TemporalAxis.STEP] == 3
    assert by_axis[TemporalAxis.SELF] == 3


def test_codes_are_unique_and_well_formed() -> None:
    codes = [c.code for c in CAPABILITIES]
    assert len(codes) == len(set(codes))
    for code in codes:
        assert code.startswith("T") and "." in code, code


def test_lookup_round_trips() -> None:
    for cap in CAPABILITIES:
        assert capability_by_id(cap.code) is cap


def test_T2_3_is_the_l2_core_test() -> None:
    """T2.3 (Wall-budget execution) is FRAMING §5's named L2 core test."""
    cap = capability_by_id("T2.3")
    assert cap.axis is TemporalAxis.STEP
    assert "Step-Clock Conflation" in cap.description or "L2" in cap.description
