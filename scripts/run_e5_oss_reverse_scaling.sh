#!/bin/bash
# E5: OSS Reverse-Scaling validation on DeepSeek-R1-Distill-Qwen-32B.
#
# Assumes vLLM is serving the model on localhost:8001 (via deploy_oss_reasoning.sh
# + SSH port-forward).
#
# Runs T3.1 at three max_completion_tokens budgets (proxy for "reasoning effort"
# in a self-hosted reasoning model with no native effort knob). The token budget
# directly controls reasoning compute spent.
#
# Output: e5-results/deepseek-r1-32b-{low,med,high}/
# After completion, the analyzer is identical to E2:
#   python scripts/compute_metrics.py --input-dir e5-results
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

run_level() {
    local LEVEL="$1"
    local BUDGET="$2"
    mkdir -p logs/e5 e5-results/deepseek-r1-32b-$LEVEL
    echo "[$(date -Iseconds)] starting OSS R1-Distill 32B level=$LEVEL budget=$BUDGET" \
        > logs/e5/oss-$LEVEL.log
    python3 scripts/run_pilot.py \
        --backend openai \
        --base-url http://127.0.0.1:8001/v1 \
        --model deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
        --capability T3.1 \
        --setting no_injection,with_injection \
        --count 30 \
        --output-dir "e5-results/deepseek-r1-32b-$LEVEL" \
        --force \
        --max-output-tokens "$BUDGET" \
        --agent-id-override "oss/deepseek-r1-32b-$LEVEL" \
        --timeout 600 \
        >> logs/e5/oss-$LEVEL.log 2>&1
    echo "[$(date -Iseconds)] done $LEVEL exit=$?" >> logs/e5/oss-$LEVEL.log
}

# Three budgets, monotone in reasoning compute. R1-Distill reasoning thinking
# happens inside the response — larger budget = more thinking allowed.
run_level low 2048 &
run_level med 8192 &
run_level high 24000 &
wait

echo "All E5 runs complete."
python3 scripts/compute_metrics.py --input-dir e5-results --output-csv e5-results/metrics.csv
