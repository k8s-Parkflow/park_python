from __future__ import annotations

import sys
from pathlib import Path

from django.test import SimpleTestCase

from parking_command_service.dependencies import get_parking_record_command_service
from parking_command_service.repositories import (
    DjangoParkingRecordRepository,
    DjangoVehicleRepository,
)
from parking_command_service.services import ParkingRecordCommandService

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))


# 의존성 조립 단위 테스트 클래스
class ParkingRecordDependenciesUnitTests(SimpleTestCase):
    # command 서비스 기본 조립 검증
    def test_should_build_command_service_with_django_repositories(self) -> None:
        # Given / When
        service = get_parking_record_command_service()

        # Then
        self.assertIsInstance(service, ParkingRecordCommandService)
        self.assertIsInstance(service.parking_record_repository, DjangoParkingRecordRepository)
        self.assertIsInstance(service.vehicle_repository, DjangoVehicleRepository)
