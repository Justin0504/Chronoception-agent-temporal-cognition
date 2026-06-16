"""Tests for the self-timing disclosure framing probe."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _ROOT / "scripts"
for p in (str(_ROOT), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import analyze_disclosure as ana  # noqa: E402
import run_disclosure_framing as run  # noqa: E402


def test_framings_present() -> None:
    assert set(run._FRAMINGS) == {"direct", "system_field", "third_person"}
    for tmpl in run._FRAMINGS.values():
        assert "{task}" in tmpl


def test_is_refusal() -> None:
    assert run._is_refusal("I'm sorry, but I can't share precise timing information.")
    assert run._is_refusal("I cannot provide the exact duration.")
    assert not run._is_refusal("The task took me 6 seconds.")


def test_wilson_interval() -> None:
    assert ana._wilson(0, 0) is None
    lo, hi = ana._wilson(5, 10)
    assert 0.0 <= lo < 0.5 < hi <= 1.0
    # All-refusal: CI hugs 1.0 but stays below it.
    lo2, hi2 = ana._wilson(15, 15)
    assert lo2 > 0.7 and hi2 <= 1.0


def test_summary_and_analyze(tmp_path: Path) -> None:
    d = tmp_path / "o3" / "direct" / "T3.1"
    d.mkdir(parents=True)
    recs = [{"no_report": True, "is_refusal": True}] * 8 + [{"no_report": False, "is_refusal": False}] * 2
    for i, r in enumerate(recs):
        (d / f"T3.1.{i:03d}.json").write_text(json.dumps(r), encoding="utf-8")
    res = ana.analyze(tmp_path)
    s = res["o3"]["direct"]
    assert s["n"] == 10
    assert s["frac_no_report"] == 0.8
    assert s["frac_refusal"] == 0.8
