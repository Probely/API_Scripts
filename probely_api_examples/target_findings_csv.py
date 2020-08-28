#!/usr/bin/env python

import csv
import requests
from urllib.parse import urljoin


token = input("API Token:")
headers = {"Authorization": "JWT {}".format(token)}
target_id = input("Target ID:")

api_base_url = "https://api.probely.com"
findings_endpoint = urljoin(
    api_base_url, 
    "targets/{}/findings/?include=compliance&length=10".format(target_id)
)

response = requests.get(findings_endpoint, headers=headers)
paged_results = [response.json()["results"]]
page_total = response.json()["page_total"]

for page in range(1, page_total):
    response = requests.get(
        "".join([findings_endpoint, "&page={}".format(1 + page)]), headers=headers)
    paged_results.append(response.json()["results"])

with open("findings.csv", "w") as csv_file:
    csv_writer = csv.writer(
        csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
    )
    for page in paged_results:
        for result in page:
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
