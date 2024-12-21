from pathlib import Path
from textwrap import dedent

import charset_normalizer
from markdownify import markdownify

# Default headers for HTTP requests
DEFAULT_HEADERS = {
    "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    "Cookie": "over18=1",  # Required for some sites like PTT
}

# Default path for SingleFile executable
DEFAULT_SINGLEFILE_PATH = "single-file"


def load_html_file(filepath: str | Path) -> str:
    """Load HTML content from a local file and convert to markdown.

    Args:
        filepath: Path to HTML file

    Returns:
        Markdown-formatted content
    """
    content = str(charset_normalizer.from_path(filepath).best())
    return dedent(markdownify(content, strip=["a", "img"]))
