#!/usr/bin/env python3
"""Build the T3.1 main panel table with n_rho + bootstrap 95% CI per cell.

Output: LaTeX table snippet for §B + console summary.
"""
from __future__ import annotations
import json
import random
from math import log10
from pathlib import Path
from statistics import median


def bootstrap_median_abs(values, n_iter=10000, seed=0):
    if not values:
        return None, None, None
    rng = random.Random(seed)
    n = len(values)
    samples = []
    for _ in range(n_iter):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(median(abs(v) for v in sample))
    samples.sort()
    point = median(abs(v) for v in values)
    return point, samples[int(0.025 * n_iter)], samples[int(0.975 * n_iter)]


def bootstrap_median_signed(values, n_iter=10000, seed=0):
    if not values:
        return None, None, None
    rng = random.Random(seed)
    n = len(values)
    samples = []
    for _ in range(n_iter):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(median(sample))
    samples.sort()
    return median(values), samples[int(0.025 * n_iter)], samples[int(0.975 * n_iter)]


def load_rhos(dirs, agent_id_filter):
    rhos = {"no_injection": [], "with_injection": []}
    for d in dirs:
        for p in Path(d).rglob("*/T3.1/*/*.json"):
            try:
                t = json.loads(p.read_text())
            except Exception:
                continue
            if t.get("agent_id") != agent_id_filter:
                continue
            setting = t.get("metadata", {}).get("setting")
            if setting not in rhos:
                continue
            steps = t.get("steps") or []
            if not steps: continue
            tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
            ts = t.get("self_narrated_duration")
            if ts and ts > 0 and tw > 0:
                rhos[setting].append(log10(ts / tw))
    return rhos


PANEL = [
    ("openai/gpt-4o-mini", "gpt-4o-mini"),
    ("openai/gpt-4o", "gpt-4o"),
    ("openai/gpt-5.1", "gpt-5.1"),
    ("openai/o3", "o3 (reasoning)"),
    ("openai/o4-mini", "o4-mini (reasoning)"),
    ("anthropic/claude-haiku-4-5", "Claude Haiku 4.5"),
    ("anthropic/claude-sonnet-4-6", "Claude Sonnet 4.6"),
    ("oss/qwen2.5-7b-instruct-yuezhao", "Qwen2.5-7B"),
]

# Sonnet 4.6 + thinking (separate)
THINKING = ("anthropic/claude-sonnet-4-6", "Claude Sonnet 4.6 + thinking",
            ["e3-results"])

DIRS = ["pilot-results", "e1-results", "e2-results", "e3-results", "e5-results", "e5b-results"]


def fmt(v, n_dec=3):
    return f"{v:.{n_dec}f}" if v is not None else "—"


def cell(point, lo, hi, n, threshold=10):
    if n == 0:
        return "—"
    flag = r" \dagger" if n < threshold else ""
    return f"${fmt(point)}_{{[{fmt(lo)},\\,{fmt(hi)}]}}^{{n={n}{flag}}}$"


print("=" * 95)
print("T3.1 main panel: median rho (signed) with bootstrap 95% CI + n_rho")
print("=" * 95)
print(f"{'Model':<28s} {'setting':<14s} {'n':>4s}  {'median rho':>22s}  {'median |rho|':>22s}")
print("-" * 95)

latex_lines = []

for agent, label in PANEL:
    if agent == "anthropic/claude-sonnet-4-6":
        # Exclude e3-results (thinking variant) and e1-results to keep this row pure
        # non-thinking baseline; thinking gets its own row below
        rhos = load_rhos(["pilot-results"], agent)
    elif agent == "openai/o4-mini":
        rhos = load_rhos(["pilot-results", "e1-results", "e2-results", "e3-results"], agent)
    elif agent == "openai/o3":
        rhos = load_rhos(["pilot-results", "e1-results"], agent)
    else:
        rhos = load_rhos(DIRS, agent)

    for setting in ("no_injection", "with_injection"):
        rs = rhos[setting]
        n = len(rs)
        if n == 0:
            print(f"{label:<28s} {setting:<14s} {n:>4d}  {'—':>22s}  {'—':>22s}")
            continue
        med, lo_s, hi_s = bootstrap_median_signed(rs)
        med_abs, lo_a, hi_a = bootstrap_median_abs(rs)
        flag = " ⚠" if n < 10 else "  "
        print(f"{label:<28s} {setting:<14s} {n:>3d}{flag}  "
              f"{fmt(med):>10s} [{fmt(lo_s)},{fmt(hi_s)}]  "
              f"{fmt(med_abs):>10s} [{fmt(lo_a)},{fmt(hi_a)}]")

print()
print("⚠ = underpowered (n < 10), bootstrap CI interpretation requires caution")
print()
print("Also adding the Sonnet 4.6 + thinking variant from e3-results:")
agent, label, sub_dirs = THINKING
rhos = load_rhos(sub_dirs, agent)
for setting in ("no_injection", "with_injection"):
    rs = rhos[setting]
    n = len(rs)
    if n == 0: continue
    med, lo_s, hi_s = bootstrap_median_signed(rs)
    med_abs, lo_a, hi_a = bootstrap_median_abs(rs)
    flag = " ⚠" if n < 10 else "  "
    print(f"  {label:<28s} {setting:<14s} {n:>3d}{flag}  "
          f"median rho = {fmt(med):>8s} [{fmt(lo_s)},{fmt(hi_s)}]  "
          f"median |rho| = {fmt(med_abs):>8s} [{fmt(lo_a)},{fmt(hi_a)}]")
