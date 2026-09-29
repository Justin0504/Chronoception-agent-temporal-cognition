#!/usr/bin/env python3
"""What does tau_self actually track: the clock, or the model's own output?

Answers the sharpest objection to the whole measurement. Wall-clock duration is
a property of the serving stack -- batching, queue depth, hardware -- not of
the policy. Asking a model how long it took can look like asking a function how
much CPU its scheduler gave it. If tau_self is a faithful readout of something
the model CAN observe, the objection has force and the paper should say so.

The test: within each agent, rank-correlate tau_self against (a) tau_wall, the
quantity the paper scores it on, and (b) the length of the model's own visible
output, which the model does have access to.

The answer is not a clean win for either side, which is why it is worth
reporting. For non-reasoning agents generation time is roughly proportional to
tokens produced, so the two predictors are collinear and both correlate. Where
they come apart -- reasoning mode, where hidden chain-of-thought inflates
tau_wall without inflating the visible answer -- tau_self follows the output
and abandons the clock: o4-mini correlates +0.058 with wall-clock against
+0.362 with output length.

That is the mechanism the Reverse-Scaling section asserts, measured directly.
It also concedes the objection's premise and then denies its conclusion: the
self-report is a readout of token production, not of duration -- and a budget
set in wall-clock seconds is not honoured by an agent faithfully reporting how
much it wrote.

    python3 scripts/analyze_what_tau_self_tracks.py
"""
from __future__ import annotations

import csv
import glob
import json
import statistics as st
from pathlib import Path

OUT = Path("pilot-results/tau_self_tracks.csv")

PANEL: dict[str, list[str]] = {
    "gpt-4o-mini": ["pilot-results/openai_gpt-4o-mini/T3.1/*/*.json"],
    "gpt-4o": ["pilot-results/openai_gpt-4o/T3.1/*/*.json"],
    "gpt-5.1": ["pilot-results/openai_gpt-5.1/T3.1/*/*.json",
                "e1-results/gpt-5.1/**/T3.1/*/*.json"],
    "o3": ["pilot-results/openai_o3/T3.1/*/*.json",
           "e1-results/o3/**/T3.1/*/*.json"],
    "o4-mini": ["pilot-results/openai_o4-mini/T3.1/*/*.json",
                "e1-results/o4-mini/**/T3.1/*/*.json"],
    "Claude Haiku 4.5": ["pilot-results/anthropic_claude-haiku-4-5/T3.1/*/*.json"],
    "Claude Sonnet 4.6": ["pilot-results/anthropic_claude-sonnet-4-6/T3.1/*/*.json"],
    "Sonnet 4.6 + thinking": ["e3-results/claude-sonnet-4-6-thinking/**/T3.1/*/*.json"],
    "Qwen2.5-7B": ["pilot-results/oss_qwen2.5-7b-instruct-yuezhao/T3.1/*/*.json"],
    "GLM-5.2-FP8": ["vultr-results/glm-5.2-fp8/**/T3.1/*/*.json"],
    "Kimi-K2.6": ["vultr-results/kimi-k2.6/**/T3.1/*/*.json"],
    "MiniMax-M2.7": ["vultr-results/minimax-m2.7/**/T3.1/*/*.json"],
    "Qwen3.6-27B": ["vultr-results/qwen3.6-27b/**/T3.1/*/*.json"],
}

# Which configurations run a hidden chain-of-thought, i.e. where wall-clock and
# visible output length are expected to come apart.
REASONING = {"gpt-5.1", "o3", "o4-mini", "Sonnet 4.6 + thinking",
             "Kimi-K2.6", "MiniMax-M2.7"}


def spearman(a, b):
    ra = {v: i for i, v in enumerate(sorted(a))}
    rb = {v: i for i, v in enumerate(sorted(b))}
    x = [ra[v] for v in a]
    y = [rb[v] for v in b]
    mx, my = st.mean(x), st.mean(y)
    den = (sum((i - mx) ** 2 for i in x) * sum((j - my) ** 2 for j in y)) ** 0.5
    return sum((i - mx) * (j - my) for i, j in zip(x, y)) / den if den else float("nan")


def collect(pats):
    ts, tw, ln = [], [], []
    for p in pats:
        for fp in glob.glob(p, recursive=True):
            try:
                d = json.load(open(fp))
            except (OSError, json.JSONDecodeError):
                continue
            s = d.get("self_narrated_duration")
            steps = d.get("steps") or []
            if not s or s <= 0 or not steps:
                continue
            w = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
            if w <= 0:
                continue
            ts.append(s)
            tw.append(w)
            ln.append(len(str(steps[-1].get("action", ""))))
    return ts, tw, ln


def main() -> int:
    rows = []
    for name, pats in PANEL.items():
        ts, tw, ln = collect(pats)
        if len(ts) < 10:
            continue
        rows.append({
            "agent": name,
            "reasoning": "yes" if name in REASONING else "no",
            "n": len(ts),
            "vs_tau_wall": round(spearman(ts, tw), 4),
            "vs_output_len": round(spearman(ts, ln), 4),
        })

    w = max(len(r["agent"]) for r in rows)
    print("What tau_self tracks, within agent (T3.1, both settings pooled)\n")
    print(f"{'agent':<{w}}  {'mode':>10}  {'n':>4}  {'vs tau_wall':>12}  {'vs output len':>14}")
    for r in sorted(rows, key=lambda r: (r["reasoning"], r["agent"])):
        print(f"{r['agent']:<{w}}  {('reasoning' if r['reasoning']=='yes' else 'plain'):>10}  "
              f"{r['n']:4d}  {r['vs_tau_wall']:+12.3f}  {r['vs_output_len']:+14.3f}")

    for label, sel in [("all", lambda r: True),
                       ("non-reasoning", lambda r: r["reasoning"] == "no"),
                       ("reasoning", lambda r: r["reasoning"] == "yes")]:
        g = [r for r in rows if sel(r)]
        if not g:
            continue
        mw = st.median(r["vs_tau_wall"] for r in g)
        ml = st.median(r["vs_output_len"] for r in g)
        print(f"\n  {label:<14} median  vs tau_wall {mw:+.3f}   vs output {ml:+.3f}"
              f"   gap {ml-mw:+.3f}")

    print("\nReading: where generation time and output length are collinear (plain")
    print("models) both predictors look alike. Where a hidden chain-of-thought pulls")
    print("them apart, the self-report follows the output and drops the clock.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
