#!/usr/bin/env bash
# Route B-1 (Anthropic half only): Sonnet 4.6 + extended thinking on 8 missing caps
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a
mkdir -p logs/route_b1

echo "[$(date -Iseconds)] start sonnet-thinking 8-cap fill"
python scripts/run_pilot.py \
  --backend anthropic --model claude-sonnet-4-6 \
  --capability T1.1,T1.2,T1.3,T2.1,T2.2,T2.3,T3.2,T3.3 \
  --setting no_injection,with_injection \
  --count 30 --output-dir e3-results/claude-sonnet-4-6-thinking/ \
  --temperature 1.0 --max-output-tokens 8192 \
  --extra-body '{"thinking":{"type":"enabled","budget_tokens":4096}}' \
  >> logs/route_b1/sonnet-thinking.log 2>&1
echo "[$(date -Iseconds)] done sonnet-thinking exit=$?"
