from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingHistory',
            fields=[
                ('history_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vehicle_num', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('PARKED', 'PARKED'), ('EXITED', 'EXITED')], default='PARKED', max_length=16)),
                ('entry_at', models.DateTimeField()),
                ('exit_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'PARKING_HISTORY',
            },
        ),
        migrations.CreateModel(
            name='ParkingSlot',
            fields=[
                ('slot_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('zone_id', models.BigIntegerField()),
                ('slot_type_id', models.BigIntegerField()),
                ('slot_code', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'PARKING_SLOT',
            },
        ),
        migrations.CreateModel(
            name='SlotOccupancy',
            fields=[
                ('slot', models.OneToOneField(db_column='slot_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='occupancy', serialize=False, to='parking_command_service.parkingslot')),
                ('occupied', models.BooleanField(default=False)),
                ('vehicle_num', models.CharField(blank=True, max_length=20, null=True)),
                ('occupied_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'SLOT_OCCUPANCY',
            },
        ),
        migrations.AddConstraint(
            model_name='parkingslot',
            constraint=models.UniqueConstraint(fields=('zone_id', 'slot_code'), name='uniq_slot_zone_slot_code'),
        ),
        migrations.AddField(
            model_name='parkinghistory',
            name='slot',
            field=models.ForeignKey(db_column='slot_id', on_delete=django.db.models.deletion.PROTECT, related_name='parking_histories', to='parking_command_service.parkingslot'),
        ),
        migrations.AddField(
            model_name='slotoccupancy',
            name='history',
            field=models.ForeignKey(blank=True, db_column='history_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='slot_occupancies', to='parking_command_service.parkinghistory'),
        ),
        migrations.AddIndex(
            model_name='parkinghistory',
            index=models.Index(fields=['slot', 'entry_at'], name='idx_history_slot_entry'),
        ),
        migrations.AddIndex(
            model_name='parkinghistory',
            index=models.Index(fields=['vehicle_num', 'exit_at'], name='idx_history_vehicle_exit'),
        ),
        migrations.AddConstraint(
            model_name='parkinghistory',
            constraint=models.UniqueConstraint(condition=models.Q(('exit_at__isnull', True)), fields=('vehicle_num',), name='uniq_active_history_per_vehicle'),
        ),
        migrations.AddConstraint(
            model_name='slotoccupancy',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('occupied', True), ('vehicle_num__isnull', False), ('history__isnull', False), ('occupied_at__isnull', False)), models.Q(('occupied', False), ('vehicle_num__isnull', True), ('history__isnull', True), ('occupied_at__isnull', True)), _connector='OR'), name='slot_occupancy_consistency'),
        ),
    ]
