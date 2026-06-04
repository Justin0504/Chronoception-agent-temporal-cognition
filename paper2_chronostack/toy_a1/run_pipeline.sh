#!/bin/bash
# A.1 pipeline orchestrator: generate → train → eval.
# Designed to run on the Yue Zhao lab server in the dedicated a1venv.
set -euo pipefail
cd /data/haiyuez/chronoception-a1
source /data/haiyuez/a1venv/bin/activate

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-2}"
LOG=run_pipeline.log

echo "[$(date -Iseconds)] A.1 pipeline starting on CUDA=$CUDA_VISIBLE_DEVICES" | tee -a $LOG

# Stage 1: data generation (skip if train.jsonl already at target size)
if [ ! -f data/train.jsonl ] || [ "$(wc -l < data/train.jsonl)" -lt 500 ]; then
    echo "[$(date -Iseconds)] STAGE 1: data generation" | tee -a $LOG
    python3 -u 01_generate_sft.py --n-train 500 --n-eval 100 2>&1 | tee -a $LOG
else
    echo "[$(date -Iseconds)] STAGE 1: skipped (data already present)" | tee -a $LOG
fi

# Stage 2: LoRA training
echo "[$(date -Iseconds)] STAGE 2: LoRA training" | tee -a $LOG
python3 -u 02_train_lora.py 2>&1 | tee -a $LOG

# Stage 3: evaluation
echo "[$(date -Iseconds)] STAGE 3: evaluation" | tee -a $LOG
python3 -u 03_eval.py --n 30 2>&1 | tee -a $LOG

echo "[$(date -Iseconds)] A.1 pipeline COMPLETE" | tee -a $LOG
