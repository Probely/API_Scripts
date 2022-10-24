# Navigation Converter

## Converts between Probely's Navigation sequences and Selenium.

### Required options

 - `--convert/-c`: `selenium2probely` or `probely2selenium`
 - `--input/-i`: `/path/to/original_file`
 - `--output/-o`: `/path/to/destination_file` (Coverting to Selenium requires `.side` extension)

### From Selenium to Probely's Navigation sequence

```sh
$ python3 ./navigation_converter.py -c 'selenium2probely' -i /tmp/selenium_testfile.side -o /tmp/probely_navigation.json
```


### From Probely's Navigation sequence to Selenium

```sh
$ python3 ./navigation_converter.py -c 'probely2selenium' -i /tmp/probely_navigation.json -o /tmp/selenium_testfile.side
```

