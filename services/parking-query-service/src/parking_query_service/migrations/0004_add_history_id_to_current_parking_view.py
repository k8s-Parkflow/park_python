from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_query_service", "0003_merge_proj22_main_current_parking_view"),
    ]

    operations = [
        migrations.AddField(
            model_name="currentparkingview",
            name="history_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
