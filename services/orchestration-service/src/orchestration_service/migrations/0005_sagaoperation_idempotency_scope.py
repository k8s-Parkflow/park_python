from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("orchestration_service", "0004_sagaoperation_result_snapshots"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sagaoperation",
            name="idempotency_key",
            field=models.CharField(max_length=128),
        ),
        migrations.AddConstraint(
            model_name="sagaoperation",
            constraint=models.UniqueConstraint(
                fields=("saga_type", "idempotency_key"),
                name="uniq_saga_operation_type_idempotency_key",
            ),
        ),
    ]
