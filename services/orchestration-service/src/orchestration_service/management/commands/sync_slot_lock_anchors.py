from __future__ import annotations

from django.core.management.base import BaseCommand

from park_py.service_databases import SERVICE_TO_DB_ALIAS
from parking_command_service.domains.parking_record.domain import ParkingSlot as CommandParkingSlot
from zone_service.models import ParkingSlot as ZoneParkingSlot


class Command(BaseCommand):
    help = "Sync zone-service parking slots into parking-command lock anchors."

    def handle(self, *args, **options):
        source_alias = SERVICE_TO_DB_ALIAS["zone"]
        target_alias = SERVICE_TO_DB_ALIAS["parking_command"]
        synced_count = 0

        for slot in ZoneParkingSlot.objects.using(source_alias).select_related("zone").order_by("slot_id"):
            CommandParkingSlot.objects.using(target_alias).update_or_create(
                slot_id=slot.slot_id,
                defaults={
                    "zone_id": slot.zone_id,
                    "slot_code": slot.slot_code,
                    "is_active": slot.is_active,
                },
            )
            synced_count += 1

        self.stdout.write(f"synced {synced_count} slot lock anchors")
