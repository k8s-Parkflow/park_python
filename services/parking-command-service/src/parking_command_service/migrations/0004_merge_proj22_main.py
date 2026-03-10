from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("parking_command_service", "0002_rename_slot_code_to_slot_name"),
        ("parking_command_service", "0003_slotoccupancy_history_one_to_one"),
    ]

    operations = []
