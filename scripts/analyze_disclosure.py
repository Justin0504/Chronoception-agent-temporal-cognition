#!/usr/bin/env python3
"""Analyzer for the o3 self-timing disclosure framing probe.

Reports, per framing, the no-report and explicit-refusal rates (with Wilson 95%
CIs for the proportions). A drop under the reframed conditions shows the guardrail
is framing-sensitive: o3 will disclose a system-measured elapsed value it won't
disclose as "how long you took".
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_disclosure_framing import _is_refusal  # noqa: E402  (recompute, don't trust stored flag)


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def _load(input_dir: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for model_dir in sorted(p for p in input_dir.iterdir() if p.is_dir()):
        for fr_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
            files = sorted((fr_dir / "T3.1").glob("*.json"))
            if files:
                out.setdefault(model_dir.name, {})[fr_dir.name] = [
                    json.loads(f.read_text(encoding="utf-8")) for f in files
                ]
    return out


def _summary(recs: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(recs)
    no_report = sum(1 for r in recs if r.get("no_report"))
    # Recompute refusal from final_text (the stored flag may predate apostrophe
    # normalization in _is_refusal).
    refusal = sum(1 for r in recs if _is_refusal(r.get("final_text", "")))
    return {
        "n": n,
        "frac_no_report": no_report / n if n else None,
        "no_report_ci": _wilson(no_report, n),
        "frac_refusal": refusal / n if n else None,
        "refusal_ci": _wilson(refusal, n),
    }


def analyze(input_dir: Path) -> dict[str, Any]:
    data = _load(input_dir)
    return {
        model: {fr: _summary(recs) for fr, recs in framings.items()}
        for model, framings in data.items()
    }


def _print_report(result: dict[str, Any]) -> None:
    print("=" * 70)
    print("Self-timing disclosure probe — refusal by report framing")
    print("=" * 70)
    if not result:
        print("(no data)")
        return
    for model, framings in result.items():
        print(f"Model: {model}")
        for fr, s in framings.items():
            def ci(c: Any) -> str:
                return f"[{c[0]:.2f}, {c[1]:.2f}]" if c else ""
            print(f"  {fr:<14} n={s['n']:>3}  no_report={s['frac_no_report']:.2f} "
                  f"{ci(s['no_report_ci'])}  refusal={s['frac_refusal']:.2f} {ci(s['refusal_ci'])}")
        print()
    print("=" * 70)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Analyze the disclosure framing probe.")
    p.add_argument("--input-dir", default="disclosure-results")
    p.add_argument("--output-json", default=None)
    args = p.parse_args(argv)
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"input dir not found: {input_dir}")
    result = analyze(input_dir)
    _print_report(result)
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(f"Wrote JSON: {args.output_json}")


if __name__ == "__main__":
    main()
