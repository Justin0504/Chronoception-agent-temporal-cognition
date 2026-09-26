#!/usr/bin/env bash
# Fetch the METR HCAST corpus the P12 analysis runs on.
#
# The paper uses METR's time-horizon-1-1 release unchanged. That specific
# release matters: it has 24,008 raw rows which filter to the 14,709 HCAST
# runs the paper reports. The time-horizon-1-0 release filters to 22,223 and
# will not reproduce our numbers.
#
# The file is ~15 MB and is gitignored; this script is how you get it back.
set -euo pipefail
DEST="${1:-data/metr/runs.jsonl}"
URL="https://raw.githubusercontent.com/METR/eval-analysis-public/main/reports/time-horizon-1-1/data/raw/runs.jsonl"
mkdir -p "$(dirname "$DEST")"
echo "fetching $URL"
curl -sSL -o "$DEST" "$URL"
n=$(wc -l < "$DEST" | tr -d ' ')
echo "wrote $DEST ($n rows; expected 24008)"
[ "$n" = "24008" ] || { echo "WARNING: row count differs from the release the paper used"; exit 1; }
