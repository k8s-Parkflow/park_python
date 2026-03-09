from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EntryCommand:
    vehicle_num: str
    slot_id: int
    entry_at: datetime | None


@dataclass(frozen=True)
class ExitCommand:
    vehicle_num: str
    exit_at: datetime | None


@dataclass(frozen=True)
class ParkingRecordSnapshot:
    history_id: int
    vehicle_num: str
    slot_id: int
    status: str
    entry_at: datetime
    exit_at: datetime | None

    def to_dict(self) -> dict[str, object]:
        return {
            "history_id": self.history_id,
            "vehicle_num": self.vehicle_num,
            "slot_id": self.slot_id,
            "status": self.status,
            "entry_at": self.entry_at.isoformat(),
            "exit_at": self.exit_at.isoformat() if self.exit_at else None,
        }
