import logging
from datetime import date

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import csrf_protect
from django.shortcuts import render

WeightEntry = apps.get_model("tracker.WeightEntry")
logger = logging.getLogger(__name__)


def get_last_entry_value(request):
    try:
        last_entry = WeightEntry.objects.filter(user=request.user).latest("timestamp")
        return last_entry.weight
    except Exception as e:
        logger.error(str(e))
        return 100


def get_todays_entries(request):
    try:
        return WeightEntry.objects.filter(
            user=request.user, timestamp__date=date.today()
        ).order_by("-timestamp")
    except Exception as e:
        logger.error(str(e))
        return []


def create_entry(request):
    if request.method == "POST":
        weight = float(request.POST.get("weight", None))
        if not weight:
            raise Exception(f"invalid weight {weight}")
        WeightEntry.objects.create(user=request.user, weight=weight)


def remove_entry(request):
    if request.method == "POST":
        id = float(request.POST.get("id", None))
        if not id:
            raise Exception(f"invalid id: {id}")
        WeightEntry.objects.filter(user=request.user, id=id).delete()


@login_required
def index(request):
    return render(
        request,
        "tracker/index.html",
        {
            "entries": get_todays_entries(request),
            "last_value": get_last_entry_value(request),
        },
    )


@login_required
@csrf_protect
def create_weight_entry(request):
    create_entry(request)
    return render(
        request,
        "components/todays_entries.html",
        {"entries": get_todays_entries(request)},
    )


@login_required
@csrf_protect
def remove_weight_entry(request):
    remove_entry(request)
    return render(
        request,
        "components/todays_entries.html",
        {"entries": get_todays_entries(request)},
    )
