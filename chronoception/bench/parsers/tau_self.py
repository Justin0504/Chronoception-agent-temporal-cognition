"""Stage 1 regex parser for self-narrated durations (tau_self).

Implements the deterministic regex pre-filter of the two-stage parser in
paper1/annotation-protocol.md §2.1. Output of this stage is then passed
to the LLM-as-judge ensemble (Stage 2, separately implemented).

What this module produces is a *candidate set* of DurationClaim records;
each candidate is annotated with a tense-heuristic prospective vs
retrospective classification, a normalized duration in seconds, and the
raw text span that triggered it.

Calling code that needs a single tau_self value per trajectory invokes
``extract_tau_self_retrospective`` which collapses candidates per the
priority rules of the annotation protocol §1.2.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "DurationClaim",
    "ClaimTense",
    "parse_duration_claims",
    "extract_tau_self_retrospective",
    "extract_tau_self_prospective",
]


class ClaimTense(str, Enum):
    """Whether the duration claim looks backward or forward."""

    RETROSPECTIVE = "retrospective"
    PROSPECTIVE = "prospective"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DurationClaim:
    """A single duration-bearing span extracted from agent output."""

    raw_text: str
    seconds: float
    tense: ClaimTense
    span_start: int = -1  # offset in the source text; -1 if unknown
    span_end: int = -1
    source_text: str = ""  # full source text the span was extracted from
    method: str = "regex"
    confidence: float = 0.5  # Stage 1 default; ensemble (Stage 2) may revise


# ---------- numeric extraction ----------

_UNIT_FACTORS_SECONDS: dict[str, float] = {
    "second": 1.0,
    "seconds": 1.0,
    "sec": 1.0,
    "secs": 1.0,
    "s": 1.0,
    "minute": 60.0,
    "minutes": 60.0,
    "min": 60.0,
    "mins": 60.0,
    "m": 60.0,
    "hour": 3600.0,
    "hours": 3600.0,
    "hr": 3600.0,
    "hrs": 3600.0,
    "h": 3600.0,
}

_NUMBER_WORDS: dict[str, float] = {
    "a": 1.0,
    "an": 1.0,
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
    "twelve": 12.0,
    "fifteen": 15.0,
    "twenty": 20.0,
    "thirty": 30.0,
    "forty": 40.0,
    "fifty": 50.0,
    "sixty": 60.0,
    "ninety": 90.0,
}

# Approximate-quantifier resolution (paper1/annotation-protocol.md Appendix A.1).
# Map (quantifier, unit_singular) -> midpoint in seconds.
_QUANTIFIER_MIDPOINTS_SECONDS: dict[tuple[str, str], float] = {
    ("a few", "second"): 6.0,
    ("a few", "minute"): 360.0,
    ("a few", "hour"): 7200.0,
    ("several", "second"): 10.0,
    ("several", "minute"): 1050.0,
    ("several", "hour"): 13500.0,
    ("a couple of", "second"): 4.0,
    ("a couple of", "minute"): 180.0,
    ("a couple of", "hour"): 7200.0,
    ("about an", "hour"): 3600.0,
    ("around an", "hour"): 3600.0,
    ("roughly an", "hour"): 3600.0,
    ("about a", "minute"): 60.0,
}


_NUMBER_RE = r"(?:\d+(?:\.\d+)?)"
_UNIT_RE = (
    r"(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|s|m|h)"
)
_RANGE_SEP_RE = r"\s*(?:-|to|–|—)\s*"

# Pattern 1: numeric duration with explicit unit, possibly a range.
_NUMERIC_RE = re.compile(
    rf"(?P<lo>{_NUMBER_RE})(?:{_RANGE_SEP_RE}(?P<hi>{_NUMBER_RE}))?\s*(?P<unit>{_UNIT_RE})\b",
    flags=re.IGNORECASE,
)

# Pattern 2: spelled-out number with unit.
_SPELLED_RE = re.compile(
    rf"\b(?P<word>{'|'.join(map(re.escape, _NUMBER_WORDS))})\s+(?P<unit>{_UNIT_RE})\b",
    flags=re.IGNORECASE,
)

# Pattern 3: approximate quantifier with unit.
_QUANTIFIER_KEYS = sorted(
    {q for q, _ in _QUANTIFIER_MIDPOINTS_SECONDS},
    key=len,
    reverse=True,
)
_QUANTIFIER_RE = re.compile(
    rf"(?P<quant>{'|'.join(map(re.escape, _QUANTIFIER_KEYS))})\s+"
    rf"(?P<unit>{_UNIT_RE})\b",
    flags=re.IGNORECASE,
)

# Tense heuristics (paper1/annotation-protocol.md §1.1).
_RETRO_MARKERS = (
    "took",
    "spent",
    "spent about",
    "needed",
    "required",
    "lasted",
    "elapsed",
    "i was",
    "i worked",
    "i did this in",
    "this took",
    "it took",
    "that took",
    "we took",
    "i used",
    "in the past",
    "ago",
    "completed in",
    "finished in",
    "wrote it in",
    "wrote this in",
)
_PROSPECTIVE_MARKERS = (
    "will take",
    "will need",
    "is going to take",
    "should take",
    "would take",
    "plan to",
    "expect",
    "expected",
    "estimate",
    "estimated",
    "i will",
    "i'll",
    "going to",
    "in the next",
    "give me another",
    "give me",
    "in the future",
    "i need another",
)


def _normalize_unit(unit: str) -> str:
    """Map any unit string (case-insensitive) to its canonical singular form."""
    unit = unit.lower()
    if unit in _UNIT_FACTORS_SECONDS:
        # already canonical-ish; map to singular base
        if unit in ("seconds", "secs"):
            return "second"
        if unit in ("minutes", "mins"):
            return "minute"
        if unit in ("hours", "hrs"):
            return "hour"
        if unit == "s":
            return "second"
        if unit == "m":
            return "minute"
        if unit == "h":
            return "hour"
        return unit
    return unit


def _classify_tense(text: str, span_start: int, span_end: int) -> ClaimTense:
    """Heuristic retro/prospective classifier based on a context window."""
    context_radius = 60
    context_start = max(0, span_start - context_radius)
    context = text[context_start:span_end].lower()
    if any(marker in context for marker in _PROSPECTIVE_MARKERS):
        return ClaimTense.PROSPECTIVE
    if any(marker in context for marker in _RETRO_MARKERS):
        return ClaimTense.RETROSPECTIVE
    return ClaimTense.UNKNOWN


def _seconds_from_numeric(lo: str, hi: str | None, unit: str) -> float:
    """Convert a numeric (optionally ranged) duration into seconds."""
    canonical = _normalize_unit(unit)
    factor = _UNIT_FACTORS_SECONDS[canonical]
    if hi is None:
        return float(lo) * factor
    midpoint = (float(lo) + float(hi)) / 2.0
    return midpoint * factor


def _seconds_from_spelled(word: str, unit: str) -> float:
    canonical = _normalize_unit(unit)
    factor = _UNIT_FACTORS_SECONDS[canonical]
    return _NUMBER_WORDS[word.lower()] * factor


def _seconds_from_quantifier(quant: str, unit: str) -> float | None:
    """Resolve approximate quantifier to midpoint seconds, or None if unmapped."""
    canonical = _normalize_unit(unit)
    key = (quant.lower(), canonical)
    return _QUANTIFIER_MIDPOINTS_SECONDS.get(key)


def parse_duration_claims(text: str) -> list[DurationClaim]:
    """Stage 1 parser. Return all candidate duration claims with tense tag."""
    claims: list[DurationClaim] = []

    # Pass 1: approximate quantifiers (longer; resolved first to avoid being
    # cannibalized by the numeric pass for phrases like "about an hour").
    for m in _QUANTIFIER_RE.finditer(text):
        secs = _seconds_from_quantifier(m.group("quant"), m.group("unit"))
        if secs is None:
            continue
        claims.append(
            DurationClaim(
                raw_text=m.group(0),
                seconds=secs,
                tense=_classify_tense(text, m.start(), m.end()),
                span_start=m.start(),
                span_end=m.end(),
                source_text=text,
            )
        )

    # Pass 2: numeric durations with explicit unit (handles ranges).
    for m in _NUMERIC_RE.finditer(text):
        secs = _seconds_from_numeric(m.group("lo"), m.group("hi"), m.group("unit"))
        claims.append(
            DurationClaim(
                raw_text=m.group(0),
                seconds=secs,
                tense=_classify_tense(text, m.start(), m.end()),
                span_start=m.start(),
                span_end=m.end(),
                source_text=text,
            )
        )

    # Pass 3: spelled-out numbers.
    for m in _SPELLED_RE.finditer(text):
        secs = _seconds_from_spelled(m.group("word"), m.group("unit"))
        claims.append(
            DurationClaim(
                raw_text=m.group(0),
                seconds=secs,
                tense=_classify_tense(text, m.start(), m.end()),
                span_start=m.start(),
                span_end=m.end(),
                source_text=text,
            )
        )

    return claims


def _pick_summative(claims: list[DurationClaim]) -> DurationClaim | None:
    """If any claim is preceded by a 'total / overall' marker, prefer it.

    The marker is searched in the source-text window preceding the matched
    duration span (not in the matched span itself, which contains only the
    numeric phrase).
    """
    summative_markers = (
        "total duration",
        "overall",
        "altogether",
        "in total",
        "the whole task",
        "the whole thing",
        "the entire task",
        "all together",
    )
    context_radius = 50
    for claim in claims:
        if claim.span_start < 0:
            # No span info; fall back to raw_text scanning.
            haystack = claim.raw_text.lower()
        else:
            start = max(0, claim.span_start - context_radius)
            haystack = claim.source_text[start:claim.span_end].lower()
        if any(marker in haystack for marker in summative_markers):
            return claim
    return None


def extract_tau_self_retrospective(text: str) -> float | None:
    """Return a single retrospective tau_self in seconds, or None.

    Implements the priority rules of paper1/annotation-protocol.md §1.2:
    explicitly summative > sum of per-sub-task breakdowns > median of
    candidate retros > None.
    """
    candidates = [
        c for c in parse_duration_claims(text)
        if c.tense is ClaimTense.RETROSPECTIVE
    ]
    if not candidates:
        return None

    summative = _pick_summative(candidates)
    if summative is not None:
        return summative.seconds

    if len(candidates) == 1:
        return candidates[0].seconds

    durations_sorted = sorted(c.seconds for c in candidates)
    mid = len(durations_sorted) // 2
    if len(durations_sorted) % 2 == 1:
        return durations_sorted[mid]
    return (durations_sorted[mid - 1] + durations_sorted[mid]) / 2.0


def extract_tau_self_prospective(text: str) -> float | None:
    """Return a single prospective tau_self in seconds, or None.

    Same priority rules as retrospective extraction (§1.2).
    """
    candidates = [
        c for c in parse_duration_claims(text)
        if c.tense is ClaimTense.PROSPECTIVE
    ]
    if not candidates:
        return None
    summative = _pick_summative(candidates)
    if summative is not None:
        return summative.seconds
    if len(candidates) == 1:
        return candidates[0].seconds
    durations_sorted = sorted(c.seconds for c in candidates)
    mid = len(durations_sorted) // 2
    if len(durations_sorted) % 2 == 1:
        return durations_sorted[mid]
    return (durations_sorted[mid - 1] + durations_sorted[mid]) / 2.0
