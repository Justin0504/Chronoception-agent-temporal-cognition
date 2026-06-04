# A.1 — Toy Positive Control

**Goal**: Existence proof that crossing $\varepsilon^*$ on T3.1 is achievable by adding wall-clock signal to the training loss. Validates CIT's positive prediction: chronoception *can* be installed when the loss support includes wall-clock.

## Design

1. **Base model**: Qwen2.5-1.5B-Instruct (small, fast to fine-tune on a single 48GB GPU).
2. **Data generation** (`01_generate_sft.py`):
   - Use T3.1 task generator (paper §6.1) to get prompts.
   - For each prompt, run the base model and measure $\tau_{\text{wall}}$.
   - Construct SFT pair: `(prompt, base_response + "\n\nThis task took {tau_wall:.1f} seconds.")`.
   - Add Gaussian noise on the duration (±20%) to mimic real human duration estimates.
   - Generate ~500 train pairs + 100 eval pairs (different sub-task seeds).
3. **LoRA fine-tune** (`02_train_lora.py`):
   - Rank 16, alpha 32, dropout 0.05.
   - 3 epochs, batch size 4, gradient accumulation 4 (effective 16).
   - AdamW, lr 2e-4, cosine schedule, 5% warmup.
   - Train on `attn.q_proj`, `attn.k_proj`, `attn.v_proj`, `attn.o_proj`, `mlp.gate_proj`, `mlp.up_proj`, `mlp.down_proj`.
4. **Evaluation** (`03_eval.py`):
   - Load fine-tuned model.
   - Run 100 held-out T3.1 instances.
   - Parse $\tau_{\text{self}}$, compute $\rho = \log_{10}(\tau_{\text{self}}/\tau_{\text{wall}})$.
   - Compare baseline vs fine-tuned median $|\rho|$.

## Expected result

| | Median $|\rho|$ | T3.1 axis score |
|---|---|---|
| Baseline Qwen2.5-1.5B | ~1.5 (Qwen2.5-7B was 1.56) | 0.78 |
| LoRA fine-tuned | **< 0.3** (target: crossable) | < 0.15 |

If achieved, this is the first positive control demonstrating CIT's converse: wall-clock-supported training **can** install chronoception. Even partial closure (e.g., $|\rho|$ from 1.5 to 0.5) establishes the existence direction; full crossing of $\varepsilon^* = 0.20$ on T3.1 alone strengthens the claim.

## Why this is sufficient for Paper 1

- Paper 1 proves CIT (negative result: token-only loss cannot install chronoception).
- A.1 demonstrates the converse (positive: wall-clock-supported loss can install partial chronoception).
- Together: the framework's central claim has both halves of its existence/non-existence proof.

A *full* installation that closes $\varepsilon$ across all 9 sub-capabilities is the program of Paper 2 (\textsc{ChronoStack}). A.1 is the existence proof on a single sub-capability (T3.1) with a single intervention (LoRA SFT with self-duration annotation).

## Server setup

```bash
ssh haiyuez@10.136.20.188
source /data/haiyuez/a1venv/bin/activate
cd /data/haiyuez/chronoception-a1  # uploaded scripts
python3 01_generate_sft.py
python3 02_train_lora.py
python3 03_eval.py
```

Training fits on one RTX 6000 Ada (48GB) in bf16 + LoRA. Expected wall-clock: ~2 hours for training + 30 min for eval.
