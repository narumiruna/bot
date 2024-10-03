import tempfile

import httpx
from langchain_community.document_loaders.pdf import PyPDFLoader

from .utils import docs_to_str

DEFAULT_HEADERS = {
    "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    "Cookie": "over18=1",  # ptt
}


def load_pdf(url: str) -> str:
    resp = httpx.get(url=url, headers=DEFAULT_HEADERS, follow_redirects=True)
    resp.raise_for_status()

    suffix = ".pdf" if resp.headers.get("content-type") == "application/pdf" else None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        fp.write(resp.content)

    return docs_to_str(PyPDFLoader(fp.name).load())


def load_pdf_file(f: str) -> str:
    return docs_to_str(PyPDFLoader(f).load())
