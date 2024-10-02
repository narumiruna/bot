import os

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from bot.utils import ai_message_repr
from bot.utils import docs_to_str
from bot.utils import download_by_httpx
from bot.utils import load_document
from bot.utils import parse_url
from bot.utils import replace_domain


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


@pytest.mark.parametrize(
    "docs, expected",
    [
        ([Document(page_content="Page 1"), Document(page_content="Page 2")], "Page 1\nPage 2"),
        ([], ""),
    ],
)
def test_docs_to_str(docs, expected):
    assert docs_to_str(docs) == expected


@pytest.mark.parametrize(
    "ai_message, expected",
    [
        (AIMessage(content="Hello"), "Hello"),
        (AIMessage(content=["Item 1", "Item 2"]), "• Item 1\n• Item 2"),
        (AIMessage(content=[{"key1": "value1", "key2": "value2"}]), "• key1: value1\n• key2: value2"),
    ],
)
def test_ai_message_repr(ai_message, expected):
    assert ai_message_repr(ai_message) == expected


def test_download():
    url = "https://www.example.com"
    file_path = download_by_httpx(url)
    assert os.path.exists(file_path)
    # Clean up the downloaded file
    os.remove(file_path)


def test_load_document():
    url = "https://www.example.com"
    content = load_document(url)
    assert isinstance(content, str)
    assert len(content) > 0
