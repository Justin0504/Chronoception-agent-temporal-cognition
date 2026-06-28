#!/usr/bin/env bash
# Route B-1 (OpenAI half): o3 + o4-mini fill on T1.1 + T2.3 + T3.1.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a
mkdir -p logs/route_b1

run () {
  local tag="$1"; shift
  echo "[$(date -Iseconds)] start $tag"
  python scripts/run_pilot.py "$@" >> "logs/route_b1/${tag}.log" 2>&1
  echo "[$(date -Iseconds)] done  $tag exit=$?"
}

run o3 \
  --backend openai --model o3 \
  --capability T1.1,T2.3,T3.1 \
  --setting no_injection,with_injection \
  --count 30 --output-dir e1-results/o3/

run o4-mini \
  --backend openai --model o4-mini \
  --capability T1.1,T2.3,T3.1 \
  --setting no_injection,with_injection \
  --count 30 --output-dir e1-results/o4-mini/

echo "[$(date -Iseconds)] OpenAI half complete"
