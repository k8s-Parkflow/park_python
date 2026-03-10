from django.test import TestCase

from parking_query_service.models import ZoneAvailability


class ZoneAvailabilityRepositoryTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # GENERAL, EV, DISABLED가 섞여 있어도 요청한 타입만 조회되어야 한다.
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=7,
            available_count=3,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=6,
            available_count=4,
        )
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="EV",
            total_count=10,
            occupied_count=9,
            available_count=1,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="DISABLED",
            total_count=10,
            occupied_count=8,
            available_count=2,
        )

    def test_should_fetch_total_available_count_by_slot_type__when_repository_called(
        self,
    ) -> None:
        # Given
        # 타입별 집계 조회는 요청한 타입 데이터만 반환해야 한다.
        from parking_query_service.repositories.zone_availability_repository import (
            ZoneAvailabilityRepository,
        )

        repository = ZoneAvailabilityRepository()

        # When
        counts = repository.get_counts_by_slot_type(slot_type="GENERAL")

        # Then
        self.assertEqual(
            [count.zone_id for count in counts],
            [1, 2],
        )
        self.assertEqual(
            sum(count.available_count for count in counts),
            7,
        )
