from django.db import models


class ParkingCommandOperation(models.Model):
    operation_id = models.CharField(max_length=64)
    action = models.CharField(max_length=64)
    response_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PARKING_COMMAND_OPERATION"
        constraints = [
            models.UniqueConstraint(
                fields=["operation_id", "action"],
                name="uniq_parking_command_operation_action",
            ),
        ]
