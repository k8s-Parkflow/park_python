from __future__ import annotations

from parking_command_service.domains.parking_record.domain import (
    ParkingHistory,
    ParkingHistoryStatus,
    ParkingSlot,
    SlotOccupancy,
)
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType
from zone_service.models import ParkingSlot as ZoneParkingSlot
from zone_service.models import SlotType, Zone


# 차량 테스트 데이터 생성 유틸리티
def create_vehicle(*, vehicle_num: str = "69가3455", vehicle_type: VehicleType = VehicleType.General) -> Vehicle:
    return Vehicle.objects.create(vehicle_num=vehicle_num, vehicle_type=vehicle_type)


# 구역 테스트 데이터 생성 유틸리티
def create_zone(*, zone_id: int = 1, zone_name: str | None = None, is_active: bool = True) -> Zone:
    zone, _created = Zone.objects.get_or_create(
        zone_id=zone_id,
        defaults={
            "zone_name": zone_name or f"ZONE-{zone_id}",
            "is_active": is_active,
        },
    )
    updated_fields: list[str] = []
    if zone_name is not None and zone.zone_name != zone_name:
        zone.zone_name = zone_name
        updated_fields.append("zone_name")
    if zone.is_active != is_active:
        zone.is_active = is_active
        updated_fields.append("is_active")
    if updated_fields:
        zone.save(update_fields=updated_fields)
    return zone


# 슬롯 테스트 데이터 생성 유틸리티
def create_slot(
    *,
    zone_id: int = 1,
    slot_type_id: int = 1,
    slot_type_name: str | None = None,
    slot_code: str = "A001",
    is_active: bool = True,
) -> ParkingSlot:
    zone = create_zone(zone_id=zone_id)
    resolved_slot_type_name = slot_type_name or {
        1: "GENERAL",
        2: "EV",
        3: "DISABLED",
    }.get(slot_type_id, f"TYPE-{slot_type_id}")
    slot_type = create_slot_type(slot_type_id=slot_type_id, type_name=resolved_slot_type_name)
    lock_anchor = ParkingSlot.objects.create(
        zone_id=zone_id,
        slot_code=slot_code,
        is_active=is_active,
    )
    ZoneParkingSlot.objects.update_or_create(
        slot_id=lock_anchor.slot_id,
        defaults={
            "zone": zone,
            "slot_type": slot_type,
            "slot_code": slot_code,
            "is_active": is_active,
        },
    )
    return lock_anchor


# 슬롯 타입 테스트 데이터 생성 유틸리티
def create_slot_type(*, slot_type_id: int = 1, type_name: str = "TYPE-1") -> SlotType:
    slot_type, _created = SlotType.objects.get_or_create(
        slot_type_id=slot_type_id,
        defaults={"type_name": type_name},
    )
    if slot_type.type_name != type_name:
        slot_type.type_name = type_name
        slot_type.save(update_fields=["type_name"])
    return slot_type


# 빈 점유 상태 생성 유틸리티
def create_empty_occupancy(*, slot: ParkingSlot) -> SlotOccupancy:
    return SlotOccupancy.objects.create(slot=slot)


# 활성 주차 이력 생성 유틸리티
def create_active_history(
    *,
    slot: ParkingSlot,
    vehicle_num: str,
    entry_at,
    slot_type_id: int | None = None,
) -> ParkingHistory:
    resolved_slot_type_id = slot_type_id
    if resolved_slot_type_id is None:
        resolved_slot_type_id = (
            ZoneParkingSlot.objects.only("slot_type_id").get(slot_id=slot.slot_id).slot_type_id
        )
    return ParkingHistory.objects.create(
        slot=slot,
        zone_id=slot.zone_id,
        slot_type_id=resolved_slot_type_id,
        slot_code=slot.slot_code,
        vehicle_num=vehicle_num,
        status=ParkingHistoryStatus.PARKED,
        entry_at=entry_at,
    )


# 점유 완료 세션 생성 유틸리티
def create_occupied_session(
    *,
    slot: ParkingSlot,
    vehicle_num: str,
    entry_at,
) -> tuple[ParkingHistory, SlotOccupancy]:
    history = create_active_history(slot=slot, vehicle_num=vehicle_num, entry_at=entry_at)
    occupancy = SlotOccupancy.objects.create(
        slot=slot,
        occupied=True,
        vehicle_num=vehicle_num,
        history=history,
        occupied_at=entry_at,
    )
    return history, occupancy
