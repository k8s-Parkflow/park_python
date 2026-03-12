from __future__ import annotations

import os
from pathlib import Path


SERVICE_DB_FILENAMES = {
    "default": "orchestration.sqlite3",
    "vehicle": "vehicle.sqlite3",
    "zone": "zone.sqlite3",
    "parking_command": "parking_command.sqlite3",
    "parking_query": "parking_query.sqlite3",
}

SERVICE_DB_ENV_KEYS = {
    "default": "ORCHESTRATION_DB_NAME",
    "vehicle": "VEHICLE_DB_NAME",
    "zone": "ZONE_DB_NAME",
    "parking_command": "PARKING_COMMAND_DB_NAME",
    "parking_query": "PARKING_QUERY_DB_NAME",
}


def build_sqlite_database(*, name: str) -> dict:
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": name,
    }


def build_service_databases(*, base_dir: Path) -> dict[str, dict]:
    databases: dict[str, dict] = {}
    for alias, filename in SERVICE_DB_FILENAMES.items():
        env_key = SERVICE_DB_ENV_KEYS[alias]
        default_name = str(base_dir / filename)
        databases[alias] = build_sqlite_database(
            name=os.getenv(env_key, default_name),
        )
    return databases
