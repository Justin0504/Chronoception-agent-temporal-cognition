"""Tests for the Stage 1 regex parser for tau_self.

These pin the parser's behavior on the corner cases enumerated in
paper1/annotation-protocol.md §1, §2.1, and Appendix A.1.
"""

from __future__ import annotations

import math

import pytest

from chronoception.bench.parsers import (
    ClaimTense,
    extract_tau_self_prospective,
    extract_tau_self_retrospective,
    parse_duration_claims,
)


# ---------- basic numeric extraction ----------


def test_numeric_seconds() -> None:
    claims = parse_duration_claims("The task took 30 seconds.")
    assert any(math.isclose(c.seconds, 30.0) for c in claims)


def test_numeric_minutes() -> None:
    claims = parse_duration_claims("It took 5 minutes.")
    assert any(math.isclose(c.seconds, 300.0) for c in claims)


def test_numeric_hours_with_decimal() -> None:
    claims = parse_duration_claims("I spent 2.5 hours on this.")
    assert any(math.isclose(c.seconds, 9000.0) for c in claims)


def test_short_unit_letters() -> None:
    claims = parse_duration_claims("Took 90s, then 2h.")
    seconds_values = {c.seconds for c in claims}
    assert 90.0 in seconds_values
    assert 7200.0 in seconds_values


# ---------- spelled-out numbers ----------


def test_spelled_two_minutes() -> None:
    claims = parse_duration_claims("It took two minutes to finish.")
    assert any(math.isclose(c.seconds, 120.0) for c in claims)


def test_spelled_an_hour() -> None:
    # "an hour" via spelled path, even without explicit "about"
    claims = parse_duration_claims("Took an hour.")
    assert any(math.isclose(c.seconds, 3600.0) for c in claims)


# ---------- approximate quantifiers ----------


def test_a_few_minutes() -> None:
    claims = parse_duration_claims("I spent a few minutes on this.")
    assert any(math.isclose(c.seconds, 360.0) for c in claims)


def test_several_hours() -> None:
    claims = parse_duration_claims("It took several hours.")
    assert any(math.isclose(c.seconds, 13500.0) for c in claims)


def test_about_an_hour() -> None:
    claims = parse_duration_claims("It took about an hour.")
    assert any(math.isclose(c.seconds, 3600.0) for c in claims)


# ---------- ranges ----------


def test_range_uses_midpoint() -> None:
    claims = parse_duration_claims("It took 20-30 minutes.")
    assert any(math.isclose(c.seconds, 1500.0) for c in claims)


# ---------- tense classification ----------


def test_retrospective_classification() -> None:
    claims = parse_duration_claims("This took me 30 minutes.")
    assert any(c.tense is ClaimTense.RETROSPECTIVE for c in claims)


def test_prospective_classification() -> None:
    claims = parse_duration_claims("This will take 30 minutes.")
    assert any(c.tense is ClaimTense.PROSPECTIVE for c in claims)


def test_unknown_tense_when_ambiguous() -> None:
    claims = parse_duration_claims("30 minutes.")
    assert any(c.tense is ClaimTense.UNKNOWN for c in claims)


# ---------- tau_self extraction ----------


def test_retrospective_extractor_returns_value() -> None:
    text = "I completed the task. The whole task took 12 minutes."
    assert extract_tau_self_retrospective(text) == pytest.approx(720.0)


def test_retrospective_extractor_returns_none_when_only_prospective() -> None:
    text = "This will take 30 minutes to complete."
    assert extract_tau_self_retrospective(text) is None


def test_prospective_extractor_returns_value() -> None:
    text = "This will take about an hour."
    assert extract_tau_self_prospective(text) == pytest.approx(3600.0)


def test_summative_preferred_over_breakdown() -> None:
    """When a 'total duration' span is present, it dominates per-step claims."""
    text = (
        "I solved step one which took 30 seconds. Step two took 2 minutes. "
        "Overall, the whole task took 5 minutes."
    )
    assert extract_tau_self_retrospective(text) == pytest.approx(300.0)


def test_breakdown_falls_back_to_median_when_no_summative() -> None:
    """Multiple retro claims with no summative -> median of values."""
    text = (
        "Subtask A took 1 minute. Subtask B took 3 minutes. "
        "Subtask C took 5 minutes."
    )
    result = extract_tau_self_retrospective(text)
    assert result == pytest.approx(180.0)  # median of [60, 180, 300]


def test_empty_input_returns_none() -> None:
    assert extract_tau_self_retrospective("") is None
    assert extract_tau_self_prospective("") is None


def test_no_duration_returns_none() -> None:
    assert extract_tau_self_retrospective("The chicken crossed the road.") is None


def test_mixed_tense_separated_correctly() -> None:
    """Retro and prospective claims in same text are not pooled."""
    text = (
        "It took 30 minutes to solve. The next part will take about an hour."
    )
    retro = extract_tau_self_retrospective(text)
    prospective = extract_tau_self_prospective(text)
    assert retro == pytest.approx(1800.0)
    assert prospective == pytest.approx(3600.0)
