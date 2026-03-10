from django.db import models


class ParkingSlot(models.Model):

    slot_id = models.BigAutoField(primary_key=True)
    zone_id = models.BigIntegerField()
    slot_type_id = models.BigIntegerField()
    # slot_name is the human-readable slot label such as A001.
    slot_name = models.CharField(max_length=50, db_column="slot_name")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PARKING_SLOT"
        constraints = [
            models.UniqueConstraint(fields=["zone_id", "slot_name"], name="uniq_slot_zone_slot_name"),
        ]

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
