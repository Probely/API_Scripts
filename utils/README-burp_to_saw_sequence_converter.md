# Burp to Snyk API&Web Sequence Converter

## Description

Converts Burp Suite Navigation Recorder sequences to Snyk API&Web's sequence format.

This converter transforms recordings made with the Burp Suite Navigation Recorder browser plugin into the format expected by Snyk API&Web for login and navigation sequences.


## Required Options

- `--input/-i`: Path to the Burp recording JSON file
- `--output/-o`: Path to the output Snyk API&Web sequence JSON file


## Usage Examples

### Convert a recorded file to Snyk API&Web sequence

```sh
python3 ./burp_to_saw_sequence_converter.py -i /tmp/burp_recorded_file.json -o /tmp/snyk_login_sequence.json
```




