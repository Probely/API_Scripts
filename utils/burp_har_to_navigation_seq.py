#!/usr/bin/env python
"""
Converts Burp or HAR files to Probely's Navigation sequences.
"""
import argparse
import json

def run():
    parser = argparse.ArgumentParser(description='Converts Burp or HAR files to Probely\'s navigation sequences')
    parser.add_argument('-t', '--type', help='burp/har', choices=['burp', 'har'], required=True)
    parser.add_argument('-i', '--input', help='Input file', type=argparse.FileType('r'), required=True)
    parser.add_argument('-o', '--output', help='Output file', type=argparse.FileType('w'), required=True)
    parser.add_argument('--crawl', help='Crawl the requests', default=True, action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    with args.input as file:
        input_data = file.read()

    if args.type == 'burp':
        out_data = [{
            'file_type': 'burp',
            'crawl': args.crawl,
            'file_data': input_data
        }]
    elif args.type == 'har':
        out_data = [{
            'file_type': 'har',
            'crawl': args.crawl,
            'file_data': input_data
        }]

    final_json = json.dumps(out_data, indent=2)
    args.output.write(final_json)

    print('Done.')
    print('File converted to file: {}'.format(args.output.name))


if __name__ == '__main__':
    run()
