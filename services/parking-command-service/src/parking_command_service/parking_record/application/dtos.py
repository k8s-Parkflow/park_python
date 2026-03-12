from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SlotCommand:
    vehicle_num: str
    zone_id: int
    slot_code: str
    slot_id: int
    slot_type: str | None = None

    @property
    def slot_name(self) -> str:
        return self.slot_code


@dataclass(frozen=True)
class EntryCommand(SlotCommand):
    entry_at: datetime | None = None


@dataclass(frozen=True)
class ExitCommand(SlotCommand):
    exit_at: datetime | None = None


@dataclass(frozen=True)
class ParkingRecordSnapshot:
    history_id: int
    vehicle_num: str
    zone_id: int
    slot_code: str
    slot_id: int
    status: str
    entry_at: datetime
    exit_at: datetime | None

    @property
    def slot_name(self) -> str:
        return self.slot_code

    def to_dict(self) -> dict[str, object]:
        return {
            "history_id": self.history_id,
            "vehicle_num": self.vehicle_num,
            "zone_id": self.zone_id,
            "slot_name": self.slot_code,
            "slot_id": self.slot_id,
            "status": self.status,
            "entry_at": self.entry_at.isoformat(),
            "exit_at": self.exit_at.isoformat() if self.exit_at else None,
        }
