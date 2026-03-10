from django.db import migrations, models


def populate_current_location_names(apps, schema_editor):
    current_parking_view_model = apps.get_model("parking_query_service", "CurrentParkingView")
    parking_slot_model = apps.get_model("parking_command_service", "ParkingSlot")
    zone_model = apps.get_model("zone_service", "Zone")

    slot_names_by_id = {
        parking_slot.slot_id: parking_slot.slot_name
        for parking_slot in parking_slot_model.objects.all().only("slot_id", "slot_name")
    }
    zone_names_by_id = {
        zone.zone_id: zone.zone_name
        for zone in zone_model.objects.all().only("zone_id", "zone_name")
    }

    for current_parking_view in current_parking_view_model.objects.all().only(
        "vehicle_num",
        "zone_id",
        "slot_id",
    ):
        current_parking_view.zone_name = zone_names_by_id.get(current_parking_view.zone_id, "")
        current_parking_view.slot_name = slot_names_by_id.get(current_parking_view.slot_id, "")
        current_parking_view.save(update_fields=["zone_name", "slot_name"])


class Migration(migrations.Migration):

    dependencies = [
        ("parking_query_service", "0001_initial"),
        ("parking_command_service", "0002_rename_slot_code_to_slot_name"),
        ("zone_service", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="currentparkingview",
            name="zone_name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="currentparkingview",
            name="slot_name",
            field=models.CharField(default="", max_length=50),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=populate_current_location_names,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="currentparkingview",
            name="slot_id",
        ),
        migrations.RemoveField(
            model_name="currentparkingview",
            name="zone_id",
        ),
    ]
