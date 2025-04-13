from datetime import datetime, timezone

from apps.core.models import User
from django.db import models
from django.db.models import CASCADE, ForeignKey, fields


class WeightEntry(models.Model):
    timestamp = fields.DateTimeField(default=datetime.now(timezone.utc))
    weight = fields.DecimalField(max_digits=5, decimal_places=1, blank=False)
    user = ForeignKey(User, on_delete=CASCADE, related_name="weight_entries")
