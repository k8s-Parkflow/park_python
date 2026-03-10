from dataclasses import dataclass


@dataclass(frozen=True)
class AvailabilityStub:
    zone_id: int
    available_count: int

class GeneralAvailabilityRepoStub:

    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[AvailabilityStub]:
        assert slot_type == "GENERAL"
        return [
            AvailabilityStub(zone_id=1, available_count=3),
            AvailabilityStub(zone_id=2, available_count=4),
            AvailabilityStub(zone_id=3, available_count=5),
        ]


class EvAvailabilityRepoStub:

    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[AvailabilityStub]:
        assert slot_type == "EV"
        return [
            AvailabilityStub(zone_id=1, available_count=10),
            AvailabilityStub(zone_id=2, available_count=20),
            AvailabilityStub(zone_id=3, available_count=30),
        ]


class DisabledAvailabilityRepoStub:

    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[AvailabilityStub]:
        assert slot_type == "DISABLED"
        return [
            AvailabilityStub(zone_id=1, available_count=1),
            AvailabilityStub(zone_id=2, available_count=2),
            AvailabilityStub(zone_id=3, available_count=3),
        ]


class EmptyAvailabilityRepoStub:

    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[AvailabilityStub]:
        return []


class TotalAvailabilityRepoStub:

    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[AvailabilityStub]:
        assert slot_type == ""
        return [
            AvailabilityStub(zone_id=1, available_count=14),
            AvailabilityStub(zone_id=2, available_count=26),
            AvailabilityStub(zone_id=3, available_count=38),
        ]


class PartialTotalAvailabilityRepoStub:

    def get_counts_by_slot_type(
        self,
        *,
        slot_type: str,
    ) -> list[AvailabilityStub]:
        assert slot_type == ""
        return [
            AvailabilityStub(zone_id=1, available_count=3),
            AvailabilityStub(zone_id=2, available_count=4),
        ]
