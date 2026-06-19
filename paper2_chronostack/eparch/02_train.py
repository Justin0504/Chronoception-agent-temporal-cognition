#!/usr/bin/env python3
"""E-ARCH stage 2 — LoRA + time-token projector training (manual loop).

A.1 reuses SFTTrainer, but E-ARCH prepends a continuous, feature-derived time
token to the input embeddings, which SFTTrainer does not model. So we run a small
explicit loop over a TimeTokenModel (base + LoRA + projector); both the LoRA
adapters and the projector are trained on standard CE over the target tokens.

Validate the mechanism first (no GPU needed):
    python -c "from chronoception.stack.time_token import smoke_test; smoke_test()"

Then on the cluster:
    python 02_train.py   # reads data/, writes lora/ + projector.pt

Runs on the lab GPU cluster in the A.1 a1venv.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from chronoception.stack.time_token import TimeTokenModel, TimeTokenProjector  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    p.add_argument("--data-dir", default="/data/haiyuez/chronoception-eparch/data")
    p.add_argument("--out-dir", default="/data/haiyuez/chronoception-eparch/out")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--grad-accum", type=int, default=4)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--lora-rank", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--max-len", type=int, default=1024)
    return p.parse_args()


class EArchDataset(Dataset):
    def __init__(self, path: Path, tok, max_len: int) -> None:
        self.rows = [json.loads(line) for line in path.open()]
        self.tok = tok
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, i: int) -> dict:
        ex = self.rows[i]
        prompt_text = self.tok.apply_chat_template(
            [{"role": "user", "content": ex["prompt"]}], tokenize=False, add_generation_prompt=True
        )
        full_text = self.tok.apply_chat_template(
            [{"role": "user", "content": ex["prompt"]},
             {"role": "assistant", "content": ex["target"]}], tokenize=False
        )
        full = self.tok(full_text, truncation=True, max_length=self.max_len)
        prompt_ids = self.tok(prompt_text)["input_ids"]
        input_ids = full["input_ids"]
        labels = list(input_ids)
        for j in range(min(len(prompt_ids), len(labels))):  # mask the prompt
            labels[j] = -100
        return {
            "input_ids": input_ids,
            "attention_mask": full["attention_mask"],
            "labels": labels,
            "time_features": ex["time_features"],
        }


def collate(batch, pad_id: int):
    maxlen = max(len(b["input_ids"]) for b in batch)
    ids, masks, labs = [], [], []
    for b in batch:
        n = maxlen - len(b["input_ids"])
        ids.append(b["input_ids"] + [pad_id] * n)
        masks.append(b["attention_mask"] + [0] * n)
        labs.append(b["labels"] + [-100] * n)
    return {
        "input_ids": torch.tensor(ids, dtype=torch.long),
        "attention_mask": torch.tensor(masks, dtype=torch.long),
        "labels": torch.tensor(labs, dtype=torch.long),
        "time_features": torch.tensor([b["time_features"] for b in batch], dtype=torch.float),
    }


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dev = "cuda:0"

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, device_map=dev, trust_remote_code=True
    )
    lora_cfg = LoraConfig(
        r=args.lora_rank, lora_alpha=args.lora_alpha, lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none", task_type="CAUSAL_LM",
    )
    base = get_peft_model(base, lora_cfg)
    projector = TimeTokenProjector(hidden_size=base.config.hidden_size).to(dev, dtype=torch.bfloat16)
    model = TimeTokenModel(base, projector)
    base.print_trainable_parameters()

    ds = EArchDataset(Path(args.data_dir) / "train.jsonl", tok, args.max_len)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True,
                    collate_fn=lambda b: collate(b, tok.pad_token_id))

    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr)
    total_steps = (len(dl) // args.grad_accum) * args.epochs
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(total_steps, 1))

    model.train()
    step = 0
    for epoch in range(args.epochs):
        for it, batch in enumerate(dl):
            batch = {k: v.to(dev) for k, v in batch.items()}
            out = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"],
                        time_features=batch["time_features"], labels=batch["labels"])
            loss = out.loss / args.grad_accum
            loss.backward()
            if (it + 1) % args.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                opt.step(); sched.step(); opt.zero_grad()
                step += 1
                if step % 10 == 0:
                    print(f"  epoch {epoch} step {step}/{total_steps} loss={out.loss.item():.4f}")

    base.save_pretrained(str(out_dir / "lora"))
    torch.save(projector.state_dict(), out_dir / "projector.pt")
    print(f"[E-ARCH] training complete -> {out_dir} (lora/ + projector.pt)")


if __name__ == "__main__":
    main()
