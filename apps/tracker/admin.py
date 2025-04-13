# myproject/admin.py
from django.contrib.admin import AdminSite


class TrackerAdminSite(AdminSite):
    pass
    # login_template = "admin_override/login.html"


admin_site = TrackerAdminSite(name="tracker")
