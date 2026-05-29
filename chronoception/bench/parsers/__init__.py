"""Parsers for self-narrated duration extraction (tau_self).

Implements the two-stage parser of paper1/annotation-protocol.md.
"""

from chronoception.bench.parsers.tau_self import (
    ClaimTense,
    DurationClaim,
    extract_tau_self_prospective,
    extract_tau_self_retrospective,
    parse_duration_claims,
)

__all__ = [
    "ClaimTense",
    "DurationClaim",
    "parse_duration_claims",
    "extract_tau_self_retrospective",
    "extract_tau_self_prospective",
]
