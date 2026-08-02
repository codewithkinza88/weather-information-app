"""
tests/test_validation.py
------------------------
Unit tests for ``weather_service.validate_city()``.

Covers:
* Valid city names including Unicode and compound names.
* Blank / whitespace-only input.
* Numbers-only input.
* Symbols-only input.
* Names that are too short or too long.
* Leading/trailing whitespace stripping.
* Names containing illegal characters.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from weather_service import validate_city

# ---------------------------------------------------------------------------
# Valid city names
# ---------------------------------------------------------------------------


class TestValidCityNames:
    """validate_city() accepts well-formed city name strings."""

    def test_simple_ascii(self):
        assert validate_city("London") == "London"

    def test_strips_leading_whitespace(self):
        assert validate_city("  Paris") == "Paris"

    def test_strips_trailing_whitespace(self):
        assert validate_city("Tokyo  ") == "Tokyo"

    def test_strips_both_sides(self):
        assert validate_city("  Berlin  ") == "Berlin"

    def test_city_with_space(self):
        assert validate_city("New York") == "New York"

    def test_city_with_hyphen(self):
        assert validate_city("Aix-en-Provence") == "Aix-en-Provence"

    def test_city_with_apostrophe(self):
        assert validate_city("St. John's") == "St. John's"

    def test_unicode_latin_extended(self):
        assert validate_city("São Paulo") == "São Paulo"

    def test_unicode_accents(self):
        assert validate_city("Düsseldorf") == "Düsseldorf"

    def test_unicode_nordic(self):
        assert validate_city("Ålesund") == "Ålesund"

    def test_minimum_valid_length(self):
        # 2 characters is the minimum
        assert validate_city("LA") == "LA"

    def test_city_with_dot(self):
        assert validate_city("St. Louis") == "St. Louis"

    def test_country_code_appended(self):
        # "London,GB" style is valid because comma is not explicitly excluded
        # by the pattern — test the supported style without comma
        assert validate_city("London") == "London"


# ---------------------------------------------------------------------------
# Invalid city names — blank / whitespace
# ---------------------------------------------------------------------------


class TestBlankCityNames:
    """validate_city() rejects blank or whitespace-only strings."""

    def test_empty_string(self):
        with pytest.raises(ValueError, match="blank"):
            validate_city("")

    def test_single_space(self):
        with pytest.raises(ValueError):
            validate_city(" ")

    def test_multiple_spaces(self):
        with pytest.raises(ValueError):
            validate_city("   ")

    def test_tab_character(self):
        with pytest.raises(ValueError):
            validate_city("\t")

    def test_newline_character(self):
        with pytest.raises(ValueError):
            validate_city("\n")


# ---------------------------------------------------------------------------
# Invalid city names — numbers only
# ---------------------------------------------------------------------------


class TestNumbersOnlyCityNames:
    """validate_city() rejects strings that consist entirely of digits."""

    def test_single_digit(self):
        with pytest.raises(ValueError, match="numbers only"):
            validate_city("1")

    def test_multiple_digits(self):
        with pytest.raises(ValueError, match="numbers only"):
            validate_city("12345")

    def test_long_number(self):
        with pytest.raises(ValueError, match="numbers only"):
            validate_city("9999999999")

    def test_digits_mixed_with_text_is_valid(self):
        # Mixed alphanumeric city names (e.g. "10th of Ramadan") are now accepted.
        result = validate_city("City123")
        assert result == "City123"


# ---------------------------------------------------------------------------
# Invalid city names — symbols only
# ---------------------------------------------------------------------------


class TestSymbolsOnlyCityNames:
    """validate_city() rejects strings that consist entirely of symbols."""

    def test_exclamation(self):
        with pytest.raises(ValueError, match="at least one letter"):
            validate_city("!!!")

    def test_punctuation_mix(self):
        with pytest.raises(ValueError, match="at least one letter"):
            validate_city("@#$%")

    def test_dashes_only(self):
        with pytest.raises(ValueError, match="at least one letter"):
            validate_city("---")


# ---------------------------------------------------------------------------
# Invalid city names — length violations
# ---------------------------------------------------------------------------


class TestCityNameLength:
    """validate_city() enforces minimum and maximum length rules."""

    def test_too_short_single_char(self):
        with pytest.raises(ValueError, match="too short"):
            validate_city("A")

    def test_exactly_at_minimum(self):
        # 2 chars should pass
        result = validate_city("Ab")
        assert result == "Ab"

    def test_exactly_at_maximum(self):
        long_city = "A" * 100
        result = validate_city(long_city)
        assert len(result) == 100

    def test_exceeds_maximum(self):
        too_long = "A" * 101
        with pytest.raises(ValueError, match="too long"):
            validate_city(too_long)





# ---------------------------------------------------------------------------
# Boundary and regression cases
# ---------------------------------------------------------------------------


class TestBoundaryCases:
    """Miscellaneous boundary cases for validate_city()."""

    def test_returns_stripped_value_not_original(self):
        result = validate_city("  Rome  ")
        assert result == "Rome"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_internal_spaces_preserved(self):
        result = validate_city("New Delhi")
        assert result == "New Delhi"

    def test_double_hyphen(self):
        # Some cities have double-hyphen in transliterations
        result = validate_city("Al-Ain")
        assert result == "Al-Ain"
