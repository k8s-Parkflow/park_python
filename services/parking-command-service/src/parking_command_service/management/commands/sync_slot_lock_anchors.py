from __future__ import annotations

from django.core.management.base import BaseCommand

from parking_command_service.clients.grpc.zone import ZoneGrpcClient
from parking_command_service.domains.parking_record.domain import ParkingSlot


class Command(BaseCommand):
    help = "Sync zone-service parking slots into parking-command lock anchors."

    def handle(self, *args, **options):
        zone_client = ZoneGrpcClient()
        synced_count = 0

        for slot in zone_client.list_parking_slots():
            ParkingSlot.objects.update_or_create(
                slot_id=slot["slot_id"],
                defaults={
                    "zone_id": slot["zone_id"],
                    "slot_code": slot["slot_code"],
                    "is_active": slot["is_active"],
                },
            )
            synced_count += 1

        self.stdout.write(f"synced {synced_count} slot lock anchors")
