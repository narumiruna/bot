import pytest

from bot.utils import parse_url


@pytest.mark.parametrize(
    "s, expected",
    [
        ("Check this out: https://example.com", "https://example.com"),
        ("No URL here!", ""),
        ("Multiple URLs: https://example.com and https://another.com", "https://example.com"),
        ("Just text", ""),
    ],
)
def test_parse_url(s, expected):
    assert parse_url(s) == expected
