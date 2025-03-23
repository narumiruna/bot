import asyncio
import concurrent.futures
import functools
import json
import re
from functools import cache
from pathlib import Path
from typing import Any

import aiofiles
import kabigon
import telegraph
from kabigon.compose import Compose


def save_text(text: str, f: str) -> None:
    with open(f, "w") as fp:
        fp.write(text)


def load_json(f: str) -> Any:
    with Path(f).open(encoding="utf-8") as fp:
        return json.load(fp)


def save_json(data: Any, f: str) -> None:
    with Path(f).open("w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)


async def async_save_json(data: Any, f: str) -> None:
    async with aiofiles.open(f, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)


def parse_url(s: str) -> str:
    url_pattern = r"https?://[^\s]+"

    match = re.search(url_pattern, s)
    if match:
        return match.group(0)

    return ""


@functools.cache
def get_telegraph_client() -> telegraph.Telegraph:
    client = telegraph.Telegraph()
    client.create_account(short_name="Narumi's Bot")
    return client


def create_page(title: str, **kwargs) -> str:
    client = get_telegraph_client()

    resp = client.create_page(title=title, **kwargs)
    return resp["url"]


def async_wrapper(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, func, *args, **kwargs)
            return result

    return wrapper


@cache
def get_composed_loader() -> Compose:
    return Compose(
        [
            kabigon.YoutubeLoader(),
            kabigon.ReelLoader(),
            kabigon.YtdlpLoader(),
            kabigon.PDFLoader(),
            kabigon.PlaywrightLoader(),
        ]
    )


def load_url(url: str) -> str:
    loader = get_composed_loader()
    return loader.load(url)


async def async_load_url(url: str) -> str:
    loader = get_composed_loader()
    return await loader.async_load(url)
