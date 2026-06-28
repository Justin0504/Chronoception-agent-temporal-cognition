#!/usr/bin/env bash
# Route B-1 (Anthropic remainder): finish Sonnet-thinking on
# T2.3 (both settings — no_injection had 22/30 done, will skip them),
# T3.2 (both), T3.3 (both). Idempotent: existing JSON files are skipped.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a
mkdir -p logs/route_b1

echo "[$(date -Iseconds)] start sonnet-thinking remainder"
python scripts/run_pilot.py \
  --backend anthropic --model claude-sonnet-4-6 \
  --capability T2.3,T3.2,T3.3 \
  --setting no_injection,with_injection \
  --count 30 --output-dir e3-results/claude-sonnet-4-6-thinking/ \
  --temperature 1.0 --max-output-tokens 8192 \
  --extra-body '{"thinking":{"type":"enabled","budget_tokens":4096}}' \
  >> logs/route_b1/sonnet-thinking-remainder.log 2>&1
echo "[$(date -Iseconds)] done sonnet-thinking remainder exit=$?"
