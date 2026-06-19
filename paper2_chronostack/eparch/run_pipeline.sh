#!/bin/bash
# E-ARCH pipeline: generate -> train -> extrapolation eval.
# Runs on the Yue Zhao lab server in the A.1 a1venv (transformers 4.46, peft, trl).
set -euo pipefail
cd "$(dirname "$0")"
source /data/haiyuez/a1venv/bin/activate

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-2}"
DATA=/data/haiyuez/chronoception-eparch/data
OUT=/data/haiyuez/chronoception-eparch/out
LOG=run_pipeline.log

echo "[$(date -Iseconds)] E-ARCH pipeline on CUDA=$CUDA_VISIBLE_DEVICES" | tee -a "$LOG"

# Stage 0: validate the time-token mechanism on CPU before spending GPU time.
python3 -c "from chronoception.stack.time_token import smoke_test; smoke_test()" 2>&1 | tee -a "$LOG"

# Stage 1: data
if [ ! -f "$DATA/train.jsonl" ] || [ "$(wc -l < "$DATA/train.jsonl")" -lt 500 ]; then
    echo "[$(date -Iseconds)] STAGE 1: data generation" | tee -a "$LOG"
    python3 -u 01_generate_data.py --n-train 500 --n-eval 100 --out-dir "$DATA" 2>&1 | tee -a "$LOG"
else
    echo "[$(date -Iseconds)] STAGE 1: skipped (data present)" | tee -a "$LOG"
fi

# Stage 2: train (LoRA + time-token projector)
echo "[$(date -Iseconds)] STAGE 2: training" | tee -a "$LOG"
python3 -u 02_train.py --data-dir "$DATA" --out-dir "$OUT" 2>&1 | tee -a "$LOG"

# Stage 3: extrapolation eval
echo "[$(date -Iseconds)] STAGE 3: extrapolation eval" | tee -a "$LOG"
python3 -u 03_eval.py --out-dir "$OUT" 2>&1 | tee -a "$LOG"

echo "[$(date -Iseconds)] E-ARCH pipeline COMPLETE" | tee -a "$LOG"
