#!/usr/bin/env bash
# One-shot vLLM startup on Yue Zhao lab server (phe108-yuezhao-01).
# Captures everything we learned in the 2026-05-31 setup. Idempotent.
#
# Usage (on the server, after SSH'ing in):
#   bash scripts/server_setup_yuezhao.sh start <model_id> <served_name> [<gpu>]
#   bash scripts/server_setup_yuezhao.sh stop
#
# Examples:
#   bash scripts/server_setup_yuezhao.sh start Qwen/Qwen2.5-7B-Instruct qwen2.5-7b 0
#   bash scripts/server_setup_yuezhao.sh start Qwen/QwQ-32B-Preview qwq-32b 0,1

set -euo pipefail

ENV_PATH="/data/haiyuez/conda/envs/chronoception"
HF_CACHE="/data/haiyuez/hf_cache"
NVJITLINK_LIB="${ENV_PATH}/lib/python3.11/site-packages/nvidia/nvjitlink/lib"
PORT="${PORT:-8000}"

cmd="${1:-help}"

case "$cmd" in
  start)
    MODEL_ID="$2"
    SERVED_NAME="$3"
    GPUS="${4:-0}"

    # Kill any previous session for this model
    tmux kill-session -t "vllm-${SERVED_NAME}" 2>/dev/null || true

    NUM_GPUS=$(echo "$GPUS" | tr ',' '\n' | wc -l)
    TP_FLAG=""
    if [ "$NUM_GPUS" -gt 1 ]; then
      TP_FLAG="--tensor-parallel-size $NUM_GPUS"
    fi

    tmux new-session -d -s "vllm-${SERVED_NAME}" "
      export LD_LIBRARY_PATH=${NVJITLINK_LIB}:\$LD_LIBRARY_PATH
      export HF_HOME=${HF_CACHE}
      export CUDA_VISIBLE_DEVICES=${GPUS}
      ${ENV_PATH}/bin/vllm serve ${MODEL_ID} \
          --host 0.0.0.0 --port ${PORT} \
          --max-model-len 4096 \
          --gpu-memory-utilization 0.85 \
          --served-model-name ${SERVED_NAME} \
          ${TP_FLAG} \
          2>&1 | tee /tmp/vllm-${SERVED_NAME}.log
      sleep 600
    "

    echo "Started vllm-${SERVED_NAME} in tmux. Tail log with:"
    echo "  tail -f /tmp/vllm-${SERVED_NAME}.log"
    echo "Endpoint will be: http://localhost:${PORT}/v1"
    ;;

  stop)
    for s in $(tmux ls 2>/dev/null | awk -F: '/^vllm-/{print $1}'); do
      tmux kill-session -t "$s"
      echo "Killed: $s"
    done
    ;;

  *)
    echo "Usage: $0 start <model_id> <served_name> [<gpu_csv>]"
    echo "       $0 stop"
    echo "Examples:"
    echo "  $0 start Qwen/Qwen2.5-7B-Instruct qwen2.5-7b 0"
    echo "  $0 start meta-llama/Llama-3.3-70B-Instruct llama-3.3-70b 0,1"
    ;;
esac
