#!/usr/bin/env python

import csv
import requests
from urllib.parse import urljoin

recurrence_map = {
    '': 'N/A',
    'd': 'daily', 
    'w': 'weekly',
    'm': 'monthly',
    'q': 'quarterly'
}

def main():
    token = input("API Token:")
    csv_filename = input("CSV path to filename (default: ./scheduled.csv):")
    if csv_filename == "":
        csv_filename = "./scheduled.csv"

    headers = {"Authorization": "JWT {}".format(token)}

    api_base_url = "https://api.probely.com"
    targets_endpoint = urljoin(
        api_base_url, "targets/?include=compliance&length=10000"
    )

    response = requests.get(targets_endpoint, headers=headers)
    results = response.json()["results"]

    with open(csv_filename, "w") as csv_file:
        csv_writer = csv.writer(
            csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        csv_writer.writerow(["ID", "NAME", "URL", "NEXT SCAN DATE", "RECURRENCE"])
        for result in results:
            next_scan = result["next_scan"] if result.get("next_scan") else None
            if not next_scan:
                continue
            row = [
                result["id"],
                result["site"]["name"],
                result["site"]["url"],
                next_scan.get("date_time", ""),
                recurrence_map[next_scan.get("recurrence", "")]
            ]
            csv_writer.writerow(row)

if __name__ == '__main__':
    main()
