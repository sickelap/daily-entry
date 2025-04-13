from datetime import date

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import csrf_protect
from django.shortcuts import render

WeightEntry = apps.get_model("tracker.WeightEntry")


def get_last_entry_value(request):
    last_entry = WeightEntry.objects.filter(user=request.user).latest("timestamp")
    return last_entry.weight or 100


def get_todays_entries(request):
    return WeightEntry.objects.filter(
        user=request.user, timestamp__date=date.today()
    ).order_by("-timestamp")


def create_entry(request):
    if request.method == "POST":
        weight = float(request.POST.get("weight", None))
        if not weight:
            raise Exception()
        WeightEntry.objects.create(user=request.user, weight=weight)


def remove_entry(request):
    if request.method == "POST":
        id = float(request.POST.get("id", None))
        if not id:
            raise Exception()
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
    try:
        create_entry(request)
    except Exception:
        return render(request, "unable to add entry")

    return render(
        request,
        "components/todays_entries.html",
        {"entries": get_todays_entries(request)},
    )


@login_required
@csrf_protect
def remove_weight_entry(request):
    try:
        remove_entry(request)
    except Exception:
        return render(request, f"unable to remove entry")

    return render(
        request,
        "components/todays_entries.html",
        {"entries": get_todays_entries(request)},
    )
