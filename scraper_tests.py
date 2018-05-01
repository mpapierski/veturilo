from unittest import mock, TestCase
from datetime import time
from decimal import Decimal


class ScraperTestCase(TestCase):

    @mock.patch.dict('os.environ', {
        'VETURILO_TZ': 'Europe/Warsaw',
        'VETURILO_USER': '+48123456789',
        'VETURILO_PASS': 'dupa.8'
    })
    def setUp(self):
        from scraper import parse_value, parse_row_id, extract_rental_details
        self.parse_value = parse_value
        self.parse_row_id = parse_row_id
        self.extract_rental_details = extract_rental_details

    def test_positive(self):
        value = self.parse_value('+10.00')
        self.assertIsNotNone(value)
        self.assertEquals(value, Decimal('10.00'))

    def test_negative(self):
        value = self.parse_value('-10.00')
        self.assertIsNotNone(value)
        self.assertEquals(value, Decimal('-10.00'))

    def test_invalid(self):
        self.assertIsNone(self.parse_value(''))

    def test_parse_row_id_small(self):
        value = self.parse_row_id('row_0')
        self.assertIsNotNone(value)
        self.assertEquals(value, 0)

    def test_parse_row_id_large(self):
        value = self.parse_row_id('row_413631')
        self.assertIsNotNone(value)
        self.assertEquals(value, 413631)

    def test_parse_row_id_invalid(self):
        self.assertIsNone(self.parse_row_id('row_asdf'))

    def test_extract_bike_details(self):
        values = self.extract_rental_details(
            'Rower 123456 do 14:15:16 (ul. Jana Pawła II)')
        self.assertEquals(len(values), 2)
        bike_id, time_point = values
        self.assertEquals(bike_id, 123456)
        self.assertEquals(time_point, time(14, 15, 16))
