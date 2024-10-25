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


def strip_base64_images(markdown_text: str) -> str:
    pattern = r"!\[.*?\]\(data:image\/.*?;base64,.*?\)"
    cleaned_text = re.sub(pattern, "", markdown_text)
    return cleaned_text


def convert_to_markdown(text: str | bytes) -> str:
    if isinstance(text, bytes):
        text = str(charset_normalizer.from_bytes(text).best())

    return dedent(markdownify(text, strip=["a", "img"]))


async def save_html_with_singlefile(url: str, cookies_file: str | None = None) -> str:
    logger.info("Downloading HTML by SingleFile: {}", url)

    filename = tempfile.mktemp(suffix=".html")

    singlefile_path = os.getenv("SINGLEFILE_PATH", "/Users/narumi/.local/bin/single-file")

    cmds = [singlefile_path]

    if cookies_file is not None:
        if not Path(cookies_file).exists():
            raise FileNotFoundError("cookies file not found")

        cmds += [
            "--browser-cookies-file",
            cookies_file,
        ]

    cmds += [
        "--filename-conflict-action",
        "overwrite",
        url,
        filename,
    ]

    process = await asyncio.create_subprocess_exec(*cmds)
    await process.communicate()

    return filename


async def load_html_with_singlefile(url: str, markdown: bool = True) -> str:
    f = await save_html_with_singlefile(url)

    return load_html_file(f)


def load_html_with_httpx(url: str, markdown: bool = True) -> str:
    logger.info("Loading HTML: {}", url)

    headers = {
        "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
        "Cookie": "over18=1",  # ptt
    }

    resp = httpx.get(url=url, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    return convert_to_markdown(resp.content)


def load_html_with_cloudscraper(url: str, markdown: bool = True) -> str:
    logger.info("Loading HTML: {}", url)

    scraper = cloudscraper.create_scraper()
    resp = scraper.get(url)
    resp.raise_for_status()

    return convert_to_markdown(resp.content)


def load_html_file(f: str) -> str:
    text = str(charset_normalizer.from_path(f).best())
    return dedent(markdownify(text, strip=["a", "img"]))
