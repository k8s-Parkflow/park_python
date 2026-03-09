from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_command_service", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="parkingslot",
            name="uniq_slot_zone_slot_code",
        ),
        migrations.RenameField(
            model_name="parkingslot",
            old_name="slot_code",
            new_name="slot_name",
        ),
        migrations.AddConstraint(
            model_name="parkingslot",
            constraint=models.UniqueConstraint(
                fields=("zone_id", "slot_name"),
                name="uniq_slot_zone_slot_name",
            ),
        ),
    ]
