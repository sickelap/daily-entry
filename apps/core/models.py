from zoneinfo import available_timezones

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

TIMEZONE_CHOICES = [(tz, tz) for tz in available_timezones()]


class User(AbstractUser):
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    timezone = models.CharField(
        max_length=50, choices=TIMEZONE_CHOICES, default=settings.TIME_ZONE
    )
