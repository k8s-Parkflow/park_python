from __future__ import annotations

import sys
from pathlib import Path
import unittest


SERVICE_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = SERVICE_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class TestATPC004InactiveSlotRejection(unittest.TestCase):

    def test_inactive_slot_cannot_be_assigned(self):
        """
        AT-PC-004
        Given: 슬롯 is_active=false
        When: 입차 요청
        Then: 400 또는 409 실패, 세션/점유 미생성
        """
        try:
            from parking_command_service import (
                InMemoryParkingRepository,
                ParkingCommandService,
            )
        except ModuleNotFoundError:
            self.fail(
                "AT-PC-004 RED: missing module "
                "'parking_command_service.InMemoryParkingRepository/ParkingCommandService'"
            )

        repository = InMemoryParkingRepository(
            slots=[
                {
                    "slot_id": "A-02",
                    "zone_id": "ZONE-A",
                    "is_active": False,
                    "occupied": False,
                }
            ]
        )
        service = ParkingCommandService(repository=repository)

        response = None
        raised_status_code = None
        try:
            response = service.entry(
                vehicle_num="12가3456",
                slot_id="A-02",
                entered_at="2026-03-05T10:05:00Z",
            )
        except Exception as exc:  # RED 단계: 에러 모델이 아직 확정되지 않음.
            raised_status_code = getattr(exc, "status_code", None)

        if response is not None:
            self.assertIn(response.get("status_code"), {400, 409})
            self.assertFalse(response.get("history_created", True))
            self.assertFalse(response.get("occupancy_created", True))
        else:
            self.assertIn(
                raised_status_code,
                {400, 409},
                "비활성 슬롯 배정 거부는 400 또는 409 계열이어야 합니다.",
            )

        active_session = repository.find_active_session_by_vehicle("12가3456")
        occupancy = repository.get_slot_occupancy("A-02")

        self.assertIsNone(active_session)
        self.assertFalse(occupancy["occupied"])
        self.assertIsNone(occupancy["current_session_id"])


if __name__ == "__main__":
    unittest.main()
