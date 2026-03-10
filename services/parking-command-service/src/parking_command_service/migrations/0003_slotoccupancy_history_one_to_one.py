from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Count


def validate_unique_slot_occupancy_history(apps, schema_editor):
    slot_occupancy_model = apps.get_model("parking_command_service", "SlotOccupancy")
    duplicates = list(
        slot_occupancy_model.objects.filter(history_id__isnull=False)
        .values("history_id")
        .annotate(ref_count=Count("slot_id"))
        .filter(ref_count__gt=1)
    )
    if duplicates:
        duplicated_history_ids = ", ".join(str(row["history_id"]) for row in duplicates[:10])
        raise RuntimeError(
            "SLOT_OCCUPANCY에 중복 history_id 참조가 존재합니다. "
            f"중복 history_id 예시: {duplicated_history_ids}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("parking_command_service", "0002_parkinghistory_uniq_active_history_per_slot"),
    ]

    operations = [
        migrations.RunPython(
            code=validate_unique_slot_occupancy_history,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="slotoccupancy",
            name="history",
            field=models.OneToOneField(
                blank=True,
                db_column="history_id",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="slot_occupancy",
                to="parking_command_service.parkinghistory",
            ),
        ),
    ]
