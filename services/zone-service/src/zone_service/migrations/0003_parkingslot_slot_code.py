from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zone_service", "0002_parkingslot_zone_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="parkingslot",
            name="slot_code",
            field=models.CharField(default="", max_length=50),
        ),
    ]
