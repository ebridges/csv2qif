from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import csv
from json import loads
from datetime import datetime
from logging import debug, info, warn, INFO, DEBUG, basicConfig
from sys import stdin, stdout, exit
from distutils.util import strtobool

from csv2qif import __version__, __doc__
from csv2qif import transaction_writer


QIF_DATE_FORMAT = '%m/%d/%Y'
PAYEE_FIELD = 'name'
DATE_FIELD = 'date'
AMOUNT_FIELD = 'amount'
REQUIRED_FIELDS = [DATE_FIELD, PAYEE_FIELD, AMOUNT_FIELD]


def get_data(input, date_idx):
    with get_inputhandle(input) as csvfile:
        try:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip the headers
            sorter = lambda row: datetime.strptime(
                row[date_idx], QIF_DATE_FORMAT
            ).date()
            sortedlist = sorted(reader, key=sorter)
            if len(sortedlist) > 0:
                start_idx = 0
                end_idx = len(sortedlist) - 1
                return sortedlist, {
                    'start': datetime.strptime(
                        sortedlist[start_idx][date_idx], QIF_DATE_FORMAT
                    ).date(),
                    'end': datetime.strptime(
                        sortedlist[end_idx][date_idx], QIF_DATE_FORMAT
                    ).date(),
                }
            else:
                return list(), {'start': None, 'end': None}
        except csv.Error as e:
            exit('file {}, line {}: {}'.format(input, reader.line_num, e))


def output_filename(account_path, fromto, file_ext):
    '''
    `account_path` represents the full hierarchical name of the account in GnuCash.
    Examples:
        'Assets:Checking Accounts:Joint Checking'
        'Liabilities:Credit Cards:Mastercard'
    '''
    account = account_path.split(':')[-1]
    f = datetime.strftime(fromto['start'], '%Y-%m-%d')
    t = datetime.strftime(fromto['end'], '%Y-%m-%d')
    return '%s--%s-%s.%s' % (f, t, account, file_ext)


def get_inputhandle(input):
    if input == 'stdin' or input == '-':
        return stdin
    else:
        return open(input, newline='')


def get_outputhandle(account_name, output_dir, output_format, fromto):
    if output_dir in ['-', 'stdout']:
        return stdout

    filename = output_filename(account_name, fromto, output_format)
    output_file = '%s/%s' % (output_dir, filename)
    return open(output_file, 'w')


def format_txn(t, col_spec):
    '''
    Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
    Transaction Date,Post Date,Description,Category,Type,Amount,Memo
    '''

    for f in REQUIRED_FIELDS:
        if f not in col_spec:
            raise ValueError(f'Required field {f} missing from col spec.')

    txn = {}
    for k, v in col_spec.items():
        txn[k] = t[v]

    return txn


def convert(args):
    if args.output_format == 'json':
        raise NotImplementedError('json support currently not implemented.')

    do_convert(
        args.account,
        args.account_type,
        args.input_file,
        args.output_dir,
        args.output_format,
        loads(args.col_spec),
        args.backup_input,
    )


def do_convert(account, type, input, output, format, col_spec, backup_input):
    data, fromto = get_data(input, col_spec[DATE_FIELD])
    if len(data) > 0:
        output_handle = get_outputhandle(account, output, format, fromto)

        try:
            w = transaction_writer.TransactionWriter.instance(format, output_handle)
            w.begin(account, type)

            txn_cnt = 1
            txn_total = len(data)
            debug('converting txn: %d of total: %d' % (txn_cnt, txn_total))
            for t in data:
                transaction = format_txn(t, col_spec)
                info(
                    'writing record for [%s: %s]'
                    % (transaction[DATE_FIELD], transaction[PAYEE_FIELD])
                )
                debug('%s' % transaction)
                w.write_record(transaction)
                txn_cnt = txn_cnt + 1

            w.end()

        finally:
            if output_handle is not stdout:
                output_handle.close()

        if backup_input:
            csv_file = output_filename(account, fromto, 'csv')
            with open(csv_file, 'w', newline='') as csv_handle:
                csv_writer = csv.writer(csv_handle, dialect='excel')
                csv_writer.writerows(data)

    else:
        warn(f'No records found for account {account}')


def configure_logging(level):
    if not level:
        level = INFO
    else:
        level = DEBUG
    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=level,
    )


def main():
    year = datetime.now().year
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        prog='csv2qif',
        description=__doc__,
        epilog=f'MIT License: ©{year} Edward Q. Bridges',
    )
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument(
        '-v', '--version', action='version', version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '-a',
        '--account',
        help='The full hierarchical name of the account in GnuCash.',
        required=True,
    )
    parser.add_argument(
        '-t',
        '--account-type',
        help='One of "Bank", "Cash", "CCard", or "Invst"',
        required=True,
    )
    parser.add_argument(
        '-i',
        '--input-file',
        help='Input file in CSV format; define location of required fields using "col-spec"',
        default='stdin',
    )
    parser.add_argument(
        '-o', '--output-dir', help='Directory to write output', default='stdout'
    )
    parser.add_argument(
        '-f',
        '--output-format',
        help='Format of output, either "qif" or "json"',
        default='qif',
    )
    parser.add_argument(
        '-c',
        '--col-spec',
        help='Specify column of required fields (date, name, amount, check_number)',
        default='{"date": 1, "name": 2, "amount": 3, "check_number": 6}',
    )
    parser.add_argument(
        '-b',
        '--backup-input',
        help='Save a copy of input CSV alongside the QIF file, with same filename.',
        type=lambda x: bool(strtobool(x)),
    )

    args = parser.parse_args()

    configure_logging(args.verbose)
    debug(args)

    convert(args)


if __name__ == '__main__':
    main()
