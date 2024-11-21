import pytest

from bot.callbacks.utils import strip_command


@pytest.mark.parametrize(
    "text, expected",
    [
        ("/sum 1 2 3", "1 2 3"),
        ("/start", ""),
        ("hello", "hello"),
        ("/command with multiple words", "with multiple words"),
        ("/", ""),
    ],
)
def test_strip_command(text, expected):
    assert strip_command(text) == expected
