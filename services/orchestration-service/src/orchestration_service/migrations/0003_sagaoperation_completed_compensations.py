from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("orchestration_service", "0002_sagaoperation_compensation_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="sagaoperation",
            name="completed_compensations",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
