from django.db import models


class SlotType(models.Model):

    slot_type_id = models.BigAutoField(primary_key=True)
    type_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "SLOT_TYPE"
