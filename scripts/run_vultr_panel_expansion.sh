#!/usr/bin/env bash
# Extend the ChronoBench panel with 4 Chinese-lab models via Vultr Inference.
# Uses one API key per model so rate limits do not cross-block.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a
mkdir -p logs/vultr

# Model x key routing. Each job runs T1.1 + T2.3 + T3.1 x A/B x n=30.
run () {
  local tag="$1" key="$2" model="$3" out="$4"
  echo "[$(date -Iseconds)] start $tag"
  OPENAI_API_KEY="$key" python scripts/run_pilot.py \
    --backend openai \
    --base-url "$VULTR_BASE_URL" \
    --model "$model" \
    --agent-id-override "vultr/$tag" \
    --capability T1.1,T2.3,T3.1 \
    --setting no_injection,with_injection \
    --count 30 --output-dir "$out" \
    --log-every 10 \
    >> "logs/vultr/${tag}.log" 2>&1
  echo "[$(date -Iseconds)] done $tag exit=$?"
}

run deepseek-v4-flash "$VULTR_KEY_1" "deepseek-ai/DeepSeek-V4-Flash" "vultr-results/deepseek-v4-flash" &
PID_DS=$!
run glm-5.2-fp8     "$VULTR_KEY_2" "zai-org/GLM-5.2-FP8"           "vultr-results/glm-5.2-fp8" &
PID_GLM=$!
run kimi-k2.6       "$VULTR_KEY_3" "moonshotai/Kimi-K2.6"          "vultr-results/kimi-k2.6" &
PID_KIMI=$!
run minimax-m2.7    "$VULTR_KEY_4" "MiniMaxAI/MiniMax-M2.7"        "vultr-results/minimax-m2.7" &
PID_MM=$!

wait $PID_DS  || true
wait $PID_GLM || true
wait $PID_KIMI || true
wait $PID_MM  || true

echo "[$(date -Iseconds)] all four models done"
