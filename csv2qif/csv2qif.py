"""
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
"""
from datetime import datetime
from logging import debug, info, INFO, DEBUG, basicConfig
from sys import stdout, stdin
from tomllib import load
import csv
from docopt import docopt

import transaction_writer


def get_data(input):
  with open(input, newline='') as csvfile:
    try:
      reader = csv.reader(csvfile)
      next(reader, None)  # skip the headers
      sortedlist = sorted(reader, key=lambda row: datetime.strptime(row[1], '%m/%d/%Y').date())
      return sortedlist, {
          'start': sortedlist[0][1],
          'end': sortedlist[len(sortedlist)-1][1],
        }
    except csv.Error as e:
        sys.exit('file {}, line {}: {}'.format(input, reader.line_num, e))

def output_filename(account_path, fromto, file_ext):
  account = account_path.split(':')[-1]
  return '%s--%s-%s.%s' % (fromto['start'], fromto['end'], account, file_ext)


def get_outputhandle(a, o, fromto):
    output_to_file = True if o['dir'] else False
    output_file = '%s/%s' % (o['dir'], output_filename(a['name'], fromto, o['format']))
    return output_to_file and open(output_file, 'w') or stdout


def format_txn(t):
  '''
  Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
  '''
  return {
    'date': t[1],
    'name': t[2],
    'amount': t[3],
    'check_number': t[6],
  }

def convert(account, input, output):
    data, fromto = get_data(input)
    output_handle = get_outputhandle(account, output, fromto)

    try:
      w = transaction_writer.TransactionWriter.instance(output['format'], output_handle)
      w.begin(account)

      txn_cnt = 1
      txn_total = len(data)
      debug("converting txn: %d of total: %d" % (txn_cnt, txn_total))
      for t in data:
        transaction = format_txn(t)
        info('writing record for [%s: %s]' % (transaction['date'], transaction['name']))
        debug('%s' % transaction)
        w.write_record(transaction)
        txn_cnt = txn_cnt+1
      
      w.end()

    finally:
      if output_handle is not stdout:
        output_handle.close()


def configure_logging(level):
    if not level:
        level = INFO
    else:
        level = DEBUG
    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=level)


def main():
  with open("pyproject.toml", "rb") as f:
    data = load(f)
    version = data['tool']['poetry']['version']
  args = docopt(__doc__, version=version)
  configure_logging(args['--verbose'])
  debug(args)
  
  if args['convert']:
    account = {
      'name': args['--account'],
      'type': args['--account-type'],
    }
    output = {
      'dir': args['--output-dir'],
      'format': args['--output-format']
    }
    input = args['--input-file'] 

    convert(account, input, output)
    return

if __name__ == '__main__':
  main()
