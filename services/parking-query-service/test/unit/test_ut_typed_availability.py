from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from unit.support import (
    DisabledAvailabilityRepoStub,
    EmptyAvailabilityRepoStub,
    EvAvailabilityRepoStub,
    GeneralAvailabilityRepoStub,
    ZoneRepoStub,
)


class TypedAvailabilityUT(SimpleTestCase):

    def test_returns_general_total(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=ZoneRepoStub(),
            zone_availability_repository=GeneralAvailabilityRepoStub(),
        )

        result = service.get(slot_type="GENERAL")

        self.assertEqual(
            result,
            {
                "slotType": "GENERAL",
                "availableCount": 12,
            },
        )

    def test_returns_ev_total(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=ZoneRepoStub(),
            zone_availability_repository=EvAvailabilityRepoStub(),
        )

        result = service.get(slot_type="EV")

        self.assertEqual(
            result,
            {
                "slotType": "EV",
                "availableCount": 60,
            },
        )

    def test_returns_disabled_total(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=ZoneRepoStub(),
            zone_availability_repository=DisabledAvailabilityRepoStub(),
        )

        result = service.get(slot_type="DISABLED")

        self.assertEqual(
            result,
            {
                "slotType": "DISABLED",
                "availableCount": 6,
            },
        )

    def test_rejects_invalid_slot_type(self) -> None:
        from parking_query_service.services.zone_availability_service import (
            ZoneAvailabilityService,
        )

        service = ZoneAvailabilityService(
            zone_repository=ZoneRepoStub(),
            zone_availability_repository=EmptyAvailabilityRepoStub(),
        )

        with self.assertRaises(ValidationError) as context:
            service.get(slot_type="VIP")

        self.assertEqual(
            context.exception.message_dict,
            {"slot_type": ["지원하지 않는 슬롯 타입입니다."]},
        )
