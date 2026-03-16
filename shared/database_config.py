from __future__ import annotations

import os
from pathlib import Path


MARIADB_ENGINE = "django.db.backends.mysql"
MARIADB_CHARSET = "utf8mb4"
DEFAULT_DB_HOST = "127.0.0.1"
DEFAULT_DB_PORT = "3306"
DEFAULT_DB_USER = "root"
DEFAULT_DB_PASSWORD = ""
DEFAULT_CONN_MAX_AGE = 60

SERVICE_DB_DEFAULT_NAMES = {
    "default": "autoe_orchestration",
    "vehicle": "autoe_vehicle",
    "zone": "autoe_zone",
    "parking_command": "autoe_parking_command",
    "parking_query": "autoe_parking_query",
}

SERVICE_DB_ENV_PREFIXES = {
    "default": "ORCHESTRATION",
    "vehicle": "VEHICLE",
    "zone": "ZONE",
    "parking_command": "PARKING_COMMAND",
    "parking_query": "PARKING_QUERY",
}

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


def build_mariadb_database(
    *,
    name: str,
    host: str = DEFAULT_DB_HOST,
    port: str = DEFAULT_DB_PORT,
    user: str = DEFAULT_DB_USER,
    password: str = DEFAULT_DB_PASSWORD,
    conn_max_age: int = DEFAULT_CONN_MAX_AGE,
) -> dict:
    return {
        "ENGINE": MARIADB_ENGINE,
        "NAME": name,
        "HOST": host,
        "PORT": str(port),
        "USER": user,
        "PASSWORD": password,
        "CONN_MAX_AGE": conn_max_age,
        "OPTIONS": {
            "charset": MARIADB_CHARSET,
        },
    }


def build_service_mariadb_databases() -> dict[str, dict]:
    databases: dict[str, dict] = {}
    for alias, default_name in SERVICE_DB_DEFAULT_NAMES.items():
        env_prefix = SERVICE_DB_ENV_PREFIXES[alias]
        databases[alias] = build_mariadb_database(
            name=os.getenv(f"{env_prefix}_DB_NAME", default_name),
            host=os.getenv(f"{env_prefix}_DB_HOST", DEFAULT_DB_HOST),
            port=os.getenv(f"{env_prefix}_DB_PORT", DEFAULT_DB_PORT),
            user=os.getenv(f"{env_prefix}_DB_USER", DEFAULT_DB_USER),
            password=os.getenv(f"{env_prefix}_DB_PASSWORD", DEFAULT_DB_PASSWORD),
        )
    return databases


def build_service_databases(*, base_dir: Path) -> dict[str, dict]:
    databases: dict[str, dict] = {}
    for alias, filename in SERVICE_DB_FILENAMES.items():
        env_key = SERVICE_DB_ENV_KEYS[alias]
        default_name = str(base_dir / filename)
        databases[alias] = build_sqlite_database(
            name=os.getenv(env_key, default_name),
        )
    return databases
