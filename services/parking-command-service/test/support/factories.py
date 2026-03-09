from __future__ import annotations

from parking_command_service.models import ParkingHistory, ParkingSlot, SlotOccupancy
from parking_command_service.models.enums import ParkingHistoryStatus
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType
from zone_service.models import SlotType


# 차량 테스트 데이터 생성 유틸리티
def create_vehicle(*, vehicle_num: str = "69가3455", vehicle_type: VehicleType = VehicleType.General) -> Vehicle:
    return Vehicle.objects.create(vehicle_num=vehicle_num, vehicle_type=vehicle_type)


# 슬롯 테스트 데이터 생성 유틸리티
def create_slot(
    *,
    zone_id: int = 1,
    slot_type_id: int = 1,
    slot_type_name: str | None = None,
    slot_code: str = "A001",
    is_active: bool = True,
) -> ParkingSlot:
    create_slot_type(slot_type_id=slot_type_id, type_name=slot_type_name or f"TYPE-{slot_type_id}")
    return ParkingSlot.objects.create(
        zone_id=zone_id,
        slot_type_id=slot_type_id,
        slot_code=slot_code,
        is_active=is_active,
    )


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
) -> ParkingHistory:
    return ParkingHistory.objects.create(
        slot=slot,
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
