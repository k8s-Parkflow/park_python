#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ARTIFACT_DIR="reports/coverage/entities"
mkdir -p "$ARTIFACT_DIR"

PYTHON_BIN="./.venv/bin/python"
RCFILE="reports/coverage/.coveragerc"

"$PYTHON_BIN" -m coverage erase
"$PYTHON_BIN" -m coverage run --rcfile="$RCFILE" manage.py test --settings=park_py.settings_test "$@"
"$PYTHON_BIN" -m coverage report -m --rcfile="$RCFILE" > "$ARTIFACT_DIR/entity_coverage_report.txt"
"$PYTHON_BIN" -m coverage xml --rcfile="$RCFILE"
"$PYTHON_BIN" -m coverage json --rcfile="$RCFILE"

echo "Coverage artifacts generated in: $ARTIFACT_DIR"
