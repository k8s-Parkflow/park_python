from __future__ import annotations

import json
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

from parking_command_service.domains.parking_record.application.dtos import (
    EntryCommand,
    ExitCommand,
)
from parking_command_service.global_shared.utils.vehicle_nums import normalize_vehicle_num


def parse_entry_command(*, body: bytes) -> EntryCommand:
    payload = _parse_json_body(body=body)
    # 필드별 오류를 한 번에 모아 표준 bad_request 형태로 반환하는 흐름
    errors: dict[str, list[str]] = {}

    vehicle_num = _normalize_vehicle_num(payload=payload, errors=errors)
    zone_id, slot_code, slot_id = _parse_slot_fields(payload=payload, errors=errors)
    entry_at = _parse_optional_datetime(payload=payload, field_name="entry_at", errors=errors)

    if errors:
        raise ValidationError(errors)

    return EntryCommand(
        vehicle_num=vehicle_num,
        zone_id=zone_id,
        slot_code=slot_code,
        slot_id=slot_id,
        entry_at=entry_at,
    )


def parse_exit_command(*, body: bytes) -> ExitCommand:
    payload = _parse_json_body(body=body)
    errors: dict[str, list[str]] = {}

    vehicle_num = _normalize_vehicle_num(payload=payload, errors=errors)
    zone_id, slot_code, slot_id = _parse_slot_fields(payload=payload, errors=errors)
    exit_at = _parse_optional_datetime(payload=payload, field_name="exit_at", errors=errors)

    if errors:
        raise ValidationError(errors)

    return ExitCommand(
        vehicle_num=vehicle_num,
        zone_id=zone_id,
        slot_code=slot_code,
        slot_id=slot_id,
        exit_at=exit_at,
    )


def _parse_slot_fields(
    *,
    payload: dict[str, object],
    errors: dict[str, list[str]],
) -> tuple[int, str, int]:
    return (
        _require_int(payload=payload, field_name="zone_id", errors=errors),
        _require_slot_code(payload=payload, errors=errors),
        _require_int(payload=payload, field_name="slot_id", errors=errors),
    )


def _parse_json_body(*, body: bytes) -> dict[str, object]:
    try:
        payload = json.loads(body or b"{}")
    except json.JSONDecodeError as exc:
        raise ValidationError({"body": ["JSON 본문 형식이 올바르지 않습니다."]}) from exc

    if not isinstance(payload, dict):
        raise ValidationError({"body": ["JSON 객체만 허용됩니다."]})
    return payload


def _normalize_vehicle_num(
    *,
    payload: dict[str, object],
    errors: dict[str, list[str]],
) -> str:
    vehicle_num = payload.get("vehicle_num")
    if vehicle_num is None:
        errors["vehicle_num"] = ["필수 입력값입니다."]
        return ""
    if not isinstance(vehicle_num, str):
        errors["vehicle_num"] = ["문자열이어야 합니다."]
        return ""

    try:
        return normalize_vehicle_num(vehicle_num)
    except ValidationError as exc:
        # 정규화 실패도 serializer 레벨에서는 필드 오류로 다시 적재한다.
        errors["vehicle_num"] = exc.messages
        return ""


def _require_int(
    *,
    payload: dict[str, object],
    field_name: str,
    errors: dict[str, list[str]],
) -> int:
    value = payload.get(field_name)
    if value is None:
        errors[field_name] = ["필수 입력값입니다."]
        return 0
    if not isinstance(value, int):
        errors[field_name] = ["정수여야 합니다."]
        return 0
    return value


def _require_slot_code(
    *,
    payload: dict[str, object],
    errors: dict[str, list[str]],
) -> str:
    field_name = "slot_code"
    value = payload.get(field_name)
    if value is None:
        errors[field_name] = ["필수 입력값입니다."]
        return ""
    if not isinstance(value, str):
        errors[field_name] = ["문자열이어야 합니다."]
        return ""
    if value == "":
        errors[field_name] = ["비어 있을 수 없습니다."]
        return ""
    if value.strip() != value:
        errors[field_name] = ["앞뒤 공백 없이 입력해야 합니다."]
        return ""
    if value.upper() != value:
        errors[field_name] = ["대문자 형식이어야 합니다."]
        return ""
    return value


def _parse_optional_datetime(
    *,
    payload: dict[str, object],
    field_name: str,
    errors: dict[str, list[str]],
) -> datetime | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        errors[field_name] = ["ISO 8601 문자열이어야 합니다."]
        return None

    parsed_datetime = parse_datetime(value)
    if parsed_datetime is None:
        errors[field_name] = ["올바른 datetime 형식이어야 합니다."]
        return None
    # 명령 API는 timezone-aware 값만 받아 write 시점을 명확히 고정한다.
    if parsed_datetime.tzinfo is None or parsed_datetime.utcoffset() is None:
        errors[field_name] = ["timezone-aware datetime이어야 합니다."]
        return None
    return parsed_datetime
