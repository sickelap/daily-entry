from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path(
        "fragments/create_weight_entry",
        views.create_weight_entry,
        name="create-weight-entry",
    ),
    path(
        "fragments/remove_weight_entry",
        views.remove_weight_entry,
        name="remove-weight-entry",
    ),
]
