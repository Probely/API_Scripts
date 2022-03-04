#!/usr/bin/env python
"""
Create a scanning agent using the API and assign it to a target

This action may only be performed by users with the required permissions.
Target API keys will not be able to create targets.

At the moment scanning agents are only available for Probely + accounts.
If you require this feature please contact our support at
support@probely.com.

This example is for python 3.5
"""
import getpass
from urllib.parse import urljoin

import requests

username = input("Username: ")
password = getpass.getpass()

api_base_url = "https://api.probely.com"
auth_endpoint = urljoin(api_base_url, "/enterprise/auth/obtain/")
scanning_agent_endpoint = urljoin(api_base_url, "/scanning-agents/")
target_endpoint = urljoin(api_base_url, "/targets/")

# Get login token
response = requests.post(
    auth_endpoint, json={"username": username, "password": password}
)
headers = {"Authorization": "JWT {}".format(response.json()["token"])}

# Create scanning agent
response = requests.post(
    scanning_agent_endpoint, headers=headers, json={"name": "Agent example"},
)
agent_id = response.json()["id"]

# Create target with agent assigned
target_url = "http://ox-test1.westeurope.cloudapp.azure.com"
response = requests.post(
    target_endpoint,
    headers=headers,
    json={
        "site": {"name": "Example", "url": target_url},
        "scanning_agent": {"id": agent_id},
    },
)
target_id = response.json()["id"]

# Unassign agent
response = requests.patch(
    "{}{}/".format(target_endpoint, target_id),
    headers=headers,
    json={"scanning_agent": {"id": None}},
)

# Reassign agent
response = requests.patch(
    "{}{}/".format(target_endpoint, target_id),
    headers=headers,
    json={"scanning_agent": {"id": agent_id}},
)
