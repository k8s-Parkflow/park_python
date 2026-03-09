from __future__ import annotations

from parking_command_service.models import ParkingHistory, ParkingSlot, SlotOccupancy
from parking_command_service.models.enums import ParkingHistoryStatus
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType


# 차량 테스트 데이터 생성 유틸리티
def create_vehicle(*, vehicle_num: str = "69가3455", vehicle_type: VehicleType = VehicleType.General) -> Vehicle:
    return Vehicle.objects.create(vehicle_num=vehicle_num, vehicle_type=vehicle_type)


# 슬롯 테스트 데이터 생성 유틸리티
def create_slot(
    *,
    zone_id: int = 1,
    slot_type_id: int = 1,
    slot_code: str = "A001",
    is_active: bool = True,
) -> ParkingSlot:
    return ParkingSlot.objects.create(
        zone_id=zone_id,
        slot_type_id=slot_type_id,
        slot_code=slot_code,
        is_active=is_active,
    )


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
