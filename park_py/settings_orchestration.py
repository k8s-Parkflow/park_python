from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
ORCHESTRATION_SERVICE_SRC = BASE_DIR / "services" / "orchestration-service" / "src"

if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))

from orchestration_service.settings import *  # noqa: F403
