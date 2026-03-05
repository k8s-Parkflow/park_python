"""AT-PC-001: 입차 성공 acceptance test."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest


SERVICE_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = SERVICE_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class ParkingEntryAcceptanceTest(unittest.TestCase):
    def test_at_pc_001_entry_success(self) -> None:
        """활성/비점유 슬롯에 입차하면 세션과 점유가 함께 생성되어야 한다."""
        from parking_command_service import InMemoryParkingRepository, ParkingCommandService

        repository = InMemoryParkingRepository(
            slots=[
                {
                    "slot_id": "A-01",
                    "zone_id": "ZONE-A",
                    "is_active": True,
                    "occupied": False,
                }
            ]
        )
        service = ParkingCommandService(repository=repository)

        response = service.entry(
            vehicle_num="12가3456",
            slot_id="A-01",
            entered_at="2026-03-05T10:00:00Z",
        )

        active_session = repository.find_active_session_by_vehicle("12가3456")
        occupancy = repository.get_slot_occupancy("A-01")

        self.assertEqual(response["vehicle_num"], "12가3456")
        self.assertEqual(response["slot_id"], "A-01")
        self.assertEqual(active_session["status"], "PARKED")
        self.assertIsNone(active_session["exit_at"])
        self.assertTrue(occupancy["occupied"])
        self.assertEqual(occupancy["current_session_id"], active_session["history_id"])


if __name__ == "__main__":
    unittest.main()
