from django.test import SimpleTestCase

from unit.support import EmptyAvailabilityRepoStub


class EmptyProjectionUT(SimpleTestCase):

    def test_returns_zero_for_missing_ev(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_availability_repository=EmptyAvailabilityRepoStub(),
        )

        result = service.get(slot_type="EV")

        self.assertEqual(
            result,
            {
                "slotType": "EV",
                "availableCount": 0,
            },
        )
