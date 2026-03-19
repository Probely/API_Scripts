#!/usr/bin/env python
"""
Export all findings to CSV format

Run: 

$ python3 findings_to_csv_v2.py --severity <OPTIONAL_SEVERITY (LOW|MEDIUM|HIGH|CRITICAL)> --state <OPTIONAL_STATE (FIXED|NOTFIXED|ACCEPTED|RETESTING|INVALID)> --search <OPTIONAL_SEARCH_STRING> --output <OUTPUT_FILE_PATH>

Multiple severities and states can be specified by repeating the argument:
$ python3 findings_to_csv_v2.py --severity HIGH --severity CRITICAL --state NOTFIXED --state ACCEPTED -o output.csv

"""
import argparse
import requests
import csv
from urllib.parse import urljoin, quote
from datetime import datetime

# Define the JWT or it will be asked when you run the script
jwt_token = None

length = 50

api_base_url = 'https://api.probely.com'
findings_endpoint = urljoin(api_base_url, "findings/")

SEVERITY_MAP = {
    10: 'LOW',
    20: 'MEDIUM',
    30: 'HIGH',
    40: 'CRITICAL'
}
SEVERITY_MAP_REVERSE = {v: k for k, v in SEVERITY_MAP.items()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--severity', help='Severity (supports multiple items)', required=False, action='append', choices=[
        'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
    parser.add_argument('--state', help='State (supports multiple items)', required=False, action='append', choices=[
        'FIXED', 'NOTFIXED', 'ACCEPTED', 'RETESTING', 'INVALID'])
    parser.add_argument('--search', help='Search string', required=False)
    parser.add_argument('-o', '--output', help='Output CSV file', type=argparse.FileType('w'), required=True)
    args = parser.parse_args()

    if jwt_token is None:
        token = input("API Token:")
    else:
        token = jwt_token

    if token is None or token == '':
        print('Error: JWT is required')
        return
    headers = {'Authorization': "JWT {}".format(token)}

    params = {
        'length': length,
        'ordering': '-last_found',
        'exclude': ['requests', 'evidence', 'scans', 'fix'],
    }
    if args.severity is not None:
        params['severity'] = [SEVERITY_MAP_REVERSE[s.upper()] for s in args.severity]
    if args.state is not None:
        params['state'] = [s.lower() for s in args.state]
    if args.search is not None:
        params['search'] = args.search

    csv_writer = csv.writer(
            args.output, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
    row = [
        'ID', 
        'Target ID', 
        'Target Name', 
        'Target URL', 
        'Finding', 
        'Method', 
        'Endpoint/Path', 
        'Parameter', 
        'Severity', 
        'State', 
        'Last Found', 
        'Snyk URL'
    ]
    csv_writer.writerow(row)

    current_page = 1
    total_pages = 1
    total_count = 0

    while current_page <= total_pages:
        params['page'] = current_page
        response_findings = requests.get(
            findings_endpoint,
            headers=headers,
            params=params
        )
        # print(f"DEBUG: Request URL: {response_findings.url}")
        response_findings.raise_for_status()
        response_json = response_findings.json()
        
        total_pages = response_json['page_total']
        total_count = response_json['count']
        findings_res = response_json['results']

        for finding in findings_res:
            row = [
                finding['id'],
                finding['target']['id'],
                finding['target']['site']['name'],
                finding['target']['site']['url'],
                finding['definition']['name'],
                finding['method'].upper() if finding.get('method') else '-',
                finding['path'],
                finding['parameter'] if finding.get('parameter') else 'NA',
                SEVERITY_MAP.get(finding['severity'], 'UNKNOWN'),
                finding['state'].upper(),
                datetime.strptime(finding['last_found'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S'),
                f'https://plus.probely.app/targets/{finding["target"]["id"]}/findings/{finding["id"]}'
            ]
            csv_writer.writerow(row)
            # print(row)

        current_page += 1

    print('Done')

if __name__ == '__main__':
    main()
