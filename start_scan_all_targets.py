#!/usr/bin/env python

import requests
from urllib.parse import urljoin

def main():
    token = input("API Token:")

    headers = {"Authorization": "JWT {}".format(token)}

    api_base_url = "https://api.probely.com"
    targets_endpoint = urljoin(
        api_base_url, "targets/?include=compliance&length=10000"
    )

    response = requests.get(targets_endpoint, headers=headers)
    results = None
    try:
        results = response.json()["results"]
    except:
        print('Failed getting the list of targets, confirm if the API Token is correct.')
        return

    for result in results:
        target_id = result.get("id", None)
        if target_id is not None:
            target_name = result["site"]["name"]
            target_url = result["site"]["url"]

            scan_now_endpoint = urljoin(api_base_url, "targets/{target_id}/scan_now/")

            try:
                scan_response = requests.post(scan_now_endpoint.format(target_id=target_id),
                            headers=headers)
                scan_result = scan_response.json()

                if "error" in scan_result:
                    error = scan_result["error"]
                    print(f"Error: {error} => ({target_name}) {target_url}")
                elif "id" not in scan_result:
                    print(f"Error: Starting scan on ({target_name}) {target_url} failed")
                else:
                    print(f"Started scan on ({target_name}) {target_url}")
            except:
                print(f"Failed starting scan on ({target_name}) {target_url}")


if __name__ == '__main__':
    main()
