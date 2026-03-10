from django.db import migrations, models


def backfill_history_slot_snapshot(apps, schema_editor):
    ParkingHistory = apps.get_model("parking_command_service", "ParkingHistory")

    for history in ParkingHistory.objects.select_related("slot").all():
        if history.slot_id is None or history.slot is None:
            continue
        slot_code = getattr(history.slot, "slot_code", "") or getattr(history.slot, "slot_name", "")
        slot_type_id = getattr(history.slot, "slot_type_id", 0)
        ParkingHistory.objects.filter(history_id=history.history_id).update(
            zone_id=history.slot.zone_id,
            slot_type_id=slot_type_id,
            slot_code=slot_code,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("parking_command_service", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="parkinghistory",
            name="zone_id",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="parkinghistory",
            name="slot_type_id",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="parkinghistory",
            name="slot_code",
            field=models.CharField(db_column="slot_name", default="", max_length=50),
        ),
        migrations.RunPython(backfill_history_slot_snapshot, migrations.RunPython.noop),
    ]
