#!/usr/bin/env python
"""
Export all discovery assets with a specific optional score to CSV format

Run: 

$ python3 discovery_assets_to_csv.py -s <OPTIONAL_SCORE> -o <OUTPUT_FILE_PATH>

"""
import argparse
import requests
import csv
from urllib.parse import urljoin, quote
from datetime import datetime

# Define the JWT or it will be asked when you run the script
jwt_token = None

api_base_url = 'https://api.probely.com'
discovery_assets_endpoint = urljoin(api_base_url, "discovery/assets/?length=10000&page=1&ordering=-last_seen&{score_str}")

def map_risk(probely_risk):
    if probely_risk == 10:
        return 'Low'
    elif probely_risk == 20:
        return 'Normal'
    elif probely_risk == 30:
        return 'High'
    else:
        return 'NA'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--score', help='Score', required=False, choices=[
        'A+', 'A', 'B', 'C', 'D', 'E', 'F', 'R', 'NA'])
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

    score_str = ''
    if args.score is not None:
        score_str = f'score={quote(args.score)}'

    response_assets = requests.get(
        discovery_assets_endpoint.format(score_str=score_str),
        headers=headers
    )
    response_assets.raise_for_status()
    assets_res = response_assets.json()['results']

    csv_writer = csv.writer(
            args.output, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
    row = ['ID', 'Name', 'URL', 'Type', 'Last Seen', 'Risk', 'Score', 'State']
    csv_writer.writerow(row)
    for asset in assets_res:
        row = [
            asset['id'],
            asset['name'],
            asset['url'],
            asset['type'],
            datetime.strptime(asset['last_seen'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S"),
            map_risk(asset['risk']),
            asset['score'],
            asset['state'],
        ]
        csv_writer.writerow(row)

    print('Done')

if __name__ == '__main__':
    main()
