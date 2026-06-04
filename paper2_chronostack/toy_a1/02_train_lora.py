#!/usr/bin/env python3
"""A.1 LoRA fine-tune — install wall-clock-grounded self-duration narration.

Take Qwen2.5-1.5B-Instruct and LoRA fine-tune on (prompt, response +
self-duration annotation) pairs. The loss is standard token-level CE,
but the training data carries wall-clock signal in the targets, so the
loss support effectively includes wall-clock duration. This is the toy
construction of a CIT-exiting training procedure.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, TrainingArguments,
)
from trl import SFTTrainer, SFTConfig


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    p.add_argument("--data-dir", default="/data/haiyuez/chronoception-a1/data")
    p.add_argument("--out-dir", default="/data/haiyuez/chronoception-a1/lora")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--grad-accum", type=int, default=4)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--lora-rank", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument("--max-len", type=int, default=1024)
    return p.parse_args()


def load_jsonl(path: Path) -> Dataset:
    rows = []
    with path.open() as f:
        for line in f:
            r = json.loads(line)
            rows.append(r)
    return Dataset.from_list(rows)


def format_sft(example, tokenizer):
    messages = [
        {"role": "user", "content": example["prompt"]},
        {"role": "assistant", "content": example["target"]},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": text}


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[A.1] loading tokenizer + model: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, device_map="cuda:0",
        trust_remote_code=True,
    )

    lora_cfg = LoraConfig(
        r=args.lora_rank, lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    print("[A.1] loading data...")
    train_ds = load_jsonl(data_dir / "train.jsonl")
    eval_ds = load_jsonl(data_dir / "eval.jsonl")
    train_ds = train_ds.map(lambda x: format_sft(x, tokenizer))
    eval_ds = eval_ds.map(lambda x: format_sft(x, tokenizer))

    sft_cfg = SFTConfig(
        output_dir=str(out_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        max_seq_length=args.max_len,
        bf16=True,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        report_to="none",
        dataset_text_field="text",
        packing=False,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        args=sft_cfg,
        processing_class=tokenizer,
    )

    print("[A.1] starting training...")
    trainer.train()
    trainer.save_model(str(out_dir / "final"))
    print(f"[A.1] training complete. LoRA saved to {out_dir / 'final'}")


if __name__ == "__main__":
    main()
