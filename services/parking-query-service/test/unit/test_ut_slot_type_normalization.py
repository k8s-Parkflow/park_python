from django.test import SimpleTestCase

from unit.support import EvAvailabilityRepoStub, ZoneRepoStub


class SlotTypeNormalizationUT(SimpleTestCase):

    def test_normalizes_mixed_case_slot_type(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=ZoneRepoStub(),
            zone_availability_repository=EvAvailabilityRepoStub(),
        )

        result = service.get(slot_type="eV")

        self.assertEqual(
            result,
            {
                "slotType": "EV",
                "availableCount": 60,
            },
        )
