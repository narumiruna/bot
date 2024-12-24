import tempfile
from pathlib import Path

import httpx
from pypdf import PdfReader

from .loader import Loader

DEFAULT_HEADERS = {
    "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
}


class PDFLoader(Loader):
    def load(self, url_or_file: str) -> str:
        if url_or_file.startswith("http"):
            url_or_file = download_pdf_from_url(url_or_file)
        return read_pdf_content(url_or_file)


def download_pdf_from_url(url: str) -> str:
    response = httpx.get(url=url, headers=DEFAULT_HEADERS, follow_redirects=True)
    response.raise_for_status()

    suffix = ".pdf" if response.headers.get("content-type") == "application/pdf" else None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        fp.write(response.content)
        return fp.name


def read_pdf_content(f: str | Path) -> str:
    lines = []
    with PdfReader(f) as reader:
        for page in reader.pages:
            text = page.extract_text(extraction_mode="plain")
            for line in text.splitlines():
                if not line.strip():
                    continue
                lines.append(line.strip())
    return "\n".join(lines)
