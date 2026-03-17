#!/usr/bin/env bash

set -euo pipefail

service_repo_root() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "${script_dir}/../.." >/dev/null 2>&1
  pwd
}

setup_service_env() {
  local service_src="$1"
  local settings_module="$2"
  local repo_root

  repo_root="$(service_repo_root)"

  export PYTHONPATH="${repo_root}:${repo_root}/${service_src}${PYTHONPATH:+:${PYTHONPATH}}"
  export DJANGO_SETTINGS_MODULE="${settings_module}"
}

export_default_env() {
  local env_key="$1"
  local default_value="$2"

  if [[ -z "${!env_key:-}" ]]; then
    export "${env_key}=${default_value}"
  fi
}

require_env() {
  local env_key="$1"

  if [[ -z "${!env_key:-}" ]]; then
    echo "Missing required environment variable: ${env_key}" >&2
    return 1
  fi
}

setup_mariadb_env() {
  local env_prefix="$1"
  local default_name="$2"

  export_default_env "${env_prefix}_DB_NAME" "${default_name}"
  export_default_env "${env_prefix}_DB_HOST" "127.0.0.1"
  export_default_env "${env_prefix}_DB_PORT" "3306"
  require_env "${env_prefix}_DB_USER"
  require_env "${env_prefix}_DB_PASSWORD"
}
