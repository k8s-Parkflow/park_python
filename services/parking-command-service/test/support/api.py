from __future__ import annotations

import json
from datetime import datetime

from django.test import Client
from django.http import HttpResponse


# 입차 API 호출 유틸리티
def post_entry(
    client: Client,
    *,
    vehicle_num: str,
    slot_id: int | None = None,
    entry_at: datetime | None = None,
) -> HttpResponse:
    payload: dict[str, object] = {"vehicle_num": vehicle_num}
    if slot_id is not None:
        payload["slot_id"] = slot_id
    if entry_at is not None:
        payload["entry_at"] = entry_at.isoformat()
    return client.post(
        "/api/parking/entry",
        data=json.dumps(payload),
        content_type="application/json",
    )


# 출차 API 호출 유틸리티
def post_exit(
    client: Client,
    *,
    vehicle_num: str,
    exit_at: datetime | None = None,
) -> HttpResponse:
    payload: dict[str, object] = {"vehicle_num": vehicle_num}
    if exit_at is not None:
        payload["exit_at"] = exit_at.isoformat()
    return client.post(
        "/api/parking/exit",
        data=json.dumps(payload),
        content_type="application/json",
    )
