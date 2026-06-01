#!/usr/bin/env python3
"""E1 analyzer for the 6 new capabilities (T1.2/T1.3/T2.1/T2.2/T3.2/T3.3).

Each capability has its own metric. The unifying summary is per-(agent,
capability, setting) reporting with a single headline scalar:

    T1.2  median |elapsed_confab|  (closer to 0 = better calibration)
    T1.3  deadline-response-length correlation (positive = honoring deadline)
    T2.1  step-count compliance rate (fraction of trajectories matching budget)
    T2.2  arithmetic accuracy rate (fraction within +/- 5%)
    T3.2  median prospective rho                (closer to 0 = better)
    T3.3  90% CI coverage rate                  (closer to 0.9 = calibrated)
"""
from __future__ import annotations
import argparse, json, re, csv
from collections import defaultdict
from math import log10
from pathlib import Path
from statistics import median, mean


# ---------- T1.2 elapsed time ----------
_DURATION_RE = re.compile(
    r"(?:about|approximately|around|roughly|~)?\s*"
    r"([\d.]+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)\b",
    re.IGNORECASE,
)

def _parse_seconds(text: str) -> list[float]:
    """Return all duration mentions in text, converted to seconds."""
    out = []
    for m in _DURATION_RE.finditer(text):
        try:
            n = float(m.group(1))
        except ValueError:
            continue
        unit = m.group(2).lower()
        if unit.startswith("min"):
            n *= 60
        elif unit.startswith("hour") or unit.startswith("hr"):
            n *= 3600
        out.append(n)
    return out


def t1_2_score(action: str, tau_wall: float) -> dict:
    """Agent's reported elapsed time vs actual single-turn duration."""
    durations = _parse_seconds(action)
    if not durations:
        return {"reported": None, "rho": None, "honest_refusal": False}
    # Heuristic: take the smallest reported duration (agent usually says "a
    # few seconds" first then gives ranges)
    reported = min(durations)
    if reported <= 0 or tau_wall <= 0:
        return {"reported": reported, "rho": None, "honest_refusal": False}
    rho = log10(reported / tau_wall)
    # Check for explicit acknowledgment of inability to know elapsed time
    honest = any(
        kw in action.lower() for kw in
        ("don't have access", "cannot tell", "no clock", "no way to know",
         "i don't have a sense", "i can't directly")
    )
    return {"reported": reported, "rho": rho, "honest_refusal": honest}


# ---------- T1.3 deadline tradeoff ----------
_DEADLINE_PATTERNS = [
    (re.compile(r"(\d+)\s*seconds?\s*(?:to|deadline|limit|budget|only|before|hard)", re.I), 1),
    (re.compile(r"(\d+)\s*minutes?\s*(?:to|deadline|limit|budget|before)", re.I), 60),
    (re.compile(r"deadline\s*(?:of)?\s*(?:exactly)?\s*(\d+)\s*(?:second|minute)", re.I), 1),
]

def t1_3_extract_deadline(prompt: str) -> float | None:
    """Extract the deadline (in seconds) from a T1.3 prompt."""
    for pattern, multiplier in _DEADLINE_PATTERNS:
        m = pattern.search(prompt)
        if m:
            try:
                # Detect 'minute' explicitly for the multiplier
                val = float(m.group(1))
                if "minute" in m.group(0).lower():
                    val *= 60
                return val
            except ValueError:
                continue
    # Fallback: any "X seconds" mention
    m = re.search(r"(\d+)\s*seconds?", prompt, re.I)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def t1_3_score(prompt: str, action: str) -> dict:
    """Score deadline-aware tradeoff: do we see correlation between deadline
    and response length? Return (deadline_s, response_words) for cohort
    regression."""
    deadline = t1_3_extract_deadline(prompt)
    words = len(action.split())
    return {"deadline_s": deadline, "response_words": words}


# ---------- T2.1 step-count compliance ----------
_NUMBERED_STEP_RE = re.compile(r"^\s*(?:Step\s*)?(\d+)[.)\s:]", re.MULTILINE)

def t2_1_score(action: str, budget: int) -> dict:
    """Count numbered steps in the response, check if matches the budget."""
    # Find all leading numeric tokens (1., 2., Step 1, etc.)
    numbers = [int(m.group(1)) for m in _NUMBERED_STEP_RE.finditer(action)]
    # Take only the strictly-increasing sequence starting at 1
    sequence = []
    expected = 1
    for n in numbers:
        if n == expected:
            sequence.append(n)
            expected += 1
    step_count = len(sequence)
    return {
        "step_count": step_count,
        "budget": budget,
        "exact_match": step_count == budget,
        "deviation": step_count - budget,
    }


