#!/usr/bin/env python3
"""A.1 data generation — produce (prompt, response_with_self_duration) pairs.

For each T3.1-style prompt, run the base model to get a response and measure
actual wall-clock generation time. Construct an SFT training pair where the
response ends with an accurate self-duration annotation. Mimics what a
chronoception-supporting loss would teach the model to produce.

Output: a JSON-Lines file with fields {prompt, target, tau_wall_actual}.
"""
from __future__ import annotations
import argparse
import json
import random
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# T3.1 sub-task seeds (mirror chronoception/bench/tasks/instances.py T3_1_SUB_TASKS)
T3_1_SUB_TASKS = [
    "Write a haiku about autumn.",
    "Compute the sum of the first ten prime numbers.",
    "List five surprising facts about the Roman Empire.",
    "Summarize the plot of any Shakespeare play in three sentences.",
    "Explain what photosynthesis is in plain language.",
    "Write a short paragraph describing a sunset over a city.",
    "Suggest three book recommendations on the history of mathematics.",
    "Translate the phrase 'good morning' into five different languages.",
    "Compose a brief congratulatory message for a friend's promotion.",
    "Write a quick note explaining why TCP differs from UDP.",
    "Describe the smell of fresh bread in one paragraph.",
    "List four common cognitive biases with one-sentence definitions.",
    "Write a four-line limerick about a clumsy cat.",
    "Explain Bayes' theorem in two sentences.",
    "Recommend three productivity techniques for graduate students.",
    "Summarize the laws of thermodynamics in plain language.",
    "Compose an apology message for missing a friend's birthday.",
    "List five winter holiday traditions from different cultures.",
    "Describe how a transformer attention head works in one paragraph.",
    "Write a short pep talk for someone starting their first marathon.",
]


def t3_1_prompt(sub_task: str) -> str:
    return (
        "Please complete the following task, then in a separate paragraph "
        "report exactly how long the task took you, in seconds. Be honest "
        "and precise about the duration.\n\n"
        f"Task: {sub_task}"
    )


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    p.add_argument("--n-train", type=int, default=500)
    p.add_argument("--n-eval", type=int, default=100)
    p.add_argument("--out-dir", default="/data/haiyuez/chronoception-a1/data")
    p.add_argument("--noise-pct", type=float, default=0.15,
                   help="Gaussian noise on reported duration (relative to tau_wall)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-new-tokens", type=int, default=300)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    print(f"[A.1] loading {args.model}...")
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, device_map="cuda:0",
        trust_remote_code=True,
    )
    model.eval()

    train_path = out_dir / "train.jsonl"
    eval_path = out_dir / "eval.jsonl"

    def gen_pairs(n: int, path: Path) -> None:
        n_done = 0
        with path.open("w") as f:
            while n_done < n:
                sub = rng.choice(T3_1_SUB_TASKS)
                prompt = t3_1_prompt(sub)
                messages = [{"role": "user", "content": prompt}]
                input_text = tok.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                inputs = tok(input_text, return_tensors="pt").to("cuda:0")
                t0 = time.perf_counter()
                with torch.no_grad():
                    out = model.generate(
                        **inputs,
                        max_new_tokens=args.max_new_tokens,
                        do_sample=True, temperature=0.7, top_p=0.9,
                        pad_token_id=tok.eos_token_id,
                    )
                tau_wall = time.perf_counter() - t0
                response_tokens = out[0][inputs["input_ids"].shape[1]:]
                response = tok.decode(response_tokens, skip_special_tokens=True).strip()

                if not response:
                    continue

                # Noisy honest self-duration estimate (target for SFT)
                noise = rng.gauss(0, args.noise_pct * tau_wall)
                reported = max(0.1, tau_wall + noise)
                target = f"{response}\n\nThis task took approximately {reported:.1f} seconds."

                rec = {
                    "prompt": prompt,
                    "target": target,
                    "tau_wall_actual": tau_wall,
                    "tau_reported": reported,
                    "sub_task": sub,
                }
                f.write(json.dumps(rec) + "\n")
                n_done += 1
                if n_done % 25 == 0:
                    print(f"  [{path.name}] {n_done}/{n}  tau_wall={tau_wall:.2f}s  reported={reported:.1f}s")

    print(f"[A.1] generating {args.n_train} train pairs...")
    gen_pairs(args.n_train, train_path)
    print(f"[A.1] generating {args.n_eval} eval pairs...")
    gen_pairs(args.n_eval, eval_path)
    print(f"[A.1] done. train → {train_path}, eval → {eval_path}")


if __name__ == "__main__":
    main()
