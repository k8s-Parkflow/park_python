from django.db import models


class CurrentParkingView(models.Model):

    vehicle_num = models.CharField(max_length=20, primary_key=True)
    slot_id = models.BigIntegerField()
    zone_id = models.BigIntegerField()
    slot_type = models.CharField(max_length=50)
    entry_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "CURRENT_PARKING_VIEW"
