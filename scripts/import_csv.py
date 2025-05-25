import csv
import sys
import httpx
import argparse
from dateutil import parser


def parse_csv(file_path):
    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        entries = []
        for row in reader:
            timestamp = int(parser.parse(row[0], dayfirst=True).timestamp())
            entries.append(
                {
                    "timestamp": timestamp,
                    "value": float(row[1]),
                }
            )
        return entries


def import_entries(entries, metric, url, email, password):
    if "http" not in url:
        url = f"http://{url}"
    with httpx.Client() as client:
        auth_payload = {"email": email, "password": password}
        response = client.post(f"{url}/api/auth/login", json=auth_payload)
        assert response.status_code == 200
        print("Authenticated")

        headers = {"Token": response.json().get("Token")}

        response = client.get(f"{url}/api/metrics", headers=headers)
        metrics = response.json()
        metrics = [m["id"] for m in metrics if m["name"] == metric]
        if not metrics:
            print(f"unable to find metric {metric}")
            sys.exit()
        metric_id = metrics[0]

        response = client.post(
            f"{url}/api/metrics/{metric_id}/values", json=entries, headers=headers
        )
        assert response.status_code == 200
        print(f"imported {len(entries)} entries")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--metric", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    entries = parse_csv(args.csv)
    import_entries(entries, args.metric, args.url, args.email, args.password)


if __name__ == "__main__":
    main()
