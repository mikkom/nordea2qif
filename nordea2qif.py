#!/usr/bin/python

# nordea2qif.py
#
# (c) Mikko Matilainen <mikkom@iki.fi> 2009, 2010
#

from datetime import datetime
import htmllib
import re
import sys

class TransactionType:
    UNKNOWN = 0
    BANK = 1

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def print_qif(transaction_type, transaction_date, total, payee, memo = None):
    # Type
    qif = '!Type:'
    if transaction_type == TransactionType.BANK:
        qif += 'Bank'
    else:
        raise Exception('Unsupported transaction type.')
    qif += '\n'
    # Date
    qif += 'D' + transaction_date.strftime("%m/%d/%Y") + '\n'
    # Total
    qif += 'T' + '%.2f'%total + '\n'
    # Payee
    qif += 'P' + payee + '\n'
    # Memo
    if memo != None:
        qif += 'M' + memo + '\n'
    qif += '^\n'
    return qif

#
# Main
#

ARGUMENT_COUNT = 2
FILENAME_INDEX = 1

DATE_INDEX = 0
TOTAL_INDEX = 3
PAYEE_INDEX = 4
MEMO_INDEX = 10
MIN_FIELD_COUNT = PAYEE_INDEX + 1

if len(sys.argv) != ARGUMENT_COUNT:
    print 'Usage: nordea2qif.py [file]'
    sys.exit()

filename = sys.argv[FILENAME_INDEX]
f = open(filename, 'rb')
content = unicode(f.read(), 'iso-8859-1')
f.close()

# Recode to UTF-8
str = content.encode('utf-8')

output = ''

lines = str.splitlines()
for line in lines:
    if re.match('\d', line) == None:
        print 'Line does not start with a number, skipping...'
    else:
        fields = line.split('\t')
        if len(fields) < MIN_FIELD_COUNT:
            print 'Not enough fields in the line, skipping...'
        else:
            transaction_date = datetime.strptime(fields[DATE_INDEX], '%d.%m.%Y')

            totalstr = fields[TOTAL_INDEX]
            totalstr = totalstr.replace('.', '')
            totalstr = totalstr.replace(',', '.')
            total = float(totalstr)

            payee = unescape(fields[PAYEE_INDEX])

            memo = None
            if len(fields) > MEMO_INDEX and fields[MEMO_INDEX] != '':
                memo = unescape(fields[MEMO_INDEX])

            transaction_type = TransactionType.BANK  # Hardcoded, for now

            output += print_qif(transaction_type, transaction_date, total, payee, memo)

f = open('Checking Account.qif', 'w')
f.write(output)
f.close()
