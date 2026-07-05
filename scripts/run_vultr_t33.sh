#!/usr/bin/env bash
# T3.3 (calibration) on the 4 Chinese-lab Vultr models.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a
mkdir -p logs/vultr

run () {
  local tag="$1" key="$2" model="$3" out="$4"
  echo "[$(date -Iseconds)] start $tag T3.3"
  OPENAI_API_KEY="$key" python scripts/run_pilot.py \
    --backend openai --base-url "$VULTR_BASE_URL" \
    --model "$model" --agent-id-override "vultr/$tag" \
    --capability T3.3 --setting no_injection,with_injection \
    --count 30 --output-dir "$out" --log-every 10 \
    >> "logs/vultr/${tag}-t33.log" 2>&1
  echo "[$(date -Iseconds)] done $tag T3.3 exit=$?"
}

run glm-5.2-fp8   "$VULTR_KEY_1" "zai-org/GLM-5.2-FP8"    "vultr-results/glm-5.2-fp8"   &
run minimax-m2.7  "$VULTR_KEY_2" "MiniMaxAI/MiniMax-M2.7" "vultr-results/minimax-m2.7"  &
run kimi-k2.6     "$VULTR_KEY_3" "moonshotai/Kimi-K2.6"   "vultr-results/kimi-k2.6"     &
run qwen3.6-27b   "$VULTR_KEY_4" "Qwen/Qwen3.6-27B"       "vultr-results/qwen3.6-27b"   &
wait
echo "[$(date -Iseconds)] all four T3.3 done"
