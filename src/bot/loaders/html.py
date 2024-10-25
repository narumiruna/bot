"""HTML content loading and conversion utilities.

This module provides functions for loading HTML content from various sources
and converting it to markdown format. It supports loading from URLs using different
methods (SingleFile, httpx, cloudscraper) and from local files.
"""

import asyncio
import os
import re
import tempfile
from pathlib import Path
from textwrap import dedent

import charset_normalizer
import cloudscraper
import httpx
from loguru import logger
from markdownify import markdownify

# Default headers for HTTP requests
DEFAULT_HEADERS = {
    "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    "Cookie": "over18=1",  # Required for some sites like PTT
}

# Default path for SingleFile executable
DEFAULT_SINGLEFILE_PATH = "/Users/narumi/.local/bin/single-file"


def strip_base64_images(markdown_text: str) -> str:
    """Remove base64-encoded images from markdown text.

    Args:
        markdown_text: The markdown text containing base64 images

    Returns:
        The markdown text with base64 images removed
    """
    pattern = r"!\[.*?\]\(data:image\/.*?;base64,.*?\)"
    return re.sub(pattern, "", markdown_text)


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


async def save_html_with_singlefile(url: str, cookies_file: str | None = None) -> str:
    """Download and save HTML content using SingleFile.

    Args:
        url: The URL to download
        cookies_file: Optional path to cookies file for authentication

    Returns:
        Path to saved HTML file

    Raises:
        FileNotFoundError: If cookies file doesn't exist
    """
    logger.info("Downloading HTML using SingleFile: {}", url)

    filename = tempfile.mktemp(suffix=".html")
    singlefile_path = os.getenv("SINGLEFILE_PATH", DEFAULT_SINGLEFILE_PATH)

    cmds = [singlefile_path]

    if cookies_file is not None:
        cookies_path = Path(cookies_file)
        if not cookies_path.exists():
            raise FileNotFoundError(f"Cookies file not found: {cookies_file}")

        cmds.extend(["--browser-cookies-file", str(cookies_path)])

    cmds.extend(
        [
            "--filename-conflict-action",
            "overwrite",
            url,
            filename,
        ]
    )

    process = await asyncio.create_subprocess_exec(*cmds)
    await process.communicate()

    return filename


async def load_html_with_singlefile(url: str) -> str:
    """Load HTML content using SingleFile and convert to markdown.

    Args:
        url: The URL to load

    Returns:
        Markdown-formatted content
    """
    html_file = await save_html_with_singlefile(url)
    return load_html_file(html_file)


def load_html_with_httpx(url: str) -> str:
    """Load HTML content using httpx and convert to markdown.

    Args:
        url: The URL to load

    Returns:
        Markdown-formatted content

    Raises:
        httpx.HTTPError: If request fails
    """
    logger.info("Loading HTML with httpx: {}", url)

    resp = httpx.get(url=url, headers=DEFAULT_HEADERS, follow_redirects=True)
    resp.raise_for_status()

    return convert_to_markdown(resp.content)


def load_html_with_cloudscraper(url: str) -> str:
    """Load HTML content using cloudscraper and convert to markdown.

    Useful for sites with anti-bot protection.

    Args:
        url: The URL to load

    Returns:
        Markdown-formatted content

    Raises:
        requests.exceptions.RequestException: If request fails
    """
    logger.info("Loading HTML with cloudscraper: {}", url)

    scraper = cloudscraper.create_scraper()
    resp = scraper.get(url)
    resp.raise_for_status()

    return convert_to_markdown(resp.content)


def load_html_file(filepath: str) -> str:
    """Load HTML content from a local file and convert to markdown.

    Args:
        filepath: Path to HTML file

    Returns:
        Markdown-formatted content
    """
    content = str(charset_normalizer.from_path(filepath).best())
    return dedent(markdownify(content, strip=["a", "img"]))