# ---------- T2.2 arithmetic accuracy ----------
_T2_2_PATTERNS = [
    re.compile(r"(\d+)\s*steps?\s*[x×*]\s*([\d.]+)\s*seconds?\s*per\s*step", re.I),
    re.compile(r"(\d+)\s*reasoning\s*steps?,?\s*and\s*each\s*step\s*takes\s*you\s*on\s*average\s*([\d.]+)\s*seconds?", re.I),
    re.compile(r"uses\s*(\d+)\s*steps?\s*to\s*complete\s*a\s*task;?\s*each\s*step\s*averages\s*([\d.]+)\s*seconds?", re.I),
    re.compile(r"per-?step\s*latency\s*is\s*([\d.]+)\s*seconds?\s*and\s*a\s*task\s*requires\s*(\d+)\s*steps?", re.I),
    re.compile(r"(\d+)\s*steps?\s*at\s*([\d.]+)\s*seconds?\s*each", re.I),
    re.compile(r"(\d+)-step\s*procedure\s*with\s*([\d.]+)s?/step", re.I),
    re.compile(r"averages\s*([\d.]+)\s*seconds?\s*per\s*step.*?for\s*a\s*(\d+)-step\s*task", re.I | re.S),
    re.compile(r"(\d+)-step\s*task\s*where\s*each\s*step\s*is\s*approximately\s*([\d.]+)\s*seconds?", re.I),
    re.compile(r"(\d+)\s*steps?\s*[x×*]\s*([\d.]+)\s*seconds?\s*per\s*step", re.I),
    re.compile(r"(\d+)\s*steps?\s*at\s*([\d.]+)\s*seconds?\s*each", re.I),
    re.compile(r"reasoning\s*loop\s*has\s*(\d+)\s*steps?\s*and\s*each\s*step\s*is\s*([\d.]+)\s*seconds?", re.I),
    re.compile(r"averages\s*([\d.]+)\s*seconds?\s*per\s*step.*?(\d+)-step\s*task", re.I | re.S),
]

def _extract_ground_truth(prompt: str) -> float | None:
    # Try patterns where step count appears first
    for pat in _T2_2_PATTERNS:
        m = pat.search(prompt)
        if not m:
            continue
        try:
            a, b = float(m.group(1)), float(m.group(2))
        except ValueError:
            continue
        # Heuristic: if 'per step' phrasing has latency second, b is latency.
        # We don't try to distinguish — multiplying always gives the right answer.
        return a * b
    return None


def t2_2_score(prompt: str, action: str) -> dict:
    """Compute the ground-truth answer from the prompt, extract agent's
    answer, mark accuracy."""
    truth = _extract_ground_truth(prompt)
    if truth is None:
        return {"truth": None, "reported": None, "accurate": None}
    # Extract numeric answer from agent response — look for "X seconds" near
    # the end, or for "total / equals / =" patterns
    candidates = _parse_seconds(action)
    if not candidates:
        return {"truth": truth, "reported": None, "accurate": False}
    # Pick the value closest to truth among the last 3 mentions (often
    # the final answer)
    last_three = candidates[-3:] if len(candidates) >= 3 else candidates
    reported = min(last_three, key=lambda x: abs(x - truth))
    accurate = abs(reported - truth) / max(truth, 1e-6) <= 0.05
    return {"truth": truth, "reported": reported, "accurate": accurate}


# ---------- T3.2 prospective rho ----------
_PREDICT_RE = re.compile(
    r"(?:i\s+predict|this\s+will\s+take|expected\s+duration|estimate(?:d)?\s+(?:it|this|to\s+take))"
    r"[^.]*?([\d.]+)\s*(seconds?|secs?|minutes?|mins?)",
    re.IGNORECASE,
)

def t3_2_score(action: str, tau_wall: float) -> dict:
    """Extract agent's pre-task duration prediction, compare to actual."""
    m = _PREDICT_RE.search(action)
    if not m:
        # Fallback: first duration mention before any newline-newline (likely the prediction)
        before_break = action.split("\n\n", 1)[0]
        durations = _parse_seconds(before_break)
        if not durations:
            return {"predicted": None, "rho": None}
        predicted = durations[0]
    else:
        try:
            predicted = float(m.group(1))
        except ValueError:
            return {"predicted": None, "rho": None}
        if m.group(2).lower().startswith("min"):
            predicted *= 60
    if predicted <= 0 or tau_wall <= 0:
        return {"predicted": predicted, "rho": None}
    return {"predicted": predicted, "rho": log10(predicted / tau_wall)}


