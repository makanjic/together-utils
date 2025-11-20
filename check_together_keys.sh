#!/usr/bin/env bash
#
# Usage:
#   ./check_together_keys.sh input_keys.txt output_keys.txt model_name
#
# Example:
#   ./check_together_keys.sh keys.txt valid.txt meta-llama/Llama-3.1-8B-Instruct-Turbo
#

set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 INPUT_FILE OUTPUT_FILE MODEL_NAME" >&2
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"
MODEL_NAME="$3"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/simple_openai_check.py"

if [ ! -f "$PY_SCRIPT" ]; then
  echo "ERROR: Cannot find $PY_SCRIPT" >&2
  exit 1
fi

# Clear output file
: > "$OUTPUT_FILE"

export OPENAI_BASE_URL="https://api.together.xyz/v1"
export OPENAI_MODEL="$MODEL_NAME"

while IFS= read -r line || [ -n "$line" ]; do
  key="$(echo "$line" | tr -d '[:space:]')"

  if [[ -z "$key" || "$key" == \#* ]]; then
    continue
  fi

  short="${key:0:8}..."

  echo "[CHECK] Testing $short with model: $MODEL_NAME" >&2

  if OPENAI_API_KEY="$key" python "$PY_SCRIPT" >/dev/null 2>&1; then
    echo "[OK] $short usable" >&2
    echo "$key" >> "$OUTPUT_FILE"
  else
    echo "[BAD] $short not usable" >&2
  fi

done < "$INPUT_FILE"
echo "Done. Valid keys saved to: $OUTPUT_FILE" >&2
