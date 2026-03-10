from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("parking_query_service", "0002_parkingqueryoperation"),
        ("parking_query_service", "0005_backfill_current_parking_slot_code"),
    ]

    operations = []
