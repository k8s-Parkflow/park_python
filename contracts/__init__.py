"""Shared service contract package."""
from __future__ import annotations

import sys
from pathlib import Path


GENERATED_PYTHON_ROOT = Path(__file__).resolve().parent / "gen" / "python"

if str(GENERATED_PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(GENERATED_PYTHON_ROOT))
