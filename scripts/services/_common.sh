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
