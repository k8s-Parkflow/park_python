from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_query_service", "0002_add_slot_code_to_current_parking_view"),
        ("parking_query_service", "0002_replace_current_location_ids_with_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="currentparkingview",
            name="slot_code",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="currentparkingview",
            name="zone_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="currentparkingview",
            name="slot_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="currentparkingview",
            name="zone_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="currentparkingview",
            name="slot_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