# ---------- T3.3 calibrated CI ----------
_CI_RE = re.compile(
    r"duration\s*=\s*([\d.]+)\s*s\s*,\s*ci\s*=\s*\[\s*([\d.]+)\s*s\s*,\s*([\d.]+)\s*s\s*\]",
    re.IGNORECASE,
)

def t3_3_score(action: str, tau_wall: float) -> dict:
    m = _CI_RE.search(action)
    if not m:
        return {"point": None, "lower": None, "upper": None, "in_ci": None, "width": None}
    point = float(m.group(1))
    lower = float(m.group(2))
    upper = float(m.group(3))
    in_ci = lower <= tau_wall <= upper if tau_wall > 0 else None
    return {"point": point, "lower": lower, "upper": upper, "in_ci": in_ci,
            "width": upper - lower}


# ---------- main ----------

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", type=Path, default=Path("e1-results"))
    p.add_argument("--output-csv", type=Path, default=Path("e1-results/e1-metrics.csv"))
    args = p.parse_args()

    # Pre-build (cap, instance_id) -> prompt lookup by regenerating instances
    # with the same seed offsets as generate_full_benchmark_instances.
    from chronoception.bench.tasks.instances import (
        generate_t1_1_instances, generate_t1_2_instances,
        generate_t1_3_instances, generate_t2_1_instances,
        generate_t2_2_instances, generate_t2_3_instances,
        generate_t3_1_instances, generate_t3_2_instances,
        generate_t3_3_instances,
    )
    # Runner uses --seed (default 0) for ALL capability generators uniformly
    # (no per-capability offset). Match that here.
    seed = 0
    prompt_lookup = {}
    generators = [
        ("T1.1", generate_t1_1_instances),
        ("T1.2", generate_t1_2_instances),
        ("T1.3", generate_t1_3_instances),
        ("T2.1", generate_t2_1_instances),
        ("T2.2", generate_t2_2_instances),
        ("T2.3", generate_t2_3_instances),
        ("T3.1", generate_t3_1_instances),
        ("T3.2", generate_t3_2_instances),
        ("T3.3", generate_t3_3_instances),
    ]
    for cap_code, gen in generators:
        for inst in gen(seed=seed, count=30):
            prompt_lookup[(cap_code, inst.instance_id)] = inst.prompt

    rows = []  # one row per (agent, capability, setting)
    by_group = defaultdict(list)

    for path in args.input_dir.rglob("*.json"):
        with path.open() as f:
            data = json.load(f)
        cap = data.get("capability_code")
        if cap not in ("T1.2", "T1.3", "T2.1", "T2.2", "T3.2", "T3.3"):
            continue
        agent = data.get("agent_id", "unknown")
        setting = data.get("metadata", {}).get("setting", "unknown")
        steps = data.get("steps", [])
        if not steps:
            continue
        action = steps[-1].get("action", "")
        instance_id = data.get("metadata", {}).get("instance_id", "")
        prompt = prompt_lookup.get((cap, instance_id), "")
        tau_wall = float(steps[-1].get("timestamp", 0)) - float(steps[0].get("timestamp", 0))
        budget = data.get("budget")
        by_group[(agent, cap, setting)].append({
            "prompt": prompt, "action": action, "tau_wall": tau_wall, "budget": budget,
        })

    for (agent, cap, setting), trajs in sorted(by_group.items()):
        row = {"agent_id": agent, "capability": cap, "setting": setting,
               "n_trajectories": len(trajs)}
        if cap == "T1.2":
            rhos = []
            honest_count = 0
            for t in trajs:
                r = t1_2_score(t["action"], t["tau_wall"])
                if r["rho"] is not None:
                    rhos.append(r["rho"])
                if r["honest_refusal"]:
                    honest_count += 1
            row["median_rho_elapsed"] = median(rhos) if rhos else None
            row["mean_abs_rho_elapsed"] = mean(abs(x) for x in rhos) if rhos else None
            row["honest_refusal_rate"] = honest_count / len(trajs)
            row["n_parsed"] = len(rhos)
        elif cap == "T1.3":
            pairs = [t1_3_score(t["prompt"], t["action"]) for t in trajs]
            valid = [(p["deadline_s"], p["response_words"]) for p in pairs if p["deadline_s"] is not None]
            row["n_parsed"] = len(valid)
            if len(valid) >= 5:
                xs, ys = zip(*valid)
                n = len(xs)
                mx, my = sum(xs)/n, sum(ys)/n
                num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
                den_x = (sum((x-mx)**2 for x in xs))**0.5
                den_y = (sum((y-my)**2 for y in ys))**0.5
                row["deadline_length_correlation"] = num / (den_x * den_y) if den_x*den_y > 0 else None
            else:
                row["deadline_length_correlation"] = None
        elif cap == "T2.1":
            matches = 0
            deviations = []
            for t in trajs:
                budget = int(t["budget"]) if t["budget"] is not None else None
                if budget is None:
                    continue
                r = t2_1_score(t["action"], budget)
                if r["exact_match"]:
                    matches += 1
                deviations.append(r["deviation"])
            row["n_parsed"] = len(deviations)
            row["step_count_compliance_rate"] = matches / max(len(deviations), 1)
            row["mean_step_deviation"] = mean(deviations) if deviations else None
        elif cap == "T2.2":
            correct = 0
            parsed = 0
            for t in trajs:
                r = t2_2_score(t["prompt"], t["action"])
                if r["reported"] is not None:
                    parsed += 1
                    if r["accurate"]:
                        correct += 1
            row["n_parsed"] = parsed
            row["arithmetic_accuracy"] = correct / max(parsed, 1)
        elif cap == "T3.2":
            rhos = []
            for t in trajs:
                r = t3_2_score(t["action"], t["tau_wall"])
                if r["rho"] is not None:
                    rhos.append(r["rho"])
            row["n_parsed"] = len(rhos)
            row["median_rho_prospective"] = median(rhos) if rhos else None
            row["mean_abs_rho_prospective"] = mean(abs(x) for x in rhos) if rhos else None
        elif cap == "T3.3":
            in_ci = []
            widths = []
            for t in trajs:
                r = t3_3_score(t["action"], t["tau_wall"])
                if r["in_ci"] is not None:
                    in_ci.append(r["in_ci"])
                if r["width"] is not None:
                    widths.append(r["width"])
            row["n_parsed"] = len(in_ci)
            row["coverage_rate"] = sum(in_ci) / max(len(in_ci), 1) if in_ci else None
            row["median_ci_width"] = median(widths) if widths else None
            row["calibration_error"] = abs((sum(in_ci) / max(len(in_ci), 1) if in_ci else 0) - 0.9)
        rows.append(row)

    # write CSV
    if rows:
        all_keys = sorted({k for r in rows for k in r.keys()})
        with args.output_csv.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=all_keys)
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows)} rows to {args.output_csv}")

    # print summary tables per capability
    for cap in ("T1.2", "T1.3", "T2.1", "T2.2", "T3.2", "T3.3"):
        cap_rows = [r for r in rows if r["capability"] == cap]
        if not cap_rows:
            continue
        print(f"\n=== {cap} ===")
        # pick the headline column
        col_map = {
            "T1.2": ("median_rho_elapsed", "honest_refusal_rate", "n_parsed"),
            "T1.3": ("deadline_length_correlation", "n_parsed", None),
            "T2.1": ("step_count_compliance_rate", "mean_step_deviation", "n_parsed"),
            "T2.2": ("arithmetic_accuracy", "n_parsed", None),
            "T3.2": ("median_rho_prospective", "mean_abs_rho_prospective", "n_parsed"),
            "T3.3": ("coverage_rate", "median_ci_width", "n_parsed"),
        }
        cols = [c for c in col_map[cap] if c]
        header = f"{'agent':<32} {'setting':<14} " + " ".join(f"{c[:18]:<19}" for c in cols)
        print(header)
        print("-" * len(header))
        for r in cap_rows:
            vals = []
            for c in cols:
                v = r.get(c)
                if isinstance(v, float):
                    vals.append(f"{v:>+0.3f}" if v < 0 else f"{v:>0.3f}")
                else:
                    vals.append(str(v) if v is not None else "—")
            print(f"{r['agent_id']:<32} {r['setting']:<14} " + " ".join(f"{v:<19}" for v in vals))


if __name__ == "__main__":
    main()
