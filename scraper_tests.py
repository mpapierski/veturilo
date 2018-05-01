from unittest import mock, TestCase

from decimal import Decimal


class ScraperTestCase(TestCase):

    @mock.patch.dict('os.environ', {
        'VETURILO_TZ': 'Europe/Warsaw',
        'VETURILO_USER': '+48123456789',
        'VETURILO_PASS': 'dupa.8'
    })
    def setUp(self):
        from scraper import parse_value
        self.parse_value = parse_value

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
