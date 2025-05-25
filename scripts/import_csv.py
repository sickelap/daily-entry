import csv
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


def import_entries(entries, url, email, password):
    if "http" not in url:
        url = f"http://{url}"
    with httpx.Client() as client:
        auth_payload = {"email": email, "password": password}
        response = client.post(f"{url}/token", json=auth_payload)
        assert response.status_code == 200
        print("Authenticated")
        headers = {"Token": response.json().get("Token")}
        response = client.post(f"{url}/import", json=entries, headers=headers)
        assert response.status_code == 200
        print(f"imported {len(entries)} entries")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    entries = parse_csv(args.csv)
    import_entries(entries, args.url, args.email, args.password)


if __name__ == "__main__":
    main()
