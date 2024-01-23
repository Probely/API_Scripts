#!/usr/bin/env python
"""
Export all findings in a target to DefectDojo JSON format

Choose "Generic Findings Import" under "Findings" > "Import Scan Results" > "Scan type"

Run: 

$ python3 findings_to_defectdojo.py -t '<TARGET_ID>' -o <OUTPUT_FILE_PATH>

"""
import argparse
import requests
import json
from urllib.parse import urljoin
from datetime import datetime

# Define the JWT or it will be asked when you run the script
jwt_token = None

api_base_url = 'https://api.probely.com'
target_endpoint = urljoin(api_base_url, "targets/{target}/")
finding_list_endpoint = urljoin(api_base_url, "targets/{target}/findings/")

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
    parser.add_argument('-t', '--target', help='Target id', required=True)
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

    response_target = requests.get(
        target_endpoint.format(target=args.target),
        headers=headers
    )
    response_target.raise_for_status()
    target_res = response_target.json()

    target_name = target_res['site'].get('name')
    target_url = target_res['site'].get('url')
    print(f'Exporting findings: {target_name} - {target_url}')

    # Findings
    response = requests.get(
        finding_list_endpoint.format(target=args.target),
        headers=headers,
        params={'length': 500}
    )
    response.raise_for_status()
    findings_res = response.json()['results']

    result = {
        'name': f'{target_name} - {target_url}',
        'findings': []
    }
    for finding in findings_res:
         result['findings'].append({
             'title': finding['definition']['name'],
             'unique_id_from_tool': finding['id'],
             'description': finding['definition']['desc'],
             'severity': map_severity(finding['severity']),
             'mitigation': finding['fix'],
             'date': datetime.strptime(finding['last_found'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d"),
             'cve': None,
             'cwe': None,
             'cvssv3': finding['cvss_vector'],
             'file_path': finding['path'],
             'endpoints': [finding['path']],
             'active': True if finding['state'] == 'notfixed' else False,
             'verified': True,
             'false_p': True if finding['state'] == 'invalid' else False
         })

    args.output.write(json.dumps(result, indent=2))
    print('Done')

if __name__ == '__main__':
    main()
