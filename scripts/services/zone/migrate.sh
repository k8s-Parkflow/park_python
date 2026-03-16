#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../_common.sh"

setup_service_env "services/zone-service/src" "zone_service.settings"
setup_mariadb_env "ZONE" "autoe_zone"

REPO_ROOT="$(service_repo_root)"

exec "${PYTHON_BIN:-python}" \
  "${REPO_ROOT}/services/zone-service/src/zone_service/manage.py" \
  migrate \
  "$@"
