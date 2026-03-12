from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
PARKING_COMMAND_SERVICE_SRC = BASE_DIR / "services" / "parking-command-service" / "src"

if str(PARKING_COMMAND_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(PARKING_COMMAND_SERVICE_SRC))

from parking_command_service.settings import *  # noqa: F403
