#!/usr/bin/env python
"""
Start a scan using the API including reduced scope

To create an API token please go to the target settings in the user interface
and under "Integrations" create one.

Alternatively to perform actions as a regular user check the login workflow in
the create_target script.
"""
import requests
from urllib.parse import urljoin

token = input("API Token:")
headers = {"Authorization": "JWT {}".format(token)}

target_id = input("Target ID:")

api_base_url = "https://api.probely.com"
scan_now_endpoint = urljoin(api_base_url, "targets/{target_id}/scan_now/")

reduced_scopes = []
i = 1
while reduced_scope := input("Reduced scope #{} (leave empty to stop):".format(i)):
    reduced_scopes.append(reduced_scope)
    i += 1

response = requests.post(
    scan_now_endpoint.format(target_id=target_id),
    headers=headers,
    json={
        "reduced_scopes": [{"url": reduced_scope} for reduced_scope in reduced_scopes]
    },
)

