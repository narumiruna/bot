import os
import subprocess
import tempfile
from functools import cache
from pathlib import Path

import charset_normalizer
from loguru import logger

from .loader import Loader
from .utils import html_to_markdown


@cache
def get_singlefile_path() -> str:
    return os.getenv("SINGLEFILE_PATH", "single-file")


class SinglefileLoader(Loader):
    def __init__(self, cookies_file: str | None = None, browser_headless: bool = False) -> None:
        self.cookies_file = cookies_file
        self.browser_headless = browser_headless

    def load(self, url: str) -> str:
        filename = self.download(url)
        content = str(charset_normalizer.from_path(filename).best())
        return html_to_markdown(content)

    def download(self, url: str) -> str:
        logger.info("Downloading HTML using SingleFile: {}", url)

        filename = tempfile.mktemp(suffix=".html")
        singlefile_path = get_singlefile_path()

        cmds = [singlefile_path]

        if self.cookies_file is not None:
            cookies_path = Path(self.cookies_file)
            if not cookies_path.exists():
                raise FileNotFoundError(f"Cookies file not found: {self.cookies_file}")

            cmds += [
                "--browser-cookies-file",
                str(cookies_path),
            ]

        cmds += [
            "--filename-conflict-action",
            "overwrite",
            "--browser-headless",
            str(self.browser_headless).lower(),
            url,
            filename,
        ]

        subprocess.run(cmds)

        return filename
