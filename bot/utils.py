import contextlib
import functools
import os
import re
import tempfile
from pathlib import Path

import httpx
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.html_bs import BSHTMLLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from loguru import logger

DEFAULT_HEADERS = {
    "User-Agent": "Chrome/126.0.0.0 Safari/537.36",
}


def download(path_or_url: str) -> str:
    resp = httpx.get(url=path_or_url, headers=DEFAULT_HEADERS)
    resp.raise_for_status()

    suffix = ".pdf" if resp.headers.get("content-type") == "application/pdf" else None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        fp.write(resp.content)
        return fp.name

    return ""


def parse_url(s: str) -> str:
    url_pattern = r"https?://[^\s]+"

    match = re.search(url_pattern, s)
    if match:
        return match.group(0)

    return ""


def docs_to_str(docs: list[Document]) -> str:
    return "\n".join([doc.page_content for doc in docs])


def load_document(url: str) -> str:
    # https://python.langchain.com/docs/integrations/document_loaders/

    with contextlib.suppress(ValueError):
        return docs_to_str(YoutubeLoader.from_youtube_url(url, add_video_info=True, language=["zh", "ja", "en"]).load())

    f = download(url)

    if f.endswith(".pdf"):
        return docs_to_str(PyPDFLoader(f).load())

    return docs_to_str(BSHTMLLoader(f).load())


def set_sqlite_llm_cache() -> None:
    database_path = Path.home() / ".cache" / ".langchain.db"
    logger.info("Using SQLite cache: {}", database_path)

    cache = SQLiteCache(database_path.as_posix())

    set_llm_cache(cache)


@functools.cache
def get_llm_from_env() -> BaseChatModel:
    if "OPENAI_API_KEY" in os.environ:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    elif "GOOGLE_API_KEY" in os.environ:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    else:
        raise ValueError("No API key found in environment variables")
