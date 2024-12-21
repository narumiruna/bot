from pathlib import Path
from textwrap import dedent

import charset_normalizer
from markdownify import markdownify


def load_html_file(filepath: str | Path) -> str:
    """Load HTML content from a local file and convert to markdown.

    Args:
        filepath: Path to HTML file

    Returns:
        Markdown-formatted content
    """
    content = str(charset_normalizer.from_path(filepath).best())
    return dedent(markdownify(content, strip=["a", "img"]))
