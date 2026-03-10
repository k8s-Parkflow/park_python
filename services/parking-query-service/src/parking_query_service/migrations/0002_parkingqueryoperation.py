from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("parking_query_service", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParkingQueryOperation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("operation_id", models.CharField(max_length=64)),
                ("action", models.CharField(max_length=64)),
                ("response_payload", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "PARKING_QUERY_OPERATION"},
        ),
        migrations.AddConstraint(
            model_name="parkingqueryoperation",
            constraint=models.UniqueConstraint(
                fields=("operation_id", "action"),
                name="uniq_parking_query_operation_action",
            ),
        ),
    ]
