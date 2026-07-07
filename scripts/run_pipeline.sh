#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

LOG_DIR="$SCRIPT_DIR/../logs"
LOG_FILE="$LOG_DIR/pipeline.log"

mkdir -p "$LOG_DIR"

# overwrite old log
> "$LOG_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting Pipeline" \
| tee -a "$LOG_FILE"

# Make sure the container works properly
if ! docker compose ps --services --status running | grep -q "^nyc-warehouse$"; then
    echo "ERROR: nyc-warehouse container is not running." \
    | tee -a "$LOG_FILE"
    echo "Run: docker compose up -d" \
    | tee -a "$LOG_FILE"
    exit 1
fi

# Execute the pipeline inside Docker container
docker compose exec -T nyc-warehouse \
    uv run python -u -m scripts.main 2>&1 \
| tee -a "$LOG_FILE" \
| grep --line-buffered "^\[INFO\]"

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Pipeline completed successfully" \
    | tee -a "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Pipeline failed" \
    | tee -a "$LOG_FILE"
    exit 1
fi