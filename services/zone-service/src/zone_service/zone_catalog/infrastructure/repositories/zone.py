from __future__ import annotations

from zone_service.zone_catalog.domain.entities import Zone


class ZoneRepository:
    def get(self, *, zone_id: int) -> Zone:
        return Zone.objects.get(zone_id=zone_id)
