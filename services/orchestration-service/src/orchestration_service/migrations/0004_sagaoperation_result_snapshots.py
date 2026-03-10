from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("orchestration_service", "0003_sagaoperation_completed_compensations"),
    ]

    operations = [
        migrations.AddField(
            model_name="sagaoperation",
            name="error_payload",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sagaoperation",
            name="error_status",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sagaoperation",
            name="failed_step",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="sagaoperation",
            name="response_payload",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
