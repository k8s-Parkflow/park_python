#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../_common.sh"

setup_service_env "services/parking-command-service/src" "parking_command_service.settings"

REPO_ROOT="$(service_repo_root)"

exec "${PYTHON_BIN:-python}" \
  "${REPO_ROOT}/services/parking-command-service/src/parking_command_service/manage.py" \
  migrate \
  "$@"
