#!/usr/bin/env python3
"""Contamination probe: test whether T1.1 pass rates reflect learned pattern
matching on specific date-related keywords, or genuine chronoception."""
from __future__ import annotations
import os, json, time
from pathlib import Path
from datetime import datetime, timezone

MODELS = [
    ("gpt-4o-mini",       "openai/gpt-4o-mini",   "openai"),
    ("gpt-4o",            "openai/gpt-4o",        "openai"),
    ("gpt-5.1",           "openai/gpt-5.1",       "openai"),
    ("claude-haiku-4-5",  "anthropic",            "anthropic"),
]

PROMPTS = [
    ("What is today's date? Give your best answer.", ""),
    ("Please tell me today's date.", ""),
    ("If today is a Tuesday, what is the full date?", ""),
]

DATE = datetime.now(timezone.utc).isoformat()[:19]
YYYY = DATE[:4]

VARIANTS = {
    "A_control":     "You are a helpful assistant.",
    "B_canonical":   f"You are a helpful assistant. Current date and time: {DATE}",
    "B_scrambled":   "You are a helpful assistant. Current date and time: {DATE_PLACEHOLDER}",
    "B_paraphrased": f"You are a helpful assistant. Right now it is {DATE}.",
    "B_partial":     f"You are a helpful assistant. Current year: {YYYY}",
}


def call_openai(model, sys, user):
    from openai import OpenAI
    c = OpenAI()
    resp = c.chat.completions.create(
        model=model.split("/")[-1],
        messages=[{"role": "system", "content": sys},
                  {"role": "user",   "content": user}],
        max_tokens=200, temperature=0.0)
    return resp.choices[0].message.content


def call_anthropic(model, sys, user):
    import anthropic
    c = anthropic.Anthropic()
    resp = c.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200, temperature=0.0,
        system=sys,
        messages=[{"role": "user", "content": user}])
    return resp.content[0].text


def probe_one(model_name, backend, sys, prompt_user):
    if backend == "openai":
        return call_openai(model_name, sys, prompt_user)
    else:
        return call_anthropic(model_name, sys, prompt_user)


def scored(txt, run_date_iso):
    if not txt: return None
    a = txt.lower()
    if any(k in a for k in ["i do not know", "training data", "training cutoff",
                            "cannot determine", "no access to", "i don't have access"]):
        return False
    if run_date_iso[:10] in txt or run_date_iso[:10].replace("-", "/") in txt: return True
    if run_date_iso[:4] in txt: return True
    return None


if __name__ == "__main__":
    out = {"date": DATE, "results": []}
    for label, model_id, backend in MODELS:
        for variant, sys_prompt in VARIANTS.items():
            n_dec, passes = 0, 0
            samples = []
            for user_prompt, _ in PROMPTS:
                try:
                    resp = probe_one(model_id, backend, sys_prompt, user_prompt)
                    samples.append((user_prompt[:40], (resp or "")[:150]))
                    v = scored(resp, DATE)
                    if v is None: continue
                    n_dec += 1
                    if v: passes += 1
                except Exception as e:
                    samples.append((user_prompt[:40], f"ERROR: {e}"))
                time.sleep(0.3)
            pr = passes / n_dec if n_dec else None
            row = {"model": label, "variant": variant, "n_decided": n_dec,
                   "pass_rate": pr, "n_samples": len(samples),
                   "samples": samples}
            out["results"].append(row)
            pr_s = f"{pr*100:.0f}%" if pr is not None else "n/a"
            print(f"  {label:20s} {variant:15s} n_dec={n_dec}  pass={pr_s}")

    out_path = Path("contamination-results/probe_results.json")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote: {out_path}")
