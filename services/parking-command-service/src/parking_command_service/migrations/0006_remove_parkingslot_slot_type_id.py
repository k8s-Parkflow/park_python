from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("parking_command_service", "0005_add_history_slot_snapshot"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="parkingslot",
            name="slot_type_id",
        ),
    ]
