#!/usr/bin/env python

import csv
import requests
from urllib.parse import urljoin


token = input("API Token:")
headers = {"Authorization": "JWT {}".format(token)}

api_base_url = "https://api.probely.com"
findings_endpoint = urljoin(
    api_base_url, "findings/?include=compliance&length=10000"
)

definitions_endpoint = urljoin(
    api_base_url, "definitions/{definition_id}"
)

definition_cache = dict()


def get_findings():
    response = requests.get(findings_endpoint, headers=headers)
    return response.json()["results"]


def get_definition(defintion_id):
    if definition_id in definition_cache.keys():
        return definition_cache[defintion_id]

    response = requests.get(definitions_endpoint.format(
        defintion_id=definition_id), headers=headers)

    definition_cache[definition_id] = response.json()
    return response.json()


with open("findings.csv", "w") as csv_file:
    csv_writer = csv.writer(
        csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
    )
    csv_writer.writerow(
        "id", "severity", "cwe_id", "definition_name", "url", "last_found", "state", "assignee", "labels"
    )

    for result in results:
        definition = get_definition(result.get("id"))

        labels = result.get("labels", [])
        labels_name = [label["name"] for label in labels]
        row = [
            result["id"],
            result["severity"],
            definition["cwe_id"],
            result["definition"]["name"],
            result["url"],
            result["last_found"],
            result["state"],
            result.get("assignee", {}).get("email", " "),
            *labels_name
        ]
        csv_writer.writerow(row)
