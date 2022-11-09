#!/usr/bin/env python

import csv
import requests
from urllib.parse import urljoin

def main():
    token = input("API Token:")
    csv_filename = input("CSV path to filename (default: ./targets.csv):")
    if csv_filename == "":
        csv_filename = "./targets.csv"

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
        for result in results:
            labels = result["labels"] if result.get("labels") else []
            labels_name = [label["name"] for label in labels]
            last_scan = result["last_scan"] if result.get("last_scan") else {}
            row = [
                result["id"],
                result["site"]["name"],
                result["site"]["url"],
                last_scan.get("status", ""),
                last_scan.get("completed", ""),
                *labels_name
            ]
            csv_writer.writerow(row)

if __name__ == '__main__':
    main()
