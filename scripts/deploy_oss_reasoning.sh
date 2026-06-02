#!/bin/bash
# Deploy DeepSeek-R1-Distill-Qwen-32B on Yue Zhao server (or any 8xRTX 6000 Ada).
#
# Run this from a machine that can ssh into haiyuez@10.136.20.188.
# All commands are idempotent: re-running won't break anything.
#
# Usage:
#   ./scripts/deploy_oss_reasoning.sh
#
# After this script completes, the model is served on the lab server at
# 127.0.0.1:8001 (vLLM, OpenAI-compatible). Port-forward and run E5:
#
#   ssh -L 8001:127.0.0.1:8001 haiyuez@10.136.20.188
#   ./scripts/run_e5_oss_reverse_scaling.sh
#
set -euo pipefail

LAB_HOST="haiyuez@10.136.20.188"
MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
PORT=8001
CONDA_ENV="/data/haiyuez/conda/envs/chronoception"

ssh -o StrictHostKeyChecking=accept-new "$LAB_HOST" bash <<EOF
set -euo pipefail
source $CONDA_ENV/bin/activate

# Persistent download path
export HF_HOME=/data/haiyuez/.hf
export TRANSFORMERS_OFFLINE=0
mkdir -p \$HF_HOME

# nvjitlink LD_LIBRARY_PATH fix (was needed for vLLM 0.6.4 + cusparse mismatch)
export LD_LIBRARY_PATH=$CONDA_ENV/lib/python3.11/site-packages/nvidia/nvjitlink/lib:\${LD_LIBRARY_PATH:-}

# Kill any running vLLM
if pgrep -f "vllm.*serve.*$PORT" >/dev/null; then
    echo "[deploy] killing existing vLLM on port $PORT"
    pkill -f "vllm.*serve.*$PORT" || true
    sleep 5
fi

# Launch vLLM in background with logs persisted
LOG=/data/haiyuez/chronoception-oss-deploy.log
nohup vllm serve "$MODEL" \\
    --host 127.0.0.1 \\
    --port $PORT \\
    --tensor-parallel-size 4 \\
    --max-model-len 32768 \\
    --gpu-memory-utilization 0.85 \\
    --dtype bfloat16 \\
    > \$LOG 2>&1 &

DEPLOY_PID=\$!
echo "[deploy] vLLM PID \$DEPLOY_PID, log: \$LOG"

# Wait for health endpoint to come up (up to 5 min)
for i in {1..60}; do
    sleep 5
    if curl -fsS http://127.0.0.1:$PORT/v1/models >/dev/null 2>&1; then
        echo "[deploy] OK, model serving on port $PORT after \$((i*5))s"
        curl -sS http://127.0.0.1:$PORT/v1/models | head -c 200
        echo
        exit 0
    fi
    echo "[deploy] still waiting (\$((i*5))s elapsed)..."
done

echo "[deploy] TIMEOUT after 5 minutes"
tail -50 \$LOG
exit 1
EOF
