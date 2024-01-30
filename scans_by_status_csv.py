#!/usr/bin/env python
"""
Export all scans on every target with a specific status to CSV format

Run: 

$ python3 scans_by_state_csv.py -s <STATUS> -o <OUTPUT_FILE_PATH>

"""
import argparse
import requests
import csv
from urllib.parse import urljoin
from datetime import datetime

# Define the JWT or it will be asked when you run the script
jwt_token = None

api_base_url = 'https://api.probely.com'
scans_endpoint = urljoin(api_base_url, "scans/?length=1000&page=1&scan_profile_name=true&search=&status={status}&exclude=target_options")

def map_severity(probely_severity):
    if probely_severity == 10:
        return 'Low'
    elif probely_severity == 20:
        return 'Medium'
    elif probely_severity == 30:
        return 'High'
    else:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--status', help='Status', required=True, choices=[
        'started', 'paused', 'under_review', 'completed', 'failed', 'canceled'])
    parser.add_argument('-o', '--output', help='Output file', type=argparse.FileType('w'), required=True)
    args = parser.parse_args()

    if jwt_token is None:
        token = input("API Token:")
    else:
        token = jwt_token

    if token is None or token == '':
        print('Error: JWT is required')
        return
    headers = {'Authorization': "JWT {}".format(token)}

    response_scans = requests.get(
        scans_endpoint.format(status=args.status),
        headers=headers
    )
    response_scans.raise_for_status()
    scans_res = response_scans.json()['results']

    csv_writer = csv.writer(
            args.output, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
    row = ['Target ID', 'Target URL', 'Scan profile', 'Started', 'Completed', 'Status']
    csv_writer.writerow(row)
    for scan in scans_res:
        row = [
            scan['target']['id'],
            scan['target']['site']['url'],
            scan['scan_profile']['name'],
            datetime.strptime(scan['started'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S") if scan['started'] is not None else '',
            datetime.strptime(scan['completed'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S") if scan['completed'] is not None else '',
            scan['status']
        ]
        csv_writer.writerow(row)

    print('Done')

if __name__ == '__main__':
    main()
