from django.test import SimpleTestCase

from unit.support import PartialTotalAvailabilityRepoStub, TotalAvailabilityRepoStub, ZoneRepoStub


class MissingTypeTotalUT(SimpleTestCase):

    def test_returns_total_without_slot_type(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=ZoneRepoStub(),
            zone_availability_repository=TotalAvailabilityRepoStub(),
        )

        result = service.get(slot_type="")

        self.assertEqual(
            result,
            {
                "availableCount": 78,
            },
        )

    def test_returns_total_with_missing_types(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=ZoneRepoStub(),
            zone_availability_repository=PartialTotalAvailabilityRepoStub(),
        )

        result = service.get(slot_type="")

        self.assertEqual(
            result,
            {
                "availableCount": 7,
            },
        )
