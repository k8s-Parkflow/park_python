#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../_common.sh"

setup_service_env "services/vehicle-service/src" "vehicle_service.settings"
setup_mariadb_env "VEHICLE" "autoe_vehicle"

exec "${PYTHON_BIN:-python}" -m vehicle_service.grpc_runtime
