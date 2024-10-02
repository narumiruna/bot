import contextlib
import functools
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import urlunparse

import chardet
import httpx
import numpy as np
import whisper
import yt_dlp
from bs4 import BeautifulSoup
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.html_bs import BSHTMLLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from loguru import logger

DEFAULT_HEADERS = {
    "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    "Cookie": "over18=1",  # ptt
}


DOMAINS_DOWNLOADING_BY_SINGLEFILE = [
    "facebook.com",
    "www.threads.net",
]


DEFAULT_LANGUAGE_CODES = ["zh-TW", "zh-Hant", "zh", "zh-Hans", "ja", "en"]

DOMAIN_REPLACEMENTS = {
    # "twitter.com": "vxtwitter.com",
    # "x.com": "fixvx.com",
    # "twitter.com": "twittpr.com",
    # "x.com": "fixupx.com",
    "twitter.com": "api.fxtwitter.com",
    "x.com": "api.fxtwitter.com",
}

FFMPEG_LOCATION = "/opt/homebrew/bin/ffmpeg"


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

    resp.encoding = detect_encoding(resp.content)
    soup = BeautifulSoup(resp.text, "html.parser", from_encoding=resp.encoding)
    text = soup.get_text(strip=True)
    return text


def download_by_httpx(url: str) -> str:
    resp = httpx.get(url=url, headers=DEFAULT_HEADERS, follow_redirects=True)
    resp.raise_for_status()

    suffix = ".pdf" if resp.headers.get("content-type") == "application/pdf" else None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
        fp.write(resp.content)
        return fp.name


def download_by_singlefile(url: str, cookies_file: str | None = None) -> str:
    filename = tempfile.mktemp(suffix=".html")

    cmds = ["/Users/narumi/.local/bin/single-file"]

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
    return docs_to_str(BSHTMLLoader(filename).load())


def parse_url(s: str) -> str:
    url_pattern = r"https?://[^\s]+"

    match = re.search(url_pattern, s)
    if match:
        return match.group(0)

    return ""


def docs_to_str(docs: list[Document]) -> str:
    return "\n".join([doc.page_content.strip() for doc in docs])


def is_youtube_video_url(url: str) -> bool:
    return url.startswith("https://www.youtube.com/watch?v=") or url.startswith("https://youtu.be/")


def load_youtube_transcripts(url: str) -> str:
    with contextlib.suppress(ValueError):
        transcripts = docs_to_str(
            YoutubeLoader.from_youtube_url(
                url,
                add_video_info=True,
                language=DEFAULT_LANGUAGE_CODES,
            ).load()
        )
        logger.info("transcripts: {}", transcripts)
        if transcripts:
            return transcripts

    # if the video has no transcripts
    # download the video and transcribe it by whisper
    return load_transcribe_by_whisper(url)


def load_document(url: str) -> str:
    # https://python.langchain.com/docs/integrations/document_loaders/

    if is_youtube_video_url(url):
        return load_youtube_transcripts(url)

    # replace domain
    url = replace_domain(url)

    if is_pdf(url):
        return load_pdf(url)

    # download
    if urlparse(url).netloc in DOMAINS_DOWNLOADING_BY_SINGLEFILE:
        f = download_by_singlefile(url)
        return docs_to_str(BSHTMLLoader(f).load())
    else:
        return load_html_bs(url)


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


def download_by_ytdlp(url: str) -> str:
    filename = tempfile.mktemp()

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": filename,
        "ffmpeg_location": FFMPEG_LOCATION,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename + ".mp3"


def load_audio(file: str, sr: int = 16000):
    """
    Open an audio file and read as mono waveform, resampling as necessary

    Parameters
    ----------
    file: str
        The audio file to open

    sr: int
        The sample rate to resample the audio if necessary

    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """

    # This launches a subprocess to decode audio while down-mixing
    # and resampling as necessary.  Requires the ffmpeg CLI in PATH.
    # fmt: off
    cmd = [
        FFMPEG_LOCATION,
        "-nostdin",
        "-threads", "0",
        "-i", file,
        "-f", "s16le",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        "-ar", str(sr),
        "-"
    ]
    # fmt: on
    try:
        out = subprocess.run(cmd, capture_output=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


@functools.cache
def load_whisper_model() -> whisper.Whisper:
    return whisper.load_model("tiny")


@functools.cache
def load_transcribe_by_whisper(url: str) -> str:
    f = download_by_ytdlp(url)
    audio = load_audio(f)
    model = load_whisper_model()
    result = model.transcribe(audio)
    logger.info("transcribe result: {}", result)
    return str(result["text"])
