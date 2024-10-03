import pytest

from bot.loaders.url import replace_domain


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://twitter.com/someuser/status/1234567890", "https://api.fxtwitter.com/someuser/status/1234567890"),
        ("https://x.com/someuser/status/1234567890", "https://api.fxtwitter.com/someuser/status/1234567890"),
        ("https://example.com/someuser/status/1234567890", "https://example.com/someuser/status/1234567890"),
        ("twitter.com/someuser/status/1234567890", "twitter.com/someuser/status/1234567890"),
        (
            "https://subdomain.twitter.com/someuser/status/1234567890",
            "https://subdomain.twitter.com/someuser/status/1234567890",
        ),
    ],
)
def test_fix_twitter(url, expected):
    assert replace_domain(url) == expected
