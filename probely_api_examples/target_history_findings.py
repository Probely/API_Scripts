#!/usr/bin/env python
"""
Create an overview file of the target finding history


This example is for python 3.5
"""
import argparse
import csv
import getpass
from collections import OrderedDict

import requests
from urllib.parse import urljoin

api_base_url = "https://api.probely.com"
auth_endpoint = urljoin(api_base_url, "auth-obtain/")
target_detail_endpoint = urljoin(api_base_url, "targets/{target}/")
scan_list_endpoint = urljoin(api_base_url, "targets/{target}/scans/")
finding_list_endpoint = urljoin(api_base_url, "targets/{target}/findings/")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target id")
    parser.add_argument("output", help="Output file")
    parser.add_argument('--limit',
                        help='Limit number of assessments (default: 5)',
                        default=5,
                        type=int)
    args = parser.parse_args()

    username = input("Username: ")
    password = getpass.getpass()

    # Get login token
    response = requests.post(auth_endpoint,
                             data={'username': username, 'password': password})
    response.raise_for_status()
    token = response.json()['token']
    headers = {'Authorization': "JWT {}".format(token)}

    # Scans
    response = requests.get(
        scan_list_endpoint.format(target=args.target),
        headers=headers,
        params={'ordering': '-started', 'length': args.limit}
        )
    response.raise_for_status()
    scans = response.json()['results']
    extra = response.json()
    extra.pop('results')

    # Findings
    response = requests.get(
        finding_list_endpoint.format(target=args.target),
        headers=headers,
        params={'length': 100}
        )
    response.raise_for_status()
    page_total = response.json()['page_total']
    findings = response.json()['results']
    extra = response.json()
    extra.pop('results')

    scan_map = OrderedDict(((scan['id'], idx)
                            for idx, scan in enumerate(scans)))
    scan_dict = OrderedDict(((scan['id'], False) for scan in scans))

    with open(args.output, 'w', newline='') as handler:
        fieldnames = ['finding_id', 'ovi'] + list(scan_map.keys())
        writer = csv.DictWriter(handler, fieldnames=fieldnames)
        writer.writeheader()

        for finding in findings:
            present = scan_dict.copy()
            for scan_id in finding['scans']:
                if scan_id in present:
                    present[scan_id] = True

            row = OrderedDict(
                [('finding_id', finding['id']),
                 ('ovi', finding['definition']['name'])]
                + list(present.items())
            )
            writer.writerow(row)

