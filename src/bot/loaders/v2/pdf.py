import tempfile
from pathlib import Path

import httpx
from loguru import logger
from pypdf import PdfReader

from .loader import Loader


class PDFLoader(Loader):
    def load(self, url: str) -> str:
        return load_pdf(url)


def load_pdf(url: str) -> str:
    logger.info("Loading PDF: {}", url)

    headers = {
        "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
        "Cookie": "over18=1",  # ptt
    }

    resp = httpx.get(url=url, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    suffix = ".pdf" if resp.headers.get("content-type") == "application/pdf" else None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        fp.write(resp.content)
        return load_pdf_file(fp.name)


def load_pdf_file(f: str | Path) -> str:
    texts = []
    with PdfReader(f) as reader:
        texts = [page.extract_text(extraction_mode="plain") for page in reader.pages]
    return "\n".join(texts)
