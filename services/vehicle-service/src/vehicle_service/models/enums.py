from django.db import models


class VehicleType(models.TextChoices):
    General = "GENERAL", "GENERAL"
    EV = "EV", "EV"
    Disabled = "DISABLED", "DISABLED"
