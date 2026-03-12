#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ARTIFACT_DIR="reports/coverage/zone_slot"
mkdir -p "$ARTIFACT_DIR/htmlcov"

PYTHON_BIN="./.venv-cpython39/bin/python"
RCFILE="reports/coverage/.coveragerc.project"
INCLUDE_FILES="services/parking-query-service/src/parking_query_service/views.py,services/parking-query-service/src/parking_query_service/dependencies.py,services/parking-query-service/src/parking_query_service/services/zone_slot_query_service.py,services/parking-query-service/src/parking_query_service/repositories/zone_slot_repository.py,park_py/openapi.py"

"$PYTHON_BIN" -m coverage erase --rcfile="$RCFILE"
"$PYTHON_BIN" -m coverage run --rcfile="$RCFILE" manage.py test acceptance contract unit repository park_py.tests.test_swagger park_py.test_openapi --settings=park_py.settings_test
"$PYTHON_BIN" -m coverage report -m --rcfile="$RCFILE" --include="$INCLUDE_FILES" > "$ARTIFACT_DIR/coverage_report.txt"
"$PYTHON_BIN" -m coverage xml --rcfile="$RCFILE" --include="$INCLUDE_FILES" -o "$ARTIFACT_DIR/coverage.xml"
"$PYTHON_BIN" -m coverage json --rcfile="$RCFILE" --include="$INCLUDE_FILES" -o "$ARTIFACT_DIR/coverage.json"
"$PYTHON_BIN" -m coverage html --rcfile="$RCFILE" --include="$INCLUDE_FILES" -d "$ARTIFACT_DIR/htmlcov"
"$PYTHON_BIN" scripts/postprocess_coverage_html.py "$ARTIFACT_DIR/htmlcov"

echo "Zone slot coverage artifacts generated in: $ARTIFACT_DIR"
