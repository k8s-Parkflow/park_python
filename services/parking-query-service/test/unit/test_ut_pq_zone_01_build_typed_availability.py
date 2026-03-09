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


class FakeEvAvailabilityRepository:
    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[ZoneAvailabilityStub]:
        # EV 요청일 때 전체 Zone 세 곳의 잔여석 10 + 20 + 30을 반환한다.
        assert slot_type == "EV"
        return [
            ZoneAvailabilityStub(zone_id=1, available_count=10),
            ZoneAvailabilityStub(zone_id=2, available_count=20),
            ZoneAvailabilityStub(zone_id=3, available_count=30),
        ]


class FakeDisabledAvailabilityRepository:
    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[ZoneAvailabilityStub]:
        # DISABLED 요청일 때 전체 Zone 세 곳의 잔여석 1 + 2 + 3을 반환한다.
        assert slot_type == "DISABLED"
        return [
            ZoneAvailabilityStub(zone_id=1, available_count=1),
            ZoneAvailabilityStub(zone_id=2, available_count=2),
            ZoneAvailabilityStub(zone_id=3, available_count=3),
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

    def test_should_return_total_available_count__when_ev_slot_type_requested(
        self,
    ) -> None:
        # Given
        # 서비스는 전체 Zone의 EV 타입 여석을 합산해 단일 숫자로 반환해야 한다.
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=FakeZoneRepository(),
            zone_availability_repository=FakeEvAvailabilityRepository(),
        )

        # When
        result = service.get(slot_type="EV")

        # Then
        # Zone A(10) + Zone B(20) + Zone C(30)이 합산된 60이 반환되어야 한다.
        self.assertEqual(
            result,
            {
                "slotType": "EV",
                "availableCount": 60,
            },
        )

    def test_should_return_total_available_count__when_disabled_slot_type_requested(
        self,
    ) -> None:
        # Given
        # 서비스는 전체 Zone의 장애인 타입 여석을 합산해 단일 숫자로 반환해야 한다.
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=FakeZoneRepository(),
            zone_availability_repository=FakeDisabledAvailabilityRepository(),
        )

        # When
        result = service.get(slot_type="DISABLED")

        # Then
        # Zone A(1) + Zone B(2) + Zone C(3)이 합산된 6이 반환되어야 한다.
        self.assertEqual(
            result,
            {
                "slotType": "DISABLED",
                "availableCount": 6,
            },
        )
