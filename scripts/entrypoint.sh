#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

LOG_DIR="$SCRIPT_DIR/../logs"
LOG_FILE="$LOG_DIR/pipeline.log"

mkdir -p "$LOG_DIR"

# overwrite old log
> "$LOG_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting Pipeline" \
| tee -a "$LOG_FILE"

uv run python -u -m scripts.main 2>&1 \
| tee -a "$LOG_FILE" \
| grep --line-buffered "^\[INFO\]"

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Pipeline completed successfully" \
    | tee -a "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Pipeline failed" \
    | tee -a "$LOG_FILE"
fi