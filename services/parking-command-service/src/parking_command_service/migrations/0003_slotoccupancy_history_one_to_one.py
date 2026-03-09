from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parking_command_service", "0002_parkinghistory_uniq_active_history_per_slot"),
    ]

    operations = [
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
