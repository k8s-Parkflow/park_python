from django.db import models


class ParkingHistoryStatus(models.TextChoices):
    PARKED = "PARKED", "PARKED"
    EXITED = "EXITED", "EXITED"
