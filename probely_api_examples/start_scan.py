#!/usr/bin/env python
"""
Start a scan using the API

To create an API token please go to the target settings in the user interface
and under "Integrations" create one.

Alternatively to perform actions as a regular user check the login workflow in
the create_target script.
"""
import requests
from urllib.parse import urljoin

token = input("API Token:")
headers = {'Authorization': "JWT {}".formar(token)}

target_id = input("Target ID:")

api_base_url = "https://api.probely.com"
scan_now_endpoint = urljoin(api_base_url, "targets/{target_id}/scan_now/")

response = requests.post(scan_now_endpoint.format(target_id=target_id),
                         headers=headers)
