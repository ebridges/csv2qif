# csv2qif

## Usage

```
CSV to QIF

usage: csv2qif -a ACCOUNT -t ACCOUNT_TYPE 
               [-i INPUT_FILE] [-o OUTPUT_DIR] [-f OUTPUT_FORMAT] [-c COL_SPEC] 
               [-b] [-s]
               [--help] [--verbose] [--version]

Convert financial transactions in CSV format to QIF files.

options:
  -a ACCOUNT, --account ACCOUNT
                        The full hierarchical name of the account in GnuCash.
                        (default: None)
  -t ACCOUNT_TYPE, --account-type ACCOUNT_TYPE
                        One of "Bank", "Cash", "CCard", or "Invst"
                        (default: None)
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input file in CSV format; define location of required fields using "col-spec"
                        (default: stdin)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to write output
                        (default: stdout)
  -f OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        Format of output, either "qif" or "json"
                        (default: qif)
  -c COL_SPEC, --col-spec COL_SPEC
                        Specify column of required fields (date, name, amount, check_number)
                        (default: {"date": 1, "name": 2, "amount": 3, "check_number": 6})
  -b, --backup-input    Save a copy of input CSV alongside the QIF file, with same filename.
                        (default: False)
  -s, --strip-headers   Assume first row of input has headers, and remove it. 
                        (default: True)
  --verbose             Debug-level logging
  -v, --version         Show program's version number and exit
  -h, --help            Show this help message and exit

MIT License: ©2023 Edward Q. Bridges
```

## Development

1. It is recommended to use `pyenv` to ensure correct python version is in use.  Cf.: `.python-version`
2. Set up virtualenv: `python -m venv venv`
3. Activate virtualenv: `source ./venv/bin/activate`
4. Update pip: `pip install --upgrade pip`

## Release process

1. Format code using: `black .`
2. Commit/push all final code.
3. Increment version in `csv2qif/__init__.py` and commit/push.
4. Tag release in format `x.y.z`, using same version string as in `csv2qif/__init__.py`. Push tag to remote.
5. [Publish a new release version](https://github.com/ebridges/csv2qif/releases/new); doing so will trigger an upload to PyPI.

## License

[MIT](LICENSE)
