from __future__ import annotations

import copy
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path


SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(SERVICE_SRC))


@dataclass
class SlotState:
    slot_id: str
    occupied: bool
    current_session_id: str | None


class InMemorySlotRepository:
    def __init__(self, slot: SlotState) -> None:
        self._slot = copy.deepcopy(slot)

    def get(self, slot_id: str) -> SlotState:
        if self._slot.slot_id != slot_id:
            raise KeyError(slot_id)
        return copy.deepcopy(self._slot)

    def save(self, slot: SlotState) -> None:
        self._slot = copy.deepcopy(slot)


class InMemoryParkingHistoryRepository:
    def __init__(self) -> None:
        self._created_sessions: list[dict] = []

    def create(self, session_data: dict) -> None:
        self._created_sessions.append(copy.deepcopy(session_data))

    def all_created(self) -> list[dict]:
        return copy.deepcopy(self._created_sessions)


class AtPc003RejectOccupiedSlotEntryTest(unittest.TestCase):
    def test_reject_entry_when_target_slot_is_already_occupied(self) -> None:
        """AT-PC-003: occupied slot entry request must be rejected with no state changes."""
        try:
            from parking_command_service.application.entry import ParkingCommandService
        except ModuleNotFoundError:
            self.fail(
                "AT-PC-003 RED: missing module "
                "'parking_command_service.application.entry.ParkingCommandService'"
            )

        slot_repo = InMemorySlotRepository(
            SlotState(slot_id="A-01", occupied=True, current_session_id="session-001")
        )
        history_repo = InMemoryParkingHistoryRepository()
        before_slot = slot_repo.get("A-01")

        service = ParkingCommandService(
            slot_repository=slot_repo,
            parking_history_repository=history_repo,
        )
        response = service.handle_entry(
            vehicle_num="12GA3456",
            slot_id="A-01",
            zone_id="ZONE-A",
            idempotency_key="AT-PC-003",
        )

        self.assertEqual(409, response["status_code"])
        self.assertEqual("SLOT_ALREADY_OCCUPIED", response["error_code"])
        self.assertEqual(before_slot, slot_repo.get("A-01"))
        self.assertEqual([], history_repo.all_created())

