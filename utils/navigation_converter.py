#!/usr/bin/env python
"""
Converts between Probely's Navigation sequences and Selenium.

We can not guarantee that the conversion will be 100% compatible.
"""
import argparse
import json
import re
import uuid
import os
from time import time


items_not_supported = []


def getUUID():
    return str(uuid.uuid4())


def getSeleniumCssAndXPath(targets, target):
    css = None
    xpath = None
    for item in targets:
        if item[1] == 'css:finder':
            css = item[0].replace('css=', '')
        if item[1] == 'xpath:position':
            xpath = item[0].replace('xpath=', '')

    if css is None and target:
        if target.startswith('name='):
            css = '[{}]'.format(target)
        elif target.startswith('id='):
            css = '[{}]'.format(target)
    return (css, xpath)


def convertProbely2Selenium(data, inputFp, outputFp=None):
    name = os.path.basename(inputFp.name)
    obj = {
        'id': getUUID(),
        'version': '2.0',
        'name': name,
        'url': None,
        'tests': [{
            'id': getUUID(),
            'name': name,
            'commands': []
        }],
        'suites': [{
            'id': getUUID(),
            'name': 'Default Suite',
            'persistSession': False,
            'parallel': False,
            'timeout': 300,
            'tests': [getUUID()]
        }],
        'urls': [],
        'plugins': []
    }
    if len(data) == 0:
        raise Exception('No data in Probely recording file to be converted.')

    for idx, item in enumerate(data):
        if idx == 0:
            if item['type'] == 'goto':
                m = re.search('(https?://[^/]+)(/?.*)', item.get('url'))
                url_base = m.group(1)
                url_path = m.group(2)
                obj['url'] = url_base
                obj['urls'].append(url_base)
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'open',
                    'target': url_path,
                    'targets': [],
                    'value': ''
                })
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'setWindowSize',
                    'target': '{}x{}'.format(item.get('windowWidth', '1800'), item.get('windowHeight', '1200')),
                    'targets': [],
                    'value': ''
                })
            else:
                raise Exception('First item must be a "goto" with an URL')
        else:
            css = 'css={}'.format(item.get('css'))
            xpath = 'xpath={}'.format(item.get('xpath'))
            if item.get('type') == 'click' or item.get('type') == 'bclick':
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'click',
                    'target': css,
                    'targets': [
                        [css, 'css:finder'],
                        [xpath, 'xpath:position']
                    ],
                    'value': ''
                })
            elif item.get('type') == 'mouseover':
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'mouseOver',
                    'target': css,
                    'targets': [
                        [css, 'css:finder'],
                        [xpath, 'xpath:position']
                    ],
                    'value': ''
                })
            elif item.get('type') == 'fill_value':
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'type',
                    'target': css,
                    'targets': [
                        [css, 'css:finder'],
                        [xpath, 'xpath:position']
                    ],
                    'value': item.get('value', '')
                })
            elif item.get('type') == 'press_key' and item.get('value') == 13:
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'sendKeys',
                    'target': css,
                    'targets': [
                        [css, 'css:finder'],
                        [xpath, 'xpath:position']
                    ],
                    'value': '${KEY_ENTER}'
                })
            elif item.get('type') == 'change' and item.get('subtype') == 'select':
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'select',
                    'target': css,
                    'targets': [
                        [css, 'css:finder'],
                        [xpath, 'xpath:position']
                    ],
                    'value': 'value={}'.format(item.get('value', ''))
                })
            elif item.get('type') == 'change' and item.get('subtype') == 'check':
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'click',
                    'target': css,
                    'targets': [
                        [css, 'css:finder'],
                        [xpath, 'xpath:position']
                    ],
                    'value': ''
                })
            elif item.get('type') == 'dbclick':
                obj['tests'][0]['commands'].append({
                    'id': getUUID(),
                    'comment': '',
                    'command': 'doubleClick',
                    'target': css,
                    'targets': [
                        [css, 'css:finder'],
                        [xpath, 'xpath:position']
                    ],
                    'value': ''
                })
            else:
                items_not_supported.append('{} => {}'.format(idx, item.get('type')))

    return obj


