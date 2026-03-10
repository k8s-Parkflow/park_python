from django.db import models

from zone_service.models.slot_type import SlotType
from zone_service.models.zone import Zone


class ParkingSlot(models.Model):
    slot_id = models.BigIntegerField(primary_key=True)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="parking_slots")
    slot_type = models.ForeignKey(
        SlotType,
        on_delete=models.PROTECT,
        related_name="parking_slots",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ZONE_PARKING_SLOT"
