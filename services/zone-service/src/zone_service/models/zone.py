from django.db import models


class Zone(models.Model):

    zone_id = models.BigAutoField(primary_key=True)
    zone_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ZONE"
