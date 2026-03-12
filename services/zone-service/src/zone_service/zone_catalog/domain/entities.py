from django.db import models


class Zone(models.Model):
    zone_id = models.BigAutoField(primary_key=True)
    zone_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ZONE"


class SlotType(models.Model):
    slot_type_id = models.BigAutoField(primary_key=True)
    type_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "SLOT_TYPE"


class ParkingSlot(models.Model):
    slot_id = models.BigIntegerField(primary_key=True)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="parking_slots")
    slot_type = models.ForeignKey(
        SlotType,
        on_delete=models.PROTECT,
        related_name="parking_slots",
    )
    slot_code = models.CharField(max_length=50, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ZONE_PARKING_SLOT"
