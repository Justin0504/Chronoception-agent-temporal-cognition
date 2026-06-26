#!/usr/bin/env bash
# Route B-1: fill reasoning-model cells missing from the panel
# (o3, o4-mini: T1.1 + T2.3 + T3.1; Sonnet-thinking: every cap except T3.1)
#
# Launches three nohup-friendly jobs in series per family so a single
# rate-limit hiccup does not cascade.
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

# 1. o3 — T1.1, T2.3, T3.1  (no + with)
run o3 \
  --backend openai --model o3 \
  --capability T1.1,T2.3,T3.1 \
  --setting no_injection,with_injection \
  --count 30 --output-dir e1-results/o3/

# 2. o4-mini — T1.1, T2.3, T3.1  (no + with)
run o4-mini \
  --backend openai --model o4-mini \
  --capability T1.1,T2.3,T3.1 \
  --setting no_injection,with_injection \
  --count 30 --output-dir e1-results/o4-mini/

# 3. Sonnet 4.6 + extended thinking — every cap except T3.1
run sonnet-thinking \
  --backend anthropic --model claude-sonnet-4-6 \
  --capability T1.1,T1.2,T1.3,T2.1,T2.2,T2.3,T3.2,T3.3 \
  --setting no_injection,with_injection \
  --count 30 --output-dir e3-results/claude-sonnet-4-6-thinking/ \
  --extra-body '{"thinking":{"type":"enabled","budget_tokens":4096}}'

echo "[$(date -Iseconds)] route_b1 complete"
