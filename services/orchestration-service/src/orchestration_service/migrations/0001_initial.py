from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SagaOperation",
            fields=[
                ("operation_id", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("saga_type", models.CharField(max_length=16)),
                ("status", models.CharField(max_length=32)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("current_step", models.CharField(blank=True, max_length=64, null=True)),
                ("history_id", models.BigIntegerField(blank=True, null=True)),
                ("vehicle_num", models.CharField(blank=True, max_length=20, null=True)),
                ("slot_id", models.BigIntegerField(blank=True, null=True)),
                ("last_error_code", models.CharField(blank=True, max_length=64, null=True)),
                ("last_error_message", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "SAGA_OPERATION",
            },
        ),
    ]

