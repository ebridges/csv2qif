from dateutil.parser import parse
from decimal import Decimal
from logging import info
from json import dumps
from datetime import datetime, date

TWOPLACES = Decimal(10) ** -2

class TransactionWriter(object):
  def __init__(self, output):
    if output:
      self.output = output

  def instance(t, output):
    if t == 'qif':
      return QifTransactionWriter(output)
    if t == 'json':
      return JsonTransactionWriter(output)

  instance = staticmethod(instance)

  def begin(self, account_info):
    pass

  def write_record(self, transaction):
    pass

  def end(self):
    pass


'''
{
  "accounts": [
    {
      "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
      "balances": {
        "available": 110,
        "current": 110,
        "iso_currency_code": "USD",
        "limit": null,
        "unofficial_currency_code": null
      },
      "mask": "0000",
      "name": "Plaid Checking",
      "official_name": "Plaid Gold Standard 0% Interest Checking",
      "subtype": "checking",
      "type": "depository"
    }
  ],
  "transactions": [
    {
      "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
      "amount": 2307.21,
      "iso_currency_code": "USD",
      "unofficial_currency_code": null,
      "category": [
        "Shops",
        "Computers and Electronics"
      ],
      "category_id": "19013000",
      "check_number": null,
      "date": "2017-01-29",
      "datetime": "2017-01-27T11:00:00Z",
      "authorized_date": "2017-01-27",
      "authorized_datetime": "2017-01-27T10:34:50Z",
      "location": {
        "address": "300 Post St",
        "city": "San Francisco",
        "region": "CA",
        "postal_code": "94108",
        "country": "US",
        "lat": 40.740352,
        "lon": -74.001761,
        "store_number": "1235"
      },
      "name": "Apple Store",
      "merchant_name": "Apple",
      "payment_meta": {
        "by_order_of": null,
        "payee": null,
        "payer": null,
        "payment_method": null,
        "payment_processor": null,
        "ppd_id": null,
        "reason": null,
        "reference_number": null
      },
      "payment_channel": "in store",
      "pending": false,
      "pending_transaction_id": null,
      "account_owner": null,
      "transaction_id": "lPNjeW1nR6CDn5okmGQ6hEpMo4lLNoSrzqDje",
      "transaction_code": null,
      "transaction_type": "place"
    }
  ]
}
'''

class JsonTransactionWriter(TransactionWriter):
  '''
  Format:
  https://plaid.com/docs/api/products/transactions/#transactionsget
  '''
  def begin(self, account_info):
    print( dumps(account_info, sort_keys=True), file=self.output)

  def write_record(self, transaction):
    def encode_date(obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
    print( dumps(transaction.to_dict(), sort_keys=True, default=encode_date), file=self.output)


class QifTransactionWriter(TransactionWriter):
  def begin(self, account):
    print('!Account', file=self.output)
    print('N%s' % account['name'], file=self.output)
    print('T%s' % account['type'], file=self.output)
    if 'description' in account:
      print('D%s' % account['description'], file=self.output)
    print('^', file=self.output)
    print('!Type:%s' % account['type'], file=self.output)


  def write_record(self, transaction):
    print('C', file=self.output) # cleared status: Values are blank (not cleared), "*" or "c" (cleared) and "X" or "R" (reconciled).
    print('D%s' % transaction['date'], file=self.output)
    print('N%s' % self.format_chknum(transaction), file=self.output)
    print('P%s' % transaction['name'], file=self.output)
    print('T%s' % self.format_amount(transaction['amount']), file=self.output)
    print('^', file=self.output)


  def format_chknum(self, t):
    return t['check_number'] if(t['check_number']) else 'N/A'


  def format_amount(self,a):
    d = Decimal(a).quantize(TWOPLACES).copy_negate()
    info("formatted amount [%s] as [%s]" % (a, str(d)))
    return d
