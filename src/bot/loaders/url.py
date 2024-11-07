from urllib.parse import urlparse
from urllib.parse import urlunparse

import httpx
from loguru import logger

from .html import load_html_with_cloudscraper
from .html import load_html_with_httpx
from .html import load_html_with_singlefile
from .pdf import load_pdf
from .video_transcript import load_video_transcript
from .youtube_transcript import load_youtube_transcript


def is_pdf_url(url: str) -> bool:
    headers = {
        "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    }

    resp = httpx.head(url=url, headers=headers, follow_redirects=True)
    resp.raise_for_status()
    return resp.headers.get("content-type") == "application/pdf"


def is_youtube_url(url: str) -> bool:
    return (
        url.startswith("https://www.youtube.com")
        or url.startswith("https://youtu.be")
        or url.startswith("https://m.youtube.com")
    )


def is_instagram_reel_url(url: str) -> bool:
    return url.startswith("https://www.instagram.com/reel/")


def replace_domain(url: str) -> str:
    replacements = {
        # "twitter.com": "vxtwitter.com",
        # "x.com": "fixvx.com",
        # "twitter.com": "twittpr.com",
        # "x.com": "fixupx.com",
        "twitter.com": "api.fxtwitter.com",
        "x.com": "api.fxtwitter.com",
    }

    parsed_url = urlparse(url)
    if parsed_url.netloc in replacements:
        new_netloc = replacements[parsed_url.netloc]
        fixed_url = parsed_url._replace(netloc=new_netloc)
        return urlunparse(fixed_url)

    return url


async def load_url(url: str) -> str:
    url = replace_domain(url)

    transcript = await load_transcript(url)
    if transcript:
        return transcript

    pdf_content = await load_pdf_content(url)
    if pdf_content:
        return pdf_content

    html_content = await load_html_content(url)
    return html_content


async def load_transcript(url: str) -> str | None:
    if is_instagram_reel_url(url):
        transcript = load_video_transcript(url)
        if transcript:
            return transcript
        logger.info("No transcript found for Instagram reel: {}", url)

    if is_youtube_url(url):
        transcript = load_youtube_transcript(url)
        if transcript:
            return transcript
        logger.info("No transcript found for YouTube video: {}", url)

        transcript = load_video_transcript(url)
        if transcript:
            return transcript
        logger.info("Unable to load video transcript for YouTube video: {}", url)

    return None


async def load_pdf_content(url: str) -> str | None:
    try:
        if is_pdf_url(url):
            return load_pdf(url)
    except httpx.HTTPStatusError as e:
        logger.error("Unable to load PDF: {} ({})", url, e)
    return None


async def load_html_content(url: str) -> str:
    httpx_domains = [
        "https://www.ptt.cc/bbs",
        "https://ncode.syosetu.com",
        "https://pubmed.ncbi.nlm.nih.gov",
        "https://www.bnext.com.tw",
        "https://github.com",
        "https://www.twreporter.org",
        "https://telegra.ph",
    ]
    for domain in httpx_domains:
        if url.startswith(domain):
            return load_html_with_httpx(url)

    cloudscraper_domains = [
        "https://blog.tripplus.cc",
        # "https://cloudflare.net",
    ]
    for domain in cloudscraper_domains:
        if url.startswith(domain):
            return load_html_with_cloudscraper(url)

    text = await load_html_with_singlefile(url)
    return text
