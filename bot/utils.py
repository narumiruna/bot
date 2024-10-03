import functools
import re
import tempfile
from urllib.parse import urlparse
from urllib.parse import urlunparse

import chardet
import httpx
import telegraph
from bs4 import BeautifulSoup
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from loguru import logger

from .loaders import load_singlefile_html
from .loaders import load_video_transcript
from .loaders import load_youtube_transcript

DEFAULT_HEADERS = {
    "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    "Cookie": "over18=1",  # ptt
}


DEFAULT_LANGUAGE_CODES = ["zh-TW", "zh-Hant", "zh", "zh-Hans", "ja", "en"]

DOMAIN_REPLACEMENTS = {
    # "twitter.com": "vxtwitter.com",
    # "x.com": "fixvx.com",
    # "twitter.com": "twittpr.com",
    # "x.com": "fixupx.com",
    "twitter.com": "api.fxtwitter.com",
    "x.com": "api.fxtwitter.com",
}


def is_pdf(url: str) -> bool:
    resp = httpx.head(url=url, headers=DEFAULT_HEADERS, follow_redirects=True)
    resp.raise_for_status()
    return resp.headers.get("content-type") == "application/pdf"


def load_pdf(url: str) -> str:
    resp = httpx.get(url=url, headers=DEFAULT_HEADERS, follow_redirects=True)
    resp.raise_for_status()

    suffix = ".pdf" if resp.headers.get("content-type") == "application/pdf" else None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        fp.write(resp.content)

    return docs_to_str(PyPDFLoader(fp.name).load())


def detect_encoding(byte_str: bytes) -> str:
    result = chardet.detect(byte_str)
    encoding = result["encoding"]
    if not encoding:
        return "utf-8"
    return encoding


def load_html_bs(url: str) -> str:
    resp = httpx.get(url, headers=DEFAULT_HEADERS)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")
    text = soup.get_text(strip=True)
    return text


def httpx_download(url: str) -> str:
    resp = httpx.get(url=url, headers=DEFAULT_HEADERS, follow_redirects=True)
    resp.raise_for_status()

    suffix = ".pdf" if resp.headers.get("content-type") == "application/pdf" else None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        fp.write(resp.content)
        return fp.name


def parse_url(s: str) -> str:
    url_pattern = r"https?://[^\s]+"

    match = re.search(url_pattern, s)
    if match:
        return match.group(0)

    return ""


def docs_to_str(docs: list[Document]) -> str:
    return "\n".join([doc.page_content.strip() for doc in docs])


def is_youtube_url(url: str) -> bool:
    return (
        url.startswith("https://www.youtube.com")
        or url.startswith("https://youtu.be")
        or url.startswith("https://m.youtube.com")
    )


def load_document(url: str) -> str:
    # https://python.langchain.com/docs/integrations/document_loaders/

    if is_youtube_url(url):
        transcript = load_youtube_transcript(url)
        if transcript:
            return transcript
        logger.info("No transcript found for YouTube video: {}", url)

        # if the video has no transcripts
        # download the video and transcribe it by whisper
        transcript = load_video_transcript(url)
        if transcript:
            return transcript
        logger.info("Unable to load video transcript for YouTube video: {}", url)

    # replace domain
    url = replace_domain(url)

    if is_pdf(url):
        return load_pdf(url)

    # download the page and convert it to text
    return load_singlefile_html(url)


def ai_message_repr(ai_message: AIMessage) -> str:
    content: str | list[str | dict] = ai_message.content
    if isinstance(content, str):
        return content

    contents = []
    for item in content:
        if isinstance(item, str):
            contents.append(f"• {item}")

        if isinstance(item, dict):
            for k, v in item.items():
                contents.append(f"• {k}: {v}")

    return "\n".join(contents)


def replace_domain(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.netloc in DOMAIN_REPLACEMENTS:
        new_netloc = DOMAIN_REPLACEMENTS[parsed_url.netloc]
        fixed_url = parsed_url._replace(netloc=new_netloc)
        return urlunparse(fixed_url)

    return url


@functools.cache
def get_telegraph_client() -> telegraph.Telegraph:
    client = telegraph.Telegraph()
    client.create_account(short_name="Narumi's Bot")
    return client


def create_page(title: str, **kwargs) -> str:
    client = get_telegraph_client()

    resp = client.create_page(title=title, **kwargs)
    return resp["url"]
