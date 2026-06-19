#!/usr/bin/env python3
"""E-ARCH stage 3 — the extrapolation test.

The defining question for route 4: does the model READ the time token, or did it
merely learn the training duration distribution (like A.1)? We inject elapsed
values into the time token -- some inside the training range, some far outside --
and check whether the reported duration tracks the injected value. A reader
grounds in AND out of range; a distribution-memorizer grounds only in range.

For each injected elapsed value we generate on held-out T3.1 prompts, parse the
reported duration, and record {injected_elapsed, tau_self}. The analysis is the
torch-free chronoception.stack.eparch_data.extrapolation_report.

Runs on the lab GPU cluster.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from chronoception.stack.eparch_data import extrapolation_report, time_features_for_elapsed  # noqa: E402
from chronoception.stack.time_token import TimeTokenModel, TimeTokenProjector  # noqa: E402

T3_1_TEST_SUB_TASKS = [
    "Briefly explain what a black hole is.",
    "Suggest three classic novels worth reading.",
    "Write a short note thanking a teacher.",
    "Explain why the sky appears blue in one paragraph.",
    "Name five common chess opening moves.",
    "Define machine learning in one paragraph.",
]


def t3_1_prompt(sub: str) -> str:
    return ("Please complete the following task, then in a separate paragraph "
            "report exactly how long the task took you, in seconds. Be honest "
            f"and precise about the duration.\n\nTask: {sub}")


_DUR_RE = re.compile(r"([\d.]+)\s*(seconds?|secs?|minutes?|mins?)", re.IGNORECASE)


def parse_self_duration(text: str) -> float | None:
    ms = list(_DUR_RE.finditer(text))
    if not ms:
        return None
    m = ms[-1]
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
    p.add_argument("--out-dir", default="/data/haiyuez/chronoception-eparch/out")
    p.add_argument("--train-lo", type=float, default=2.0, help="train elapsed range low (s)")
    p.add_argument("--train-hi", type=float, default=15.0, help="train elapsed range high (s)")
    p.add_argument("--inject", default="3,8,12,60,120,240",
                   help="comma elapsed values to inject (mix in- and out-of-range)")
    p.add_argument("--reps", type=int, default=6, help="prompts per injected value")
    p.add_argument("--max-new-tokens", type=int, default=300)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    dev = "cuda:0"

    tok = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16, device_map=dev, trust_remote_code=True
    )
    base = PeftModel.from_pretrained(base, str(out_dir / "lora")).eval()
    projector = TimeTokenProjector(hidden_size=base.config.hidden_size).to(dev, dtype=torch.bfloat16)
    projector.load_state_dict(torch.load(out_dir / "projector.pt", map_location=dev))
    projector.eval()
    model = TimeTokenModel(base, projector)

    inject_vals = [float(x) for x in args.inject.split(",")]
    rows = []
    for elapsed in inject_vals:
        feats = torch.tensor([time_features_for_elapsed(elapsed)], dtype=torch.float, device=dev)
        for r in range(args.reps):
            sub = T3_1_TEST_SUB_TASKS[r % len(T3_1_TEST_SUB_TASKS)]
            text = tok.apply_chat_template(
                [{"role": "user", "content": t3_1_prompt(sub)}], tokenize=False, add_generation_prompt=True
            )
            enc = tok(text, return_tensors="pt").to(dev)
            out = model.generate(
                input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
                time_features=feats, max_new_tokens=args.max_new_tokens,
                do_sample=False, pad_token_id=tok.eos_token_id,
            )
            resp = tok.decode(out[0], skip_special_tokens=True).strip()
            tau_self = parse_self_duration(resp)
            rows.append({"injected_elapsed": elapsed, "tau_self": tau_self,
                         "sub_task": sub, "response_tail": resp[-200:]})
        print(f"  injected={elapsed:.0f}s  reported={[r['tau_self'] for r in rows[-args.reps:]]}")

    (out_dir / "eval_rows.jsonl").open("w").write(
        "\n".join(json.dumps(r) for r in rows) + "\n"
    )
    report = extrapolation_report(rows, args.train_lo, args.train_hi)

    print("\n" + "=" * 66)
    print("E-ARCH EXTRAPOLATION TEST")
    print("=" * 66)
    print(f"train range: {report['train_range']}  (in-range n={report['n_in_range']}, "
          f"out-of-range n={report['n_out_range']})")
    print(f"median |rho| in-range  : {report['median_abs_rho_in_range']}")
    print(f"median |rho| out-range : {report['median_abs_rho_out_range']}")
    print(f"READS THE CHANNEL (grounds out-of-range)? {report['reads_channel']}")
    print("=" * 66)
    with (out_dir / "extrapolation_summary.json").open("w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
