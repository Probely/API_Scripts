#!/usr/bin/env python
"""
Output CVSS score and vector for all findings in a target


This example is for python 3.5
"""
import argparse

import requests
from urllib.parse import urljoin


api_base_url = "https://api.probely.com"
finding_list_endpoint = urljoin(api_base_url, "targets/{target}/findings/")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target id")
    args = parser.parse_args()

    token = input("API Token:")
    headers = {'Authorization': "JWT {}".format(token)}

    # Findings
    response = requests.get(
        finding_list_endpoint.format(target=args.target),
        headers=headers,
        params={'length': 100}
    )
    response.raise_for_status()
    findings = response.json()['results']

    print('Id, CVSS Score, CVSS vector')
    for finding in findings:
        if finding['cvss_score']:
            print("%s, %s, %s" % (finding['id'],
                                  finding['cvss_score'],
                                  finding['cvss_vector']))
