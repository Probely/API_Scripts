#!/usr/bin/env python
"""
Script to copy (non-API) target with settings/integrations

This example is for python 3.6
"""

import requests

API_BASE_URL = "https://api.probely.com"
API_TOKEN = "" 
TARGET_ID = ""

if not API_TOKEN:
    print('Missing API_TOKEN')
    exit(1)

if not TARGET_ID:
    print('Missing TARGET_ID')
    exit(1)

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"JWT {API_TOKEN}",
    }
)

response = session.get(f"{API_BASE_URL}/targets/{TARGET_ID}")
assert response.status_code == 200
data = response.json()
for field in ('id', 'connected_target', 'highs', 'mediums', 'lows'):
    data.pop(field)

data['site']['name'] = data['site']['name'] + ' (Copy)' 
response = session.post(f"{API_BASE_URL}/targets/?skip_reachability_check=true", json=data)
assert response.status_code == 201, response.json()
copied_target_id = response.json()['id']

response = session.get(f"{API_BASE_URL}/integrations/")
assert response.status_code == 200

installed_integrations = [
        integration for integration, installed 
        in response.json()["installed"].items() if installed]

for integration in installed_integrations:
    response = session.get(
            f"{API_BASE_URL}/targets/{TARGET_ID}/"
            f"integrations/{integration.replace('_', '-')}/")
    assert response.status_code == 200

    data = response.json()

    response = session.patch(
            f"{API_BASE_URL}/targets/{copied_target_id}/"
            f"integrations/{integration.replace('_', '-')}/", 
            json=data)
    assert response.status_code == 200
