#!/usr/bin/env python
"""
Start a scan using the API selecting a scan profile

Currently there are 3 different scan profiles:
* normal -- default profile
* full -- does everything the default profile does and adds boolean based SQL
          injection tests
* safe -- doesn't use any content changing methods (no POST, DELETE, etc) and
          tries fewer payloads for SQL injection tests

"""
import requests
from urllib.parse import urljoin

token = input("API Token:")
headers = {'Authorization': "JWT {}".format(token)}

target_id = input("Target ID:")

api_base_url = "https://api.probely.com"
scan_now_endpoint = urljoin(api_base_url, "targets/{target_id}/scan_now/")

response = requests.post(scan_now_endpoint.format(target_id=target_id),
                         data={'scan_profile': 'safe'},
                         headers=headers)
