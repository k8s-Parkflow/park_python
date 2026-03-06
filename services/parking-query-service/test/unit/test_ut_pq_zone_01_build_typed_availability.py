from dataclasses import dataclass

from django.test import SimpleTestCase


@dataclass(frozen=True)
class ZoneStub:

    # 전체 Zone 합산에 필요한 최소 식별 정보만 유지한다.
    zone_id: int
    zone_name: str


@dataclass(frozen=True)
class ZoneAvailabilityStub:

    # 타입별 여석 합산에 필요한 최소 데이터만 유지한다.
    zone_id: int
    available_count: int


class FakeZoneRepository:

    def list_zones(self) -> list[ZoneStub]:
        # 서비스는 이 목록의 모든 Zone을 전체 합산 대상으로 사용해야 한다.
        return [
            ZoneStub(zone_id=1, zone_name="A"),
            ZoneStub(zone_id=2, zone_name="B"),
            ZoneStub(zone_id=3, zone_name="C"),
        ]


class FakeTypedAvailabilityRepository:

    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[ZoneAvailabilityStub]:
        # GENERAL 요청일 때 전체 Zone 세 곳의 잔여석 3 + 4 + 5를 반환한다.
        assert slot_type == "GENERAL"
        return [
            ZoneAvailabilityStub(zone_id=1, available_count=3),
            ZoneAvailabilityStub(zone_id=2, available_count=4),
            ZoneAvailabilityStub(zone_id=3, available_count=5),
        ]


class ZoneAvailabilityQueryServiceUnitTest(SimpleTestCase):

    def test_should_return_total_available_count__when_general_slot_type_requested(
        self,
    ) -> None:

        # Given
        # 서비스는 전체 Zone을 기준으로 해당 타입의 여석만 합산해야 한다.
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=FakeZoneRepository(),
            zone_availability_repository=FakeTypedAvailabilityRepository(),
        )

        # When
        result = service.get(slot_type="GENERAL")

        # Then
        # Zone별 상세가 아니라 전체 합계 12만 반환되어야 한다.
        self.assertEqual(
            result,
            {
                "slotType": "GENERAL",
                "availableCount": 12,
            },
        )
