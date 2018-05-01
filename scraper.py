from requests_html import HTMLSession
from datetime import datetime
import pytz
import decimal
import os
import csv
import sys
import codecs
import re


tz = pytz.timezone(os.getenv('VETURILO_TZ', 'Europe/Warsaw'))

session = HTMLSession()


veturilo_user = os.environ['VETURILO_USER']
veturilo_pass = os.environ['VETURILO_PASS']


def parse_value(value):
    """Parses delta value.

    "-10.00" -> Decimal('-10.00')
    "+10.00" -> Decimal('10.00')
    "" -> None
    """
    try:
        return decimal.Decimal(value)
    except decimal.InvalidOperation:
        return None


def parse_row_id(value):
    """Parses row number.

    "row_0" -> 0
    "row_32562" -> 32562
    """
    match = re.search(r'^row_(\d+)$', value)
    if match is not None:
        (row_id,) = match.groups()
        return int(row_id)
    return None


def main():

    r = session.get('https://www.veturilo.waw.pl/veturilo-login/')
    r.raise_for_status()

    r = session.get('https://poland.nextbike.net/iframe/?domain=vp&L=pl&id=login&redirect_index=https://www.veturilo.waw.pl/veturilo-login&redirect_account=https://www.veturilo.waw.pl/account')
    r.raise_for_status()

    form = r.html.find('#mailform', first=True)
    if form is None:
        raise RuntimeError('Unable to find form')

    r = session.post('https://poland.nextbike.net/iframe/?id=login&L=pl&domain=vp', data={
        'logintype': 'login',
        'redirect_index': 'https://www.veturilo.waw.pl/veturilo-login',
        'redirect_account': 'https://www.veturilo.waw.pl/account',
        'user': veturilo_user,
        'pass': veturilo_pass,
        'submit': 'Zaloguj'
    })
    r.raise_for_status()

    r = session.get('https://poland.nextbike.net/iframe/?L=pl&domain=vp')
    r.raise_for_status()
    table = r.html.find('#contenttable_account', first=True)
    if table is None:
        raise RuntimeError('Unable to find table')

    total = decimal.Decimal('0')

    with open('rentals.csv', 'w', encoding='utf-8') as rentals:
        rentals.write(codecs.BOM_UTF8.decode('utf-8'))

        writer = csv.writer(rentals, delimiter=';')

        for row in table.find('tr:has(td)'):
            cells = row.find('td')

            date_text = cells[0].text.strip()
            if not date_text:
                continue

            row_id = parse_row_id(row.attrs['id'])
            if row_id is None:
                raise RuntimeError('Invalid row id')

            date_naive = datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
            date = tz.localize(date_naive)
            description = cells[1].text.strip()
            value = parse_value(cells[2].text.strip())
            if value is not None:
                total += value
            writer.writerow([row_id, date, description, value])


if __name__ == '__main__':
    main()
