# csv2qif

## Usage

```
CSV to QIF.

Convert financial transactions in CSV format to QIF files.

Usage:
  csv2qif convert --account=<account-name> --account-type=<type> [--output-format=<fmt>] [--input-file=<path>] [--output-dir=<path>] [--verbose]
  csv2qif -h | --help
  csv2qif --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --account=<account-name>  Complete GnuCash account name.
  --account-type=<type>     QIF Account type <https://www.w3.org/2000/10/swap/pim/qif-doc/QIF-doc.htm> [Default: Bank]
  --output-format=<format>  Output format either 'json' or 'qif'. [Default: qif]
  --output-dir=<path>       Location to output file to. (Default: output to stdout)
  --input-file=<path>       Location of input file.
  --ignore-pending          Ignore pending transactions.
  --verbose                 Verbose logging output.
```

## License

[MIT](LICENSE.md)
