import functools
import json
import re
from pathlib import Path
from typing import Any

import telegraph


def save_text(text: str, f: str) -> None:
    with open(f, "w") as fp:
        fp.write(text)


def load_json(f: str) -> Any:
    with Path(f).open(encoding="utf-8") as fp:
        return json.load(fp)


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
