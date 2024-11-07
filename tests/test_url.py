import pytest

from bot.loaders.url import is_instagram_reel_url
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


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www.instagram.com/reel/xyz", True),
        ("https://www.instagram.com/reel/", True),
        ("https://www.instagram.com/reels/xyz", False),
        ("https://www.instagram.com/someuser/reel/xyz", False),
        ("https://www.instagram.com/reel", False),
        ("https://www.instagram.com/reelxyz", False),
    ],
)
def test_is_instagram_reel_url(url, expected):
    assert is_instagram_reel_url(url) == expected
