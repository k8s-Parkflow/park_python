#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../_common.sh"

setup_service_env "services/orchestration-service/src" "orchestration_service.settings"
setup_mariadb_env "ORCHESTRATION" "autoe_orchestration"

REPO_ROOT="$(service_repo_root)"

exec "${PYTHON_BIN:-python}" \
  "${REPO_ROOT}/services/orchestration-service/src/orchestration_service/manage.py" \
  migrate \
  "$@"
