#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../_common.sh"

setup_service_env "services/zone-service/src" "zone_service.settings"
setup_mariadb_env "ZONE" "autoe_zone"

exec "${GUNICORN_BIN:-gunicorn}" \
  "zone_service.http_runtime.wsgi:application" \
  --bind "${HTTP_HOST:-0.0.0.0}:${HTTP_PORT:-8000}" \
  --workers "${HTTP_WORKERS:-1}"
