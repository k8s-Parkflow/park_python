from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
ZONE_SERVICE_SRC = BASE_DIR / "services" / "zone-service" / "src"

if str(ZONE_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ZONE_SERVICE_SRC))

from zone_service.settings import *  # noqa: F403
