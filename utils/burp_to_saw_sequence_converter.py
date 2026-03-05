#!/usr/bin/env python
"""
Converts Burp Suite Navigation Recorder sequences to Snyk API&Web's sequence format.
"""
import argparse
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse


def extract_css_selector(event: Dict[str, Any]) -> Optional[str]:
    """
    Generate a CSS selector from Burp event data.
    Priority: id > name > placeholder > class > tag
    """
    tag = event.get('tagName', '').lower()
    if not tag:
        return None
    
    # ID
    element_id = event.get('id')
    if element_id:
        return f"#{element_id}"
    
    # Name attribute
    name = event.get('name')
    if name:
        return f"{tag}[name='{name}']"
    
    # Placeholder for inputs
    placeholder = event.get('placeholder')
    if placeholder and tag == 'input':
        return f"input[placeholder='{placeholder}']"
    
    # Class name
    class_name = event.get('className', '').strip()
    if class_name:
        classes = class_name.replace(' ', '.')
        return f"{tag}.{classes}"
    
    # href
    href = event.get('href')
    if href and tag == 'a':
        return f"a[href='{href}']"
    
    # Fallback: tag name
    return tag


def build_frame_hierarchy(burp_data: List[Dict]) -> Dict[int, Dict]:
    """
    Map of all frames
    """
    frame_map = {0: {'selector': None, 'parent': None}}
    
    start_event = burp_data[0] if burp_data and burp_data[0].get('eventType') == 'start' else None
    if not start_event:
        return frame_map

    iframes = start_event.get('iframes', [])
    for iframe in iframes:
        frame_id = iframe.get('frameId')
        attrs = iframe.get('attributes', {})

        iframe_id = attrs.get('id')
        if iframe_id:
            selector = f"iframe#{iframe_id}"
        elif attrs.get('src'):
            selector = f"iframe[src='{attrs.get('src')}']"
        elif iframe.get('xPath'):
            selector = iframe.get('xPath')
        else:
            selector = f"iframe:nth-child({iframe.get('iframeIndex', 0) + 1})"
        
        frame_map[frame_id] = {
            'selector': selector,
            'parent': 0,
            'url': attrs.get('src', '')
        }
    
    # Discover nested iframes
    frame_urls = {}
    for event in burp_data:
        frame_id = event.get('frameId', 0)
        if frame_id != 0 and event.get('isIframe'):
            event_url = event.get('url', '')
            if event_url:
                frame_urls[frame_id] = event_url
    
    # Collect all top-level iframe IDs for combined selector
    top_level_iframe_ids = [fid for fid in frame_map.keys() if fid != 0]
    
    for frame_id, url in frame_urls.items():
        if frame_id not in frame_map:
            parsed = urlparse(url)
            path = parsed.path

            if path:
                path_parts = path.rstrip('/').split('/')
                filename = path_parts[-1] if path_parts else path
                selector = f"iframe[src*='{filename}']"
            else:
                selector = "iframe"

            # Combine parent selector (all top-level iframes)
            frame_map[frame_id] = {
                'selector': selector,
                'parent': None,
                'url': url,
                'possible_parents': top_level_iframe_ids
            }
    
    return frame_map


def build_frame_selector(frame_map: Dict[int, Dict], frame_id: int) -> Optional[str]:
    """
    Build frame selector for iframes
    """
    if frame_id == 0:
        return None
    
    if frame_id not in frame_map:
        return None
    
    frame_info = frame_map.get(frame_id)
    if not frame_info:
        return None
    
    selector = frame_info.get('selector')
    if not selector:
        return None

    possible_parents = frame_info.get('possible_parents')
    if possible_parents:
        parent_selectors = []
        for parent_id in possible_parents:
            parent_info = frame_map.get(parent_id)
            if parent_info and parent_info.get('selector'):
                parent_selectors.append(parent_info.get('selector'))
        
        if parent_selectors:
            # Join selectors with " >>> "
            combined_parents = ','.join(parent_selectors)
            return f"{combined_parents} >>> {selector}"
        else:
            return selector

    selectors = [selector]
    current_frame_id = frame_info.get('parent')
    
    while current_frame_id is not None and current_frame_id != 0:
        parent_info = frame_map.get(current_frame_id)
        if not parent_info:
            break
        
        parent_selector = parent_info.get('selector')
        if parent_selector:
            selectors.append(parent_selector)
        
        current_frame_id = parent_info.get('parent')
    
    if len(selectors) == 1:
        return selectors[0]

    selectors.reverse()
    return ' >>> '.join(selectors)


