from django.contrib import admin

from .models import WeightEntry

admin.site.site_header = "Admin"
admin.site.site_title = "Weight Tracker"
admin.site.index_title = "Dashboard"


@admin.register(WeightEntry)
class WeighEntryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "weight", "user")
