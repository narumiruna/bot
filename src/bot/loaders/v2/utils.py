from textwrap import dedent

import charset_normalizer
from markdownify import markdownify


def convert_to_markdown(content: str | bytes) -> str:
    """Convert HTML content to markdown format.

    Args:
        content: HTML content as string or bytes

    Returns:
        Converted markdown text with normalized whitespace
    """
    if isinstance(content, bytes):
        content = str(charset_normalizer.from_bytes(content).best())

    return dedent(markdownify(content, strip=["a", "img"]))