def convert_burp_to_saw(burp_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert Burp Suite Navigation Recorder format to SAW sequence format.
    """
    saw_sequence = []
    
    if not burp_data or len(burp_data) == 0:
        raise Exception('No data in Burp recording file to be converted.')

    frame_map = build_frame_hierarchy(burp_data)
    
    for idx, event in enumerate(burp_data):
        event_type = event.get('eventType')
        
        # Skip the start item
        if event_type == 'start':
            continue
        
        # goto
        if event_type == 'goto':
            url = event.get('url')
            timestamp = event.get('timestamp', 0)
            window_width = 1800
            window_height = 1200

            if idx + 1 < len(burp_data):
                next_event = burp_data[idx + 1]
                window_width = next_event.get('windowInnerWidth', window_width)
                window_height = next_event.get('windowInnerHeight', window_height)
            
            saw_sequence.append({
                'type': 'goto',
                'urlType': 'force',
                'url': url,
                'timestamp': timestamp,
                'windowWidth': window_width,
                'windowHeight': window_height
            })
        
        # click
        elif event_type == 'click':
            css = extract_css_selector(event)
            xpath = event.get('xPath')
            timestamp = event.get('timestamp', 0)
            frame_id = event.get('frameId', 0)

            frame = build_frame_selector(frame_map, frame_id) if event.get('isIframe') else None
            
            # Value
            value = (event.get('value') or event.get('textContent') or '').strip()[:20].replace('\n', '')
            
            saw_sequence.append({
                'timestamp': timestamp,
                'type': 'click',
                'css': css,
                'xpath': xpath,
                'value': value,
                'frame': frame
            })
        
        # fill_value
        elif event_type == 'typing':
            css = extract_css_selector(event)
            xpath = event.get('xPath')
            typed_value = event.get('typedValue', '')
            timestamp = event.get('timestamp', 0)
            frame_id = event.get('frameId', 0)

            frame = build_frame_selector(frame_map, frame_id) if event.get('isIframe') else None
            
            saw_sequence.append({
                'timestamp': timestamp,
                'type': 'fill_value',
                'css': css,
                'xpath': xpath,
                'value': typed_value,
                'frame': frame
            })
        
        # dblclick
        elif event_type == 'dblclick':
            css = extract_css_selector(event)
            xpath = event.get('xPath')
            timestamp = event.get('timestamp', 0)
            frame_id = event.get('frameId', 0)
            
            frame = build_frame_selector(frame_map, frame_id) if event.get('isIframe') else None
            value = (event.get('value') or event.get('textContent') or '').strip()[:20].replace('\n', '')
            
            saw_sequence.append({
                'timestamp': timestamp,
                'type': 'dblclick',
                'css': css,
                'xpath': xpath,
                'value': value,
                'frame': frame
            })
        
        # skip userNavigate
        elif event_type == 'userNavigate':
            pass
        
        # Log unsupported steps
        else:
            print(f"Warning: Unsupported step '{event_type}' at index {idx}")
    
    return saw_sequence


def run():
    """
    Main
    """
    parser = argparse.ArgumentParser(
        description='Converts Burp Suite Navigation Recorder sequences to Snyk API&Web sequence format'
    )
    parser.add_argument(
        '-i', '--input',
        help='Input Burp recording JSON file',
        type=argparse.FileType('r'),
        required=True
    )
    parser.add_argument(
        '-o', '--output',
        help='Output Snyk API&Web sequence JSON file',
        type=argparse.FileType('w'),
        required=True
    )
    
    args = parser.parse_args()
    
    # Load Burp recording
    try:
        burp_data = json.load(args.input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        return 1
    
    # Convert to Snyk API&Web format
    try:
        saw_data = convert_burp_to_saw(burp_data)
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1
    
    json.dump(saw_data, args.output, indent=2)
    
    print(f"✓ Successfully converted {len(burp_data)} Burp steps to {len(saw_data)} Snyk API&Web")
    print(f"✓ Output written to: {args.output.name}")
    
    return 0


if __name__ == '__main__':
    run()
