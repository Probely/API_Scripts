#!/usr/bin/env python
"""
Import postman environment file

To set postman environment for existing API target 
with Postman collection schema type

"""
import json
from urllib.parse import urljoin

import requests


token = input("API Token:")
headers = {"Authorization": "JWT {}".format(token)}
target_id = input("Target ID: ")
postman_env_file = input("Postman collection file: ")

with open(postman_env_file) as fd:
    postman_env = json.load(fd)

parsed_env = [
    {"name": value["key"], "value": value["value"]}
    for value in postman_env["values"]
    if value["enabled"]
]

api_base_url = "https://api.probely.com"
target_endpoint = urljoin(api_base_url, "targets/{target_id}/")

response = requests.get(target_endpoint.format(target_id=target_id), headers=headers)
assert response.status_code == 200, response.json()

custom_api_parameters = (
    response.json()["site"]["api_scan_settings"]["custom_api_parameters"] or []
)

updated_field_names = [entry["name"] for entry in parsed_env]

custom_api_parameters = [
    *[
        entry
        for entry in custom_api_parameters
        if entry["name"] not in updated_field_names
    ],
    *parsed_env,
]
response = requests.patch(
    target_endpoint.format(target_id=target_id),
    headers=headers,
    json={
        "site": {"api_scan_settings": {"custom_api_parameters": custom_api_parameters}}
    },
)
assert response.status_code == 200, response.json()
