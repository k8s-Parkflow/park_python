from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
VEHICLE_SERVICE_SRC = BASE_DIR / "services" / "vehicle-service" / "src"

if str(VEHICLE_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(VEHICLE_SERVICE_SRC))

from vehicle_service.settings import *  # noqa: F403
