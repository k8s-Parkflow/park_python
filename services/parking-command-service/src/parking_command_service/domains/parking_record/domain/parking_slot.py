from django.db import models


class ParkingSlot(models.Model):
    """
    Command-side lock anchor for slot occupancy transitions.

    `zone-service` owns the authoritative slot metadata. This model remains in
    `parking-command-service` only so write flows can lock a stable row per
    `slot_id` before mutating `SlotOccupancy` and `ParkingHistory`.
    """

    slot_id = models.BigAutoField(primary_key=True)
    # Mirrored operational metadata. These fields are not the source of truth.
    zone_id = models.BigIntegerField()
    # Human-readable slot label mirrored from zone metadata.
    slot_code = models.CharField(max_length=50, db_column="slot_name")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PARKING_SLOT"
        constraints = [
            models.UniqueConstraint(fields=["zone_id", "slot_code"], name="uniq_slot_zone_slot_name"),
        ]
