#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MVP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SQL_FILE="$SCRIPT_DIR/validation_loop_smoke_test.sql"

if [ ! -f "$SQL_FILE" ]; then
  echo "Smoke-test SQL not found: $SQL_FILE"
  exit 1
fi

cd "$MVP_DIR"

docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map < "$SQL_FILE"
