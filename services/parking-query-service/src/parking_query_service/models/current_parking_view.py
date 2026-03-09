from django.db import models


class CurrentParkingView(models.Model):

    vehicle_num = models.CharField(max_length=20, primary_key=True)
    zone_name = models.CharField(max_length=100)
    slot_name = models.CharField(max_length=50)
    slot_type = models.CharField(max_length=50)
    entry_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "CURRENT_PARKING_VIEW"
