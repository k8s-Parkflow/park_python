from django.db import IntegrityError, transaction
from django.test import TestCase

from parking_query_service.models import ZoneAvailability


class ZoneAvailabilityConstraintRepositoryTest(TestCase):

    def test_should_fail_when_zone_availability_invariant_is_broken__when_available_count_is_negative(
        self,
    ) -> None:
        # Given
        # 여석은 음수가 될 수 없으므로 DB 제약으로 저장이 막혀야 한다.

        # When / Then
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ZoneAvailability.objects.create(
                    zone_id=1,
                    slot_type="GENERAL",
                    total_count=10,
                    occupied_count=12,
                    available_count=-2,
                )

    def test_should_fail_when_zone_availability_invariant_is_broken__when_available_count_does_not_match_formula(
        self,
    ) -> None:
        # Given
        # available_count는 total_count - occupied_count와 반드시 일치해야 한다.

        # When / Then
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ZoneAvailability.objects.create(
                    zone_id=1,
                    slot_type="GENERAL",
                    total_count=10,
                    occupied_count=7,
                    available_count=1,
                )
