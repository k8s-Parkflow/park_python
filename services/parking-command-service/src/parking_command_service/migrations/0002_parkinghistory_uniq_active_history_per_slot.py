from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_command_service", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="parkinghistory",
            constraint=models.UniqueConstraint(
                condition=models.Q(("exit_at__isnull", True)),
                fields=("slot",),
                name="uniq_active_history_per_slot",
            ),
        ),
    ]
