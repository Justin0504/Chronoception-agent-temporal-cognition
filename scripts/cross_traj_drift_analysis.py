#!/usr/bin/env python3
"""Cross-trajectory drift analysis: does |rho| grow with tau_wall across trajectories?

This is the closest analog to P8 we can compute from single-step ChronoBench
data. Bucket trajectories by tau_wall, compute median |rho| per bucket.
"""
from __future__ import annotations
import json
from collections import defaultdict
from math import log10
from pathlib import Path
from statistics import median


def load_t31(dirs):
    """Return list of (agent, tau_wall, rho) tuples for all T3.1 traj."""
    rows = []
    for d in dirs:
        for p in Path(d).rglob("*/T3.1/no_injection/*.json"):
            try:
                data = json.loads(p.read_text())
            except Exception:
                continue
            steps = data.get("steps") or []
            if not steps:
                continue
            tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
            ts = data.get("self_narrated_duration")
            if ts and ts > 0 and tw > 0:
                rows.append({
                    "agent": data["agent_id"],
                    "tau_wall": tw,
                    "rho": log10(ts/tw),
                })
    return rows


def bucket(tw):
    if tw < 2: return "<2s"
    if tw < 5: return "2-5s"
    if tw < 15: return "5-15s"
    if tw < 60: return "15-60s"
    return ">60s"


rows = load_t31(["pilot-results", "e2-results", "e3-results", "e5-results"])
print(f"Loaded {len(rows)} T3.1 trajectories with parseable rho")

# Per-bucket median |rho| across panel
by_bucket = defaultdict(list)
for r in rows:
    by_bucket[bucket(r["tau_wall"])].append(abs(r["rho"]))

print("\n=== Cross-trajectory drift: |rho| vs tau_wall (all agents pooled) ===")
order = ["<2s", "2-5s", "5-15s", "15-60s", ">60s"]
for b in order:
    vs = by_bucket.get(b, [])
    if vs:
        print(f"  {b:>8}: n={len(vs):4d}  median|rho|={median(vs):.3f}")

# Per-agent class
print("\n=== Per-agent-class ===")
reasoning_keywords = ["o3", "o4-mini", "deepseek-r1", "sonnet-4-6-thinking"]
def cls(agent):
    a = agent.lower()
    if any(k in a for k in reasoning_keywords):
        return "reasoning"
    return "non-reasoning"

by_class_bucket = defaultdict(lambda: defaultdict(list))
for r in rows:
    by_class_bucket[cls(r["agent"])][bucket(r["tau_wall"])].append(abs(r["rho"]))

for c in ["non-reasoning", "reasoning"]:
    print(f"\n  {c}:")
    for b in order:
        vs = by_class_bucket[c].get(b, [])
        if vs:
            print(f"    {b:>8}: n={len(vs):4d}  median|rho|={median(vs):.3f}")

# Spearman-ish: slope of median |rho| vs log10(bucket_mid)
print("\n=== Slope: median |rho| vs log10(tau_wall) per class ===")
import math
bucket_mid = {"<2s": 1.0, "2-5s": 3.0, "5-15s": 9.0, "15-60s": 30.0, ">60s": 180.0}
for c in ["non-reasoning", "reasoning"]:
    pts = []
    for b, mid in bucket_mid.items():
        vs = by_class_bucket[c].get(b, [])
        if len(vs) >= 5:
            pts.append((math.log10(mid), median(vs)))
    if len(pts) >= 2:
        xs, ys = zip(*pts)
        n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
        num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
        den = sum((x-mx)**2 for x in xs)
        slope = num/den if den > 0 else 0
        print(f"  {c}: slope = {slope:+.3f}  (positive = |rho| grows with tau_wall)")
