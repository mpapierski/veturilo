from requests_html import HTMLSession
from datetime import datetime, time, timedelta
from collections import defaultdict
import operator
import pytz
import decimal
import os
import csv
import sys
import codecs
import re
import statistics

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


def extract_rental_details(value):
    """Extract rental details.

    "Rower 63854 do 13:00:22" -> (63854, time(13, 00, 22))
    """
    match = re.search(r'^Rower (\d+) do (\d+):(\d+):(\d+)', value)
    if match is None:
        return None
    bike_id, hours, minutes, seconds = map(int, match.groups())
    return (bike_id, time(hours, minutes, seconds))


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

    rental_time = timedelta()
    bikes = defaultdict(int)
    rental_times = []

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

            rental = extract_rental_details(description)
            if rental is not None:
                (bike_id, time_point) = rental
                return_date = date_naive.replace(
                    hour=time_point.hour,
                    minute=time_point.minute,
                    second=time_point.second)
                # How long this bike have been rented
                timediff = return_date - date_naive
                # Add this
                rental_times += [timediff]
                # Mark this bike as rented
                bikes[bike_id] += 1
                # Add total rental time
                rental_time += timediff

            if value is not None:
                total += value
            writer.writerow([row_id, date, description, value])

    print('Account status', total)
    print('Total rental time', rental_time)
    print('Longest rental time', max(rental_times))
    print('Shortest rental time', min(rental_times))

    rental_by_seconds = (td.total_seconds() for td in rental_times)
    print('Average rental time', timedelta(
        seconds=statistics.mean(rental_by_seconds)))
    sorted_bikes = sorted(
        bikes.items(), key=operator.itemgetter(1), reverse=True)
    for bike_id, count in sorted_bikes:
        print(bike_id, count)


if __name__ == '__main__':
    main()
