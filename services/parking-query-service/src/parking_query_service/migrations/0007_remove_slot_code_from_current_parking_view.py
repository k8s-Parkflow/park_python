from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("parking_query_service", "0006_merge_proj23_main"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="currentparkingview",
            name="slot_code",
        ),
    ]
