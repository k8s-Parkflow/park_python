from __future__ import annotations

from zone_service.models import Zone


class ZoneRepository:
    def get(self, *, zone_id: int) -> Zone:
        return Zone.objects.get(zone_id=zone_id)
