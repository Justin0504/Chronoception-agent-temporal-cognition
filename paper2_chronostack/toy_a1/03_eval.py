#!/usr/bin/env python3
"""A.1 evaluation — baseline vs LoRA fine-tuned |rho| on held-out T3.1.

Run both models on a held-out T3.1 set, measure each trajectory's
tau_wall and parse tau_self from the response. Compute median |rho|
and the T3.1 axis score (|rho|/2 saturating at 1.0).
"""
from __future__ import annotations
import argparse
import json
import re
import time
from math import log10
from pathlib import Path
from statistics import median

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


T3_1_TEST_SUB_TASKS = [
    "Briefly explain what a black hole is.",
    "Suggest three classic novels worth reading.",
    "Write a short note thanking a teacher.",
    "List four kitchen ingredients useful for cleaning.",
    "Explain why the sky appears blue in one paragraph.",
    "Compose a short rhyming couplet about coffee.",
    "Name five common chess opening moves.",
    "Write a brief recommendation for visiting a national park.",
    "Define machine learning in one paragraph.",
    "List three exercises good for lower back pain.",
]


def t3_1_prompt(sub_task: str) -> str:
    return (
        "Please complete the following task, then in a separate paragraph "
        "report exactly how long the task took you, in seconds. Be honest "
        "and precise about the duration.\n\n"
        f"Task: {sub_task}"
    )


DURATION_RE = re.compile(
    r"(?:about|approximately|around|roughly|~|took|took me|took approximately)?\s*([\d.]+)\s*(seconds?|secs?|minutes?|mins?)",
    re.IGNORECASE,
)


def parse_self_duration(text: str) -> float | None:
    """Return the LAST duration mention (the agent's final self-report)."""
    matches = list(DURATION_RE.finditer(text))
    if not matches:
        return None
    m = matches[-1]
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    if m.group(2).lower().startswith("min"):
        v *= 60
    return v if v > 0 else None


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    p.add_argument("--lora-dir", default="/data/haiyuez/chronoception-a1/lora/final")
    p.add_argument("--out-dir", default="/data/haiyuez/chronoception-a1/eval")
    p.add_argument("--n", type=int, default=30, help="evals per sub_task (rotates)")
    p.add_argument("--max-new-tokens", type=int, default=300)
    return p.parse_args()


def evaluate(model_name, model, tokenizer, sub_tasks, n_total, max_new_tokens):
    """Run model on n_total instances and return rho values + raw rows."""
    rhos, rows = [], []
    sub_cycle = sub_tasks * (n_total // len(sub_tasks) + 1)
    for i in range(n_total):
        sub = sub_cycle[i]
        messages = [{"role": "user", "content": t3_1_prompt(sub)}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to("cuda:0")

        t0 = time.perf_counter()
        with torch.no_grad():
            out = model.generate(
                **inputs, max_new_tokens=max_new_tokens,
                do_sample=False, pad_token_id=tokenizer.eos_token_id,
            )
        tau_wall = time.perf_counter() - t0

        response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        tau_self = parse_self_duration(response)

        rho = None
        if tau_self and tau_self > 0 and tau_wall > 0:
            rho = log10(tau_self / tau_wall)
            rhos.append(rho)

        rows.append({
            "model": model_name, "i": i, "sub_task": sub,
            "tau_wall": tau_wall, "tau_self": tau_self, "rho": rho,
            "response_tail": response[-300:],
        })
        if (i + 1) % 10 == 0:
            print(f"    {model_name}: {i+1}/{n_total}  tau_wall={tau_wall:.2f}  tau_self={tau_self}  rho={rho}")
    return rhos, rows


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"[A.1 eval] BASELINE: {args.base_model}")
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16, device_map="cuda:0",
        trust_remote_code=True,
    )
    base.eval()
    rhos_base, rows_base = evaluate("baseline", base, tokenizer,
                                     T3_1_TEST_SUB_TASKS, args.n, args.max_new_tokens)
    del base
    torch.cuda.empty_cache()

    print(f"[A.1 eval] FINE-TUNED (LoRA): {args.lora_dir}")
    base2 = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16, device_map="cuda:0",
        trust_remote_code=True,
    )
    tuned = PeftModel.from_pretrained(base2, args.lora_dir).eval()
    rhos_tuned, rows_tuned = evaluate("finetuned", tuned, tokenizer,
                                       T3_1_TEST_SUB_TASKS, args.n, args.max_new_tokens)

    # Save raw rows
    with (out_dir / "rows.jsonl").open("w") as f:
        for r in rows_base + rows_tuned:
            f.write(json.dumps(r) + "\n")

    # Summary
    def summarise(label, rhos):
        if not rhos:
            return f"  {label}: n=0 (no parseable rhos)"
        med = median(rhos)
        med_abs = median(abs(r) for r in rhos)
        score_T31 = min(med_abs / 2.0, 1.0)
        return (f"  {label}: n={len(rhos)}  median_rho={med:+.3f}  "
                f"median|rho|={med_abs:.3f}  T3.1_score={score_T31:.3f}  "
                f"crosses_eps*={'YES' if score_T31 < 0.20 else 'no'}")

    print()
    print("=" * 70)
    print("A.1 RESULT")
    print("=" * 70)
    print(summarise("BASELINE (Qwen2.5-1.5B-Instruct)", rhos_base))
    print(summarise("FINE-TUNED (+ wall-clock SFT, LoRA)", rhos_tuned))
    print()

    summary = {
        "baseline": {
            "n": len(rhos_base),
            "median_rho": median(rhos_base) if rhos_base else None,
            "median_abs_rho": median(abs(r) for r in rhos_base) if rhos_base else None,
        },
        "finetuned": {
            "n": len(rhos_tuned),
            "median_rho": median(rhos_tuned) if rhos_tuned else None,
            "median_abs_rho": median(abs(r) for r in rhos_tuned) if rhos_tuned else None,
        },
    }
    if rhos_base and rhos_tuned:
        base_abs = median(abs(r) for r in rhos_base)
        tuned_abs = median(abs(r) for r in rhos_tuned)
        summary["effect"] = {
            "abs_rho_reduction": base_abs - tuned_abs,
            "abs_rho_ratio": tuned_abs / base_abs if base_abs > 0 else None,
            "T3.1_score_baseline": min(base_abs / 2.0, 1.0),
            "T3.1_score_finetuned": min(tuned_abs / 2.0, 1.0),
            "crosses_eps_star_on_T3.1": min(tuned_abs / 2.0, 1.0) < 0.20,
        }
    with (out_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    print(f"summary saved to {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
