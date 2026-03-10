from __future__ import annotations


SERVICE_TO_DB_ALIAS = {
    "orchestration": "default",
    "vehicle": "vehicle",
    "zone": "zone",
    "parking_command": "parking_command",
    "parking_query": "parking_query",
}

SERVICE_MIGRATION_ORDER = (
    "orchestration",
    "vehicle",
    "zone",
    "parking_command",
    "parking_query",
)
