#!/usr/bin/env python3
"""Compute per-cell stats for the Sonnet 4.6 + extended thinking variant only.

Reads e3-results/claude-sonnet-4-6-thinking/ exclusively, so the numbers
are not contaminated by the non-thinking baseline (which shares agent_id).

Output: a LaTeX table snippet + console summary.
"""
from __future__ import annotations
import json, random
from math import log10, sqrt
from pathlib import Path
from statistics import median

DIR = Path("e3-results/claude-sonnet-4-6-thinking")


def bootstrap_signed(values, n_iter=10000, seed=0):
    if not values: return None, None, None
    rng = random.Random(seed); n = len(values); samples = []
    for _ in range(n_iter):
        s = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(median(s))
    samples.sort()
    return median(values), samples[int(0.025*n_iter)], samples[int(0.975*n_iter)]


def wilson(succ, n):
    if n == 0: return None, None
    z = 1.96; p = succ/n
    den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = (z * sqrt(p*(1-p)/n + z*z/(4*n*n))) / den
    return max(0, c-h), min(1, c+h)


def extract_rho(t):
    steps = t.get("steps") or []
    if not steps: return None
    tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
    ts = t.get("self_narrated_duration")
    if ts is None or ts <= 0 or tw <= 0: return None
    return log10(ts / tw)


def t11_pass(action, run_date):
    if not action: return None
    a = action.lower()
    if any(k in a for k in ["i do not know","training data","training cutoff",
                            "cannot determine","no access to","i don't have access"]):
        return False
    if run_date[:10] in action or run_date[:10].replace("-","/") in action: return True
    if run_date[:4] in action: return True
    return None


def car(t):
    steps = t.get("steps") or []
    if not steps: return None
    tw = float(steps[-1]["timestamp"]) - float(steps[0]["timestamp"])
    budget = (t.get("metadata") or {}).get("task_budget")
    if budget is None or budget <= 0 or tw <= 0: return None
    return tw / budget


CAPS = ["T1.1","T1.2","T1.3","T2.1","T2.2","T2.3","T3.1","T3.2","T3.3"]
SETTINGS = ["no_injection", "with_injection"]

print(f"{'cap':5s} {'setting':14s} {'kind':10s} {'n':>4s}  {'stat':>40s}")
print("-"*80)
for cap in CAPS:
    for setting in SETTINGS:
        d = DIR / "anthropic_claude-sonnet-4-6" / cap / setting
        if not d.exists():
            print(f"{cap:5s} {setting:14s} {'-':10s} {'0':>4s}  {'no dir':>40s}")
            continue
        trajs = []
        for p in d.glob("*.json"):
            try: trajs.append(json.loads(p.read_text()))
            except Exception: continue
        n_total = len(trajs)
        if n_total == 0:
            print(f"{cap:5s} {setting:14s} {'-':10s} {'0':>4s}  {'empty':>40s}")
            continue
        if cap == "T1.1":
            n_dec, passes = 0, 0
            for t in trajs:
                steps = t.get("steps") or []
                if not steps: continue
                from datetime import datetime, timezone
                run_date = datetime.fromtimestamp(float(steps[0]["timestamp"]), tz=timezone.utc).isoformat()
                v = t11_pass(steps[-1].get("action",""), run_date)
                if v is None: continue
                n_dec += 1
                if v: passes += 1
            lo, hi = wilson(passes, n_dec) if n_dec else (None, None)
            rate = passes/n_dec if n_dec else None
            stat = f"pass={rate:.2f} [{lo:.2f},{hi:.2f}]" if rate is not None else "no decided"
            print(f"{cap:5s} {setting:14s} {'T1.1':10s} {n_dec:>4d}  {stat:>40s}")
        elif cap == "T2.3":
            cars = [car(t) for t in trajs]
            cars = [c for c in cars if c is not None]
            if cars:
                m = sum(cars)/len(cars)
                stat = f"CAR mean={m:.3f} (n={len(cars)})"
            else:
                stat = "no CAR"
            print(f"{cap:5s} {setting:14s} {'T2.3':10s} {len(cars):>4d}  {stat:>40s}")
        elif cap in {"T3.1","T3.2","T3.3"}:
            rhos = [extract_rho(t) for t in trajs]
            rhos = [r for r in rhos if r is not None]
            if rhos:
                med, lo, hi = bootstrap_signed(rhos)
                stat = f"median rho={med:+.3f} [{lo:+.3f},{hi:+.3f}]"
            else:
                stat = "no rho"
            print(f"{cap:5s} {setting:14s} {'rho':10s} {len(rhos):>4d}  {stat:>40s}")
        else:
            # T1.2, T1.3 (date arithmetic / next event), T2.1, T2.2 — count traj
            print(f"{cap:5s} {setting:14s} {'traj':10s} {n_total:>4d}  {'(rho/CAR parser TBD)':>40s}")
