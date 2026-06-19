#!/usr/bin/env python3
"""E-ARCH stage 1 — generate (prompt, response, tau_wall) and build time-token SFT data.

Mirrors A.1's generation but writes E-ARCH examples: the target carries the
ACCURATE duration and the same value is supplied as the time-token feature vector
(via chronoception.stack.eparch_data.make_training_example), so the model learns
to READ the token rather than estimate. Runs on the lab GPU cluster.

Output JSONL fields: {prompt, target, tau_wall, time_features, sub_task}.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from chronoception.stack.eparch_data import make_training_example  # noqa: E402

# Reuse the A.1 sub-task pool (T3.1-style).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toy_a1"))
try:
    from importlib import import_module
    _gen = import_module("01_generate_sft")  # type: ignore
    T3_1_SUB_TASKS = _gen.T3_1_SUB_TASKS
    t3_1_prompt = _gen.t3_1_prompt
except Exception:  # fallback: minimal inline copy
    T3_1_SUB_TASKS = [
        "Write a haiku about autumn.", "Compute the sum of the first ten prime numbers.",
        "List five surprising facts about the Roman Empire.", "Explain photosynthesis in plain language.",
        "Suggest three book recommendations on the history of mathematics.",
    ]
    def t3_1_prompt(sub: str) -> str:
        return ("Please complete the following task, then in a separate paragraph "
                "report exactly how long the task took you, in seconds. Be honest "
                f"and precise about the duration.\n\nTask: {sub}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    p.add_argument("--n-train", type=int, default=500)
    p.add_argument("--n-eval", type=int, default=100)
    p.add_argument("--out-dir", default="/data/haiyuez/chronoception-eparch/data")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-new-tokens", type=int, default=300)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    print(f"[E-ARCH] loading {args.model}...")
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, device_map="cuda:0", trust_remote_code=True
    ).eval()

    def gen(n: int, path: Path) -> None:
        done = 0
        with path.open("w") as f:
            while done < n:
                sub = rng.choice(T3_1_SUB_TASKS)
                prompt = t3_1_prompt(sub)
                text = tok.apply_chat_template(
                    [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
                )
                inputs = tok(text, return_tensors="pt").to("cuda:0")
                t0 = time.perf_counter()
                with torch.no_grad():
                    out = model.generate(**inputs, max_new_tokens=args.max_new_tokens,
                                         do_sample=True, temperature=0.7, top_p=0.9,
                                         pad_token_id=tok.eos_token_id)
                tau_wall = time.perf_counter() - t0
                resp = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
                if not resp:
                    continue
                ex = make_training_example(prompt, resp, tau_wall)
                ex["sub_task"] = sub
                f.write(json.dumps(ex) + "\n")
                done += 1
                if done % 25 == 0:
                    print(f"  [{path.name}] {done}/{n}  tau_wall={tau_wall:.2f}s")

    print(f"[E-ARCH] generating {args.n_train} train + {args.n_eval} eval examples...")
    gen(args.n_train, out_dir / "train.jsonl")
    gen(args.n_eval, out_dir / "eval.jsonl")
    print(f"[E-ARCH] done -> {out_dir}")


if __name__ == "__main__":
    main()
