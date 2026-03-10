from __future__ import annotations

from unittest import TestCase

from orchestration_service.models import SagaOperation
from parking_command_service.models import ParkingHistory
from parking_query_service.models import CurrentParkingView
from park_py.database_router import ServiceDatabaseRouter
from vehicle_service.models import Vehicle
from zone_service.models import Zone


class MsaDatabaseRouterContractTests(TestCase):
    def test_should_route_each_service_model_to_its_database__when_router_is_used(self) -> None:
        """[CT-MSA-DB-01] app label별 DB 라우팅 계약"""

        router = ServiceDatabaseRouter()

        self.assertEqual(router.db_for_read(SagaOperation), "default")
        self.assertEqual(router.db_for_write(Vehicle), "vehicle")
        self.assertEqual(router.db_for_write(Zone), "zone")
        self.assertEqual(router.db_for_write(ParkingHistory), "parking_command")
        self.assertEqual(router.db_for_write(CurrentParkingView), "parking_query")
