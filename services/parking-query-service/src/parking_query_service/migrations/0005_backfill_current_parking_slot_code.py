from django.db import migrations


def backfill_current_parking_slot_code(apps, schema_editor):
    current_parking_view_model = apps.get_model("parking_query_service", "CurrentParkingView")

    for current_parking_view in current_parking_view_model.objects.filter(
        slot_name__isnull=False,
    ).exclude(slot_name=""):
        if current_parking_view.slot_code:
            continue
        current_parking_view.slot_code = current_parking_view.slot_name
        current_parking_view.save(update_fields=["slot_code"])


class Migration(migrations.Migration):

    dependencies = [
        ("parking_query_service", "0004_add_history_id_to_current_parking_view"),
    ]

    operations = [
        migrations.RunPython(
            code=backfill_current_parking_slot_code,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
