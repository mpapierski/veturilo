from decimal import Decimal
from scraper import parse_value

from nose.tools import assert_equals, assert_is_none


def test_positive():
    assert_equals(parse_value('+10.00'), Decimal('10.00'))


def test_negative():
    assert_equals(parse_value('-10.00'), Decimal('-10.00'))


def test_invalid():
    assert_is_none(parse_value(''))
