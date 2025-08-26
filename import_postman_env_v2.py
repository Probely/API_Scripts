#!/usr/bin/env python
"""
Import postman environment file - V2

To set postman environment for existing API target 
with Postman collection schema type

"""
import argparse
import json
from urllib.parse import urljoin
import requests

# Define the JWT or it will be asked when you run the script
jwt_token = None

api_base_url = 'https://api.probely.com'

def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--target', help='Target ID', required=True)
    parser.add_argument('-e', '--env-file', help='Environment Variables file', type=argparse.FileType('r'), required=True)
    parser.add_argument('--ignore-enabled', help='Ignore enabled property', action='store_true', required=False)
    parser.add_argument('--null-to', help='Converts null values to defined value.\n--null-to "null": converts null values to string "null"\n--null-to "": converts null values to empty string (default)', default="", required=False)
    parser.add_argument('--include-empty', help='Include empty values', action='store_true', required=False)
    args = parser.parse_args()

    if jwt_token is None:
        token = input("API Token:")
    else:
        token = jwt_token

    if token is None or token == '':
        print('Error: JWT is required')
        return
    headers = {'Authorization': "JWT {}".format(token)}
    
    target_id = args.target

    postman_env = json.load(args.env_file)

    if "values" not in postman_env or "values" in postman_env and len(postman_env["values"]) == 0:
        print("No values on Environment Variables file")
        return

    parsed_env = []

    for item in postman_env["values"]:

        if "key" not in item or "value" not in item:
            continue
            
        if args.ignore_enabled == False:
            if not "enabled" in item or not item["enabled"]:
                continue

        if "value" in item and item["value"] is None:
            item["value"] = args.null_to

        if "value" in item and item["value"] == "" and args.include_empty == False:
            continue

        parsed_env.append({
            "name": item["key"],
            "value": item["value"]
        })

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

if __name__ == '__main__':
    main()
    print("Done.")
