#!/usr/bin/python3

#####
#
# Plenum-Reminder, by Kunsi, modified for AfRA by Morn_
#
# To be executed by a cronjob every day at 00:01
#
# Checks wether a Plenum is scheduled for the next day, if yes, it
# sends out a mail notification to the intern mailing list.
#
#####

import requests
import sys
import datetime
import smtplib
import locale
import re
from email.mime.text import MIMEText

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

wiki = requests.get("https://afra-berlin.de/dokuwiki/doku.php?id=plenum&do=export_raw")
wikisource = wiki.content.decode('utf-8')

date_match = re.search(r"\*\*Termin:\*\* [a-zA-Z]*, ([0-9]+).([0-9]+).([0-9]+),", wikisource)
topics_match = re.search(r"\*\*(Themen|Topics):\*\*\n(( .*\n)+)", wikisource)


if not date_match:
    raise Exception("Plenum date not found on wiki page.")

if not topics_match:
    raise Exception("Plenum topics could not be parsed.")

next_plenum_date = datetime.date(year=int(date_match.group(3)), month=int(date_match.group(2)), day=int(date_match.group(1)))
topics_text = topics_match.group(2)

if len(topics_text) > 128 * 1024:
    raise Exception("Topic text seems a bit long.")

print("Next plenum seems to be on {:%x}.".format(next_plenum_date))

tomorrow = datetime.date.today() + datetime.timedelta(days=1)

if tomorrow == next_plenum_date:
    print("Tomorrow is plenum.")

    msg = MIMEText(
        "Hallo,\n\n"
        "morgen ist laut Wiki [1] wieder mal Plenum. Nachfolgend die\n"
        "Tagesordnungspunkte:\n\n{}\n"
        "Viele Grüße,\n\n"
        "Das AfRA-Plenum-Reminder-Script\n\n"
        "[1] https://afra-berlin.de/dokuwiki/doku.php?id=plenum\n".format(topics_text))

    msg['Subject'] = 'Plenum am {:%A, %d.%m.%Y}'.format(next_plenum_date)
    msg['From'] = 'AfRA Plenum Reminder <afra-plenum-reminder@0ptr.net>'
    msg['To'] = 'afra@afra-berlin.de'

    smtpObj = smtplib.SMTP('localhost')
    smtpObj.send_message(msg)
    smtpObj.quit()

    print("Plenum reminder email was sent.")

else:
    print("Tomorrow is no plenum.")
