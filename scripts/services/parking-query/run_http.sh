#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../_common.sh"

setup_service_env "services/parking-query-service/src" "parking_query_service.settings"

exec "${GUNICORN_BIN:-gunicorn}" \
  "parking_query_service.http_runtime.wsgi:application" \
  --bind "${HTTP_HOST:-0.0.0.0}:${HTTP_PORT:-8000}" \
  --workers "${HTTP_WORKERS:-1}"
