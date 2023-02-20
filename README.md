# csv2qif

## Usage

```
CSV to QIF

usage: csv2qif [-h] [--verbose] [-v] -a ACCOUNT -t ACCOUNT_TYPE -i INPUT_FILE [-o OUTPUT_DIR] [-f OUTPUT_FORMAT] [-c COL_SPEC]

Convert financial transactions in CSV format to QIF files.

options:
  -h, --help            show this help message and exit
  --verbose
  -v, --version         show program's version number and exit
  -a ACCOUNT, --account ACCOUNT
  -t ACCOUNT_TYPE, --account-type ACCOUNT_TYPE
  -i INPUT_FILE, --input-file INPUT_FILE
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Location to write output file (default: .)
  -f OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        Format of output, either "qif" or "json" (default: qif)
  -c COL_SPEC, --col-spec COL_SPEC
                        Specify column of required fields (date, name, amount, check_number)
                        (default: {"date": 1, "name": 2, "amount": 3, "check_number": 6})
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
