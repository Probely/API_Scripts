# Burp and HAR files converter

## Converts Burp or HAR files to Probely's Navigation sequences.

### Required options

 - `--type/-t`: `burp` or `har` (input file format)
 - `--input/-i`: `/path/to/original_file`
 - `--output/-o`: `/path/to/destination_file`

### Optional

- `--crawl` or `--no-crawl` (default: `crawl`)

### From Burp file to Probely's Navigation sequence

```sh
$ python3 ./burp_har_to_navigation_seq.py -t burp -i /tmp/burp_exported_file.xml -o /tmp/probely_navigation.json
```


### From HAR file to Probely's Navigation sequence

```sh
$ python3 ./burp_har_to_navigation_seq.py -t har -i /tmp/har_exported_file.har -o /tmp/probely_navigation.json
```

```sh
$ python3 ./burp_har_to_navigation_seq.py -h 
usage: burp_har_to_navigation_seq.py [-h] -t {burp,har} -i INPUT -o OUTPUT [--crawl | --no-crawl]

Converts Burp or HAR files to Probely's navigation sequences

options:
  -h, --help            show this help message and exit
  -t {burp,har}, --type {burp,har}
                        burp/har
  -i INPUT, --input INPUT
                        Input file
  -o OUTPUT, --output OUTPUT
                        Output file
  --crawl, --no-crawl   Crawl the requests
```