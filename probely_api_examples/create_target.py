"""
Create a target using the API

This action may only be performed by users with the required permissions,
target API keys will no be able to create targets.

At the moment only the user that created the account is able to create targets.
If you require enabling other users please contact our support at
support@probely.com.

This example is for python 3.5
"""
import requests
from urllib.parse import urljoin

username = input("Username:")
password = input("Password:")

api_base_url = "https://api.probely.com"
auth_endpoint = urljoin(api_base_url, "auth-obtain/")
target_endpoint = urljoin(api_base_url, "targets/")
site_endpoint = urljoin(api_base_url, "targets/{target_id}/site/")
verification_endpoint = urljoin(api_base_url,
                                "targets/{target_id}/site/verify/")

# Get login token
response = requests.post(auth_endpoint,
                         data={'username': username, 'password': password})
token = response.json()['token']
headers = {'Authorization': "JWT {}".formar(token)}

# Create target
response = requests.post(target_endpoint, headers=headers)
target_id = response.json()['id']

# Input target name and url
response = requests.put(
    site_endpoint.format(target_id=target_id), headers=headers,
    data={
        'name': "Example",
        'url': "http://ox-test1.westeurope.cloudapp.azure.com",
    })
verification_token = response.json()['verification_token']

# Verify the site
# MANUAL STEP!!
# Site verification must be done either by file or DNS record
verification_type = "dns"

response = requests.post(
    verification_endpoint.format(target_id=target_id), headers=headers,
    data={'type': verification_type})

if not response.json()['site']['verified']:
    if verification_type == "dns":
        print("Add the following DNS TXT record to your target's (sub)domain:")
        print("Probe.ly={verification_token}".format(
            verification_token=verification_token))

    elif verification_type == "file":
        print("Add the following file your target's root path:")
        print("Filename: {verification_token}.txt".format(
              verification_token=verification_token))
        print("File content: Probe.ly")

# Add site to subscription

# Trial
# During your trial period do not worry the first target you scan
# will be automatically added to your subscription (trials usually allow only
# one site).

# Site Pool
# Sites are added to your subscription as soon as they are created.

# On Demand
# You are paying per target added to your subscription.
# Please go to the user interface and in the user drop down (top right corner)
# select account. Afterwards click "Subscribe to out plans" and follow the
# regular billing flow to add the target.
# We do not recommend adding targets to the subscription using the API (since
# it incurs a payment) but if you really want to don't be shy and ask us.
