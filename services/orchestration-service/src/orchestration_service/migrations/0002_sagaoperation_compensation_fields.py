from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orchestration_service", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sagaoperation",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sagaoperation",
            name="compensation_attempts",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="sagaoperation",
            name="expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sagaoperation",
            name="next_retry_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
