import csv

from dateutil import parser
from django.apps import apps
from django.core.management.base import BaseCommand

WeightEntry = apps.get_model("tracker.WeightEntry")
User = apps.get_model("core.User")


class Command(BaseCommand):
    help = "Import historic data from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to CSV file")
        parser.add_argument("user_id", type=int, help="User to import data for")

    def handle(self, *_, **options):
        user_id = options["user_id"]
        with open(options["csv_file"], newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                timestamp = parser.parse(row[0], dayfirst=True)
                weight = row[1]
                user = User.objects.filter(id=user_id).first()
                self.stdout.write(f"{timestamp}, {weight}")
                WeightEntry.objects.create(
                    timestamp=timestamp, weight=weight, user=user
                )
        self.stdout.write("Import complete.")
