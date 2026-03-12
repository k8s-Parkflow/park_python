#!/usr/bin/env python
from __future__ import annotations

import os
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.runtime_paths import bootstrap_service_runtime


DEFAULT_SETTINGS_MODULE = "vehicle_service.settings"


def main() -> None:
    bootstrap_service_runtime(__file__)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
