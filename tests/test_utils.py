import pytest
from langchain_core.messages import AIMessage

from bot.utils import ai_message_repr
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