def convertSelenium2Probely(data):
    obj = []
    timestamp = int(time()) * 1000
    tests_arr = data.get('tests')
    if tests_arr is None or len(tests_arr) == 0:
        raise Exception('No tests in Selenium file to be converted.')

    commands_arr = tests_arr[0].get('commands')
    if commands_arr is None or len(commands_arr) == 0:
        raise Exception('No commands in Selenium file to be converted.')

    url_base = data.get('url')
    # get first url
    first_command = commands_arr[0].get('command')
    second_command = commands_arr[1].get('command')
    url_path = commands_arr[0].get('target')
    dimensions = commands_arr[1].get('target')
    if first_command != 'open' or second_command != 'setWindowSize':
        raise Exception('Selenium first command must be "open" or second command must be "setWindowSize"')
    if url_path is None:
        raise Exception('Selenium first command must have a "target"')

    windowWidth = 1800
    windowHeight = 1200
    if dimensions:
        m = re.search('([0-9]+)x([0-9]+)', dimensions)
        windowWidth = int(m.group(1))
        windowHeight = int(m.group(2))

    obj.append({
        'type': 'goto',
        'urlType': 'force',
        'url': '{}{}'.format(url_base, url_path),
        'timestamp': timestamp,
        'windowWidth': windowWidth,
        'windowHeight': windowHeight
    })
    for idx, item in enumerate(commands_arr):
        if idx == 0 or idx == 1:
            continue
        else:
            css, xpath = getSeleniumCssAndXPath(item.get('targets'), item.get('target'))
            if css is None:
                continue
            if item.get('command') == 'click':
                timestamp += 1000
                obj.append({
                    'timestamp': timestamp,
                    'type': 'click',
                    'css': css,
                    'xpath': xpath,
                    'value': '',
                    'frame': None
                })
            elif item.get('command') == 'mouseOver':
                timestamp += 1000
                obj.append({
                    'timestamp': timestamp,
                    'type': 'mouseover',
                    'css': css,
                    'xpath': xpath,
                    'value': '',
                    'frame': None
                })
            elif item.get('command') == 'type':
                timestamp += 1000
                obj.append({
                    'timestamp': timestamp,
                    'type': 'fill_value',
                    'css': css,
                    'xpath': xpath,
                    'value': item.get('value', ''),
                    'frame': None
                })
            elif item.get('command') == 'sendKeys' and item.get('value') == '${KEY_ENTER}':
                timestamp += 1000
                obj.append({
                    'timestamp': timestamp,
                    'type': 'press_key',
                    'css': css,
                    'xpath': xpath,
                    'value': 13,
                    'frame': None
                })
            elif item.get('command') == 'select':
                timestamp += 1000
                select_value = item.get('value', '').replace('label=', '').replace('value=', '')
                obj.append({
                    'timestamp': timestamp,
                    'type': 'change',
                    'subtype': 'select',
                    'css': css,
                    'xpath': xpath,
                    'value': select_value,
                    'selected': 1,  # hardcoded, not correct
                    'frame': None
                })
            elif item.get('command') == 'doubleClick':
                timestamp += 1000
                obj.append({
                    'timestamp': timestamp,
                    'type': 'dblclick',
                    'css': css,
                    'xpath': xpath,
                    'value': '',
                    'frame': None
                })
            else:
                items_not_supported.append('{} => {}'.format(idx, item.get('command')))

    return obj


def run():
    parser = argparse.ArgumentParser(description='Converts Probely navigation sequences to selenium or selenium to Probely navigation sequences')
    parser.add_argument('-c', '--convert', help='<probely2selenium>/<selenium2probely>', choices=['probely2selenium', 'selenium2probely'])
    parser.add_argument('-i', '--input', help='Input file', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', help='Output file', type=argparse.FileType('w'))
    args = parser.parse_args()

    if args.convert == 'probely2selenium' and not args.output.name.endswith('.side'):
        raise Exception('Error: Selenium file name must use ".side" extension')

    input_data = json.load(args.input)

    if args.convert == 'probely2selenium':
        out_data = convertProbely2Selenium(input_data, args.input)
    elif args.convert == 'selenium2probely':
        out_data = convertSelenium2Probely(input_data)

    final_json = json.dumps(out_data, indent=2)
    args.output.write(final_json)

    if len(items_not_supported) > 0:
        print('Warning:')
        print('Items not supported/converted from positions: {}'.format(str(items_not_supported)))

    print('Done.')
    print('File converted to file: {}'.format(args.output.name))


if __name__ == '__main__':
    run()
