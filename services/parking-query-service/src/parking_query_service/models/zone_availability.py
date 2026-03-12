from django.db import models
from django.db.models import F, Q


class ZoneAvailability(models.Model):
    id = models.BigAutoField(primary_key=True)

    zone_id = models.BigIntegerField()
    slot_type = models.CharField(max_length=50)
    total_count = models.IntegerField()
    occupied_count = models.IntegerField()
    available_count = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ZONE_AVAILABILITY"
        indexes = [
            models.Index(fields=["zone_id", "slot_type"], name="idx_zone_type"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["zone_id", "slot_type"],
                name="uniq_zone_availability_zone_slot_type",
            ),
            models.CheckConstraint(
                check=Q(available_count=F("total_count") - F("occupied_count"))
                & Q(available_count__gte=0),
                name="chk_zone_availability_available_count",
            ),
        ]
