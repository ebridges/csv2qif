from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import csv
from json import loads
from datetime import datetime
from logging import debug, info, INFO, DEBUG, basicConfig
from sys import stdin, stdout, exit

from csv2qif import __version__, __doc__
from csv2qif import transaction_writer


def get_data(input):
    with get_inputhandle(input) as csvfile:
        try:
            reader = csv.reader(csvfile)
            next(reader, None)  # skip the headers
            sorter = lambda row: datetime.strptime(row[1], "%m/%d/%Y").date()
            sortedlist = sorted(reader, key=sorter)
            end_idx = len(sortedlist) - 1
            return sortedlist, {
                "start": datetime.strptime(sortedlist[0][1], "%m/%d/%Y").date(),
                "end": datetime.strptime(sortedlist[end_idx][1], "%m/%d/%Y").date(),
            }
        except csv.Error as e:
            exit("file {}, line {}: {}".format(input, reader.line_num, e))


def output_filename(account_path, fromto, file_ext):
    account = account_path.split(":")[-1]
    f = datetime.strftime(fromto["start"], "%Y-%m-%d")
    t = datetime.strftime(fromto["end"], "%Y-%m-%d")
    return "%s--%s-%s.%s" % (f, t, account, file_ext)

def get_inputhandle(input):
    if input == 'stdin' or input == '-':
        return stdin
    else:
        return open(input, newline="")


def get_outputhandle(account_name, output_dir, output_format, fromto):
    if output_dir in ['-', 'stdout']:
        return stdout

    filename = output_filename(account_name, fromto, output_format)
    output_file = "%s/%s" % (output_dir, filename)
    return open(output_file, "w")


def format_txn(t, col_spec):
    """
    Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
    """
    return {
        "date": t[col_spec["date"]],
        "name": t[col_spec["name"]],
        "amount": t[col_spec["amount"]],
        "check_number": t[col_spec["check_number"]],
    }


def convert(args):
    do_convert(
        args.account,
        args.account_type,
        args.input_file,
        args.output_dir,
        args.output_format,
        loads(args.col_spec),
    )


def do_convert(account, account_type, input_file, output_dir, output_format, col_spec):
    data, fromto = get_data(input_file)
    output_handle = get_outputhandle(account, output_dir, output_format, fromto)

    try:
        w = transaction_writer.TransactionWriter.instance(output_format, output_handle)
        w.begin(account, account_type)

        txn_cnt = 1
        txn_total = len(data)
        debug("converting txn: %d of total: %d" % (txn_cnt, txn_total))
        for t in data:
            transaction = format_txn(t, col_spec)
            info(
                "writing record for [%s: %s]"
                % (transaction["date"], transaction["name"])
            )
            debug("%s" % transaction)
            w.write_record(transaction)
            txn_cnt = txn_cnt + 1

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
        format="[%(asctime)s][%(levelname)s] %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        level=level,
    )


def main():
    year = datetime.now().year
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        prog="csv2qif",
        description=__doc__,
        epilog=f"MIT License: ©{year} Edward Q. Bridges",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-a", "--account", required=True)
    parser.add_argument("-t", "--account-type", required=True)
    parser.add_argument("-i", "--input-file", default="stdin")
    parser.add_argument(
        "-o", "--output-dir", help="Directory to write output", default="stdout"
    )
    parser.add_argument(
        "-f",
        "--output-format",
        help='Format of output, either "qif" or "json"',
        default="qif",
    )
    parser.add_argument(
        "-c",
        "--col-spec",
        help="Specify column of required fields (date, name, amount, check_number)",
        default='{"date": 1, "name": 2, "amount": 3, "check_number": 6}',
    )

    args = parser.parse_args()

    configure_logging(args.verbose)
    debug(args)

    convert(args)


if __name__ == "__main__":
    main()
