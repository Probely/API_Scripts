#!/usr/bin/env python

import csv
import requests
from urllib.parse import urljoin


token = input("API Token:")
headers = {"Authorization": "JWT {}".format(token)}

api_base_url = "https://api.qa.probely.com"
findings_endpoint = urljoin(
    api_base_url, "findings/?include=compliance&length=10000"
)

response = requests.get(findings_endpoint, headers=headers)
results = response.json()["results"]
with open("findings.csv", "w") as csv_file:
    csv_writer = csv.writer(
        csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
    )
    for result in results:
        labels = result["labels"] if result.get("labels") else []
        labels_name = [label["name"] for label in labels]
        row = [
            result["id"],
            result["severity"],
            result["definition"]["name"],
            result["url"],
            result["last_found"],
            result["state"],
            result.get("assignee")["email"] if result.get("assignee") else " ",
            *labels_name
        ]
        csv_writer.writerow(row)
