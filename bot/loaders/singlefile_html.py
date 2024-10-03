import os
import subprocess
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup


def get_singlefile_path_from_env() -> str:
    return os.getenv("SINGLEFILE_PATH", "/Users/narumi/.local/bin/single-file")


def singlefile_download(url: str, cookies_file: str | None = None) -> str:
    filename = tempfile.mktemp(suffix=".html")

    singlefile_path = get_singlefile_path_from_env()

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

    subprocess.run(cmds)
    return filename


def load_singlefile_html(url: str) -> str:
    f = singlefile_download(url)

    with open(f, "rb") as fp:
        soup = BeautifulSoup(fp, "html.parser")
        text = soup.get_text(strip=True)
    return text
