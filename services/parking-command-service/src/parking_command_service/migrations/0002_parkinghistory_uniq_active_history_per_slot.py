from django.db import migrations, models
from django.db.models import Count


def validate_unique_active_history_per_slot(apps, schema_editor):
    parking_history_model = apps.get_model("parking_command_service", "ParkingHistory")
    duplicates = list(
        parking_history_model.objects.filter(exit_at__isnull=True)
        .values("slot_id")
        .annotate(active_count=Count("history_id"))
        .filter(active_count__gt=1)
    )
    if duplicates:
        duplicated_slot_ids = ", ".join(str(row["slot_id"]) for row in duplicates[:10])
        raise RuntimeError(
            "PARKING_HISTORY에 동일 slot_id의 중복 활성 이력이 존재합니다. "
            f"중복 slot_id 예시: {duplicated_slot_ids}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("parking_command_service", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            code=validate_unique_active_history_per_slot,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="parkinghistory",
            constraint=models.UniqueConstraint(
                condition=models.Q(("exit_at__isnull", True)),
                fields=("slot",),
                name="uniq_active_history_per_slot",
            ),
        ),
    ]
