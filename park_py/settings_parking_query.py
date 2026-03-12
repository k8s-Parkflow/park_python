from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
PARKING_QUERY_SERVICE_SRC = BASE_DIR / "services" / "parking-query-service" / "src"

if str(PARKING_QUERY_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(PARKING_QUERY_SERVICE_SRC))

from parking_query_service.settings import *  # noqa: F403
