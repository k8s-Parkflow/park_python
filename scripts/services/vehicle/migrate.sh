#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../_common.sh"

setup_service_env "services/vehicle-service/src" "vehicle_service.settings"

REPO_ROOT="$(service_repo_root)"

exec "${PYTHON_BIN:-python}" \
  "${REPO_ROOT}/services/vehicle-service/src/vehicle_service/manage.py" \
  migrate \
  "$@"
