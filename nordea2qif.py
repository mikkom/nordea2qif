#!/usr/bin/python

# nordea2qif.py
#
# (c) Mikko Matilainen <mikkom@iki.fi> 2009, 2010
#

from datetime import datetime
import htmllib
import re
import sys

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def print_qif(transaction_type, transaction_date, total, payee, memo = None):
    # Type
    qif = '!Type:'
    if transaction_type != 666:
        qif += 'Bank'
    else:
        qif += 'DevilsDue'
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

# Main
if len(sys.argv) != 2:
    print 'Usage: nordea2qif.py [file]'
    sys.exit()

filename = sys.argv[1]
f = open(filename, 'rb')
content = unicode(f.read(), 'iso-8859-1')
f.close()

# Recode to UTF-8
str = content.encode('utf-8')

output = ''

lines = str.splitlines()
for line in lines:
    if re.match('\d', line) != None:
        fields = line.split('\t')
        if len(fields) < 5:
            print 'Not enough fields in the line, skipping...'
        else:
            transaction_date = datetime.strptime(fields[0], '%d.%m.%Y')

            totalstr = fields[3]
            totalstr = totalstr.replace('.', '')
            totalstr = totalstr.replace(',', '.')
            total = float(totalstr)

            payee = unescape(fields[4])

            memo = None
            if len(fields) >= 11 and fields[10] != '':
                memo = unescape(fields[10])

            transaction_type = 1 # Fixed, for now

            output += print_qif(transaction_type, transaction_date, total, payee, memo)
    else:
        print 'Line does not start with a number, skipping...'

f = open(filename + '.qif', 'w')
f.write(output)
f.close()
