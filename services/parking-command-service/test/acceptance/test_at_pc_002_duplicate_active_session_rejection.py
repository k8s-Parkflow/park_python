"""AT-PC-002: 활성 세션 중복 입차 거부 acceptance test."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest


SERVICE_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = SERVICE_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class DuplicateActiveSessionRejectionAcceptanceTest(unittest.TestCase):
    def test_at_pc_002_reject_duplicate_entry_for_same_vehicle(self) -> None:
        """
        Given: 동일 vehicle_num 활성 세션(exit_at IS NULL) 존재
        When: 동일 차량으로 다시 입차 요청
        Then: 409 충돌, 신규 세션 미생성
        """
        from parking_command_service import (
            DuplicateActiveSessionError,
            InMemoryParkingRepository,
            ParkingCommandService,
        )

        repository = InMemoryParkingRepository(
            slots=[
                {
                    "slot_id": "A-01",
                    "zone_id": "ZONE-A",
                    "is_active": True,
                    "occupied": False,
                },
                {
                    "slot_id": "A-02",
                    "zone_id": "ZONE-A",
                    "is_active": True,
                    "occupied": False,
                },
            ]
        )
        service = ParkingCommandService(repository=repository)

        first = service.entry(
            vehicle_num="12가3456",
            slot_id="A-01",
            entered_at="2026-03-05T10:00:00Z",
        )

        with self.assertRaises(DuplicateActiveSessionError) as error:
            service.entry(
                vehicle_num="12가3456",
                slot_id="A-02",
                entered_at="2026-03-05T10:05:00Z",
            )

        active_session = repository.find_active_session_by_vehicle("12가3456")
        sessions = repository.list_sessions_by_vehicle("12가3456")

        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(first["slot_id"], "A-01")
        self.assertEqual(active_session["slot_id"], "A-01")
        self.assertEqual(len(sessions), 1)


if __name__ == "__main__":
    unittest.main()
