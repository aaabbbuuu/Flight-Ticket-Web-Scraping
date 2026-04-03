"""Tests for price parsing logic."""

from flight_tracker.scraper import _parse_price


class TestParsePrice:
    def test_simple_dollar(self):
        assert _parse_price("$350") == 350

    def test_with_commas(self):
        assert _parse_price("$1,234") == 1234

    def test_with_decimals(self):
        assert _parse_price("$1,234.56") == 1234

    def test_dollar_no_comma(self):
        assert _parse_price("$899") == 899

    def test_empty_string(self):
        assert _parse_price("") is None

    def test_no_digits(self):
        assert _parse_price("N/A") is None

    def test_whitespace(self):
        assert _parse_price("  $450  ") == 450
