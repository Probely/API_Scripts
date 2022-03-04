#!/usr/bin/env python
"""
Probe.ly currently does not support TOTP login, this script is presented as a
temporary work around.

To create an API token please go to the target settings in the user interface
and under "Integrations" create one. Afterwards please asks us to give the key
permissions to change the target settings (support@probely.com).

This code is python 3 only.
"""
import hashlib
import math
import time
import base64
from urllib.parse import urljoin

import hmac
import requests

probely_api_key = "CHANGE ME"
probely_target_id = "CHANGE ME"

probely_api_base_url = "https://api.probely.com"
probely_api_headers = {'Authorization': "JWT {}".format(probely_api_key)}


def login(username, password, totp_code):
    """Login skeleton function change this acording to your login"""
    response = requests.post("https://example.com/auth/login/",
                             data={
                                 'username': username,
                                 'password': password,
                                 'totp': totp_code,
                             })
    return response.json()['token']


def generate_totp(secret):
    time_step = 30
    time_counter = math.floor(int(time.time()) / time_step)
    time_counter = time_counter.to_bytes(8, byteorder='big')

    hasher = hmac.new(base64.b64decode(secret), time_counter, hashlib.sha1)
    hash_ = bytearray(hasher.digest())

    offset = hash_[-1] & 0xf
    num_digits = 6
    code = ((hash_[offset] & 0x7f) << 24 |
            (hash_[offset + 1] & 0xff) << 16 |
            (hash_[offset + 2] & 0xff) << 8 |
            (hash_[offset + 3] & 0xff))

    return str(code % 10 ** num_digits).zfill(num_digits)


if __name__ == '__main__':
    # Get username and password
    username = input("Login username:")
    password = input("Login password:")

    # Get TOTP secrert key
    secret = input("TOTP Secret (base 64 encoded):")
    secret = secret.encode('utf')
    totp_code = generate_totp(secret)

    # Get login token
    token = login(username, password, totp_code)

    # Get current site settings
    site_endpoint = urljoin(probely_api_base_url, "targets/{target_id}/site/")
    site_endpoint = site_endpoint.format(target_id=probely_target_id)
    response = requests.get(site_endpoint, headers=probely_api_headers)

    # Put or replace the token in a custom cookie
    cookies = response.json().get('cookies') or []
    cookies = {item['name']: item['value'] for item in cookies}
    cookies['session_id'] = token
    cookies = [{'name': k, 'value': v} for k, v in cookies.items()]

    # Put or replace token in a custom header
    headers = response.json().get('headers') or []
    headers = {item['name']: item['value'] for item in headers}
    headers['Authorization'] = token
    headers = [{'name': k, 'value': v} for k, v in headers.items()]

    # Update target site settings
    response = requests.patch(site_endpoint, headers=probely_api_headers,
                              json={
                                  'cookies': cookies,
                                  'headers': headers,
                              })

    # Start scan
    scan_now_endpoint = urljoin(probely_api_base_url,
                                "targets/{target_id}/scan_now/")
    scan_now_endpoint = scan_now_endpoint.format(target_id=probely_target_id)

    response = requests.post(scan_now_endpoint, headers=probely_api_headers)
