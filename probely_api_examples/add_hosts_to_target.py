#!/usr/bin/env python
"""
Add hosts to an existing target
"""
import requests
from urllib.parse import urljoin

token = input("API Token: ")
target_id = input("Target ID: ")

headers = {
    'Authorization': "JWT {}".format(token),
    'Content-Type': "application/json",
}
api_base_url = "https://api.probely.com"
endpoint = urljoin(api_base_url, "targets/{target_id}/assets/")

response = requests.post(
    endpoint.format(target_id=target_id),
    headers=headers,
    json={'host': 'example.com'})

print(response.request.headers)

if response.status_code == 200:
    print('\nSUCCESS')

else:
    print('\n[%s]\n%s' %(response.status_code, response.text))
