from urllib.parse import urlparse
from urllib.parse import urlunparse

from loguru import logger

from .cloudscraper import CloudscraperLoader
from .httpx import HttpxLoader
from .loader import Loader
from .loader import LoaderError
from .pdf import PDFLoader
from .singlefile import SinglefileLoader
from .youtube import YoutubeTranscriptLoader
from .ytdlp import YtdlpLoader

REPLACEMENTS = {
    "api.fxtwitter.com": [
        "twitter.com",
        "x.com",
        "fxtwitter.com",
        "vxtwitter.com",
        "fixvx.com",
        "twittpr.com",
        "fixupx.com",
    ]
}


def replace_domain(url: str) -> str:
    parsed = urlparse(url)
    for target, source in REPLACEMENTS.items():
        if parsed.netloc in source:
            fixed_url = parsed._replace(netloc=target)
            return urlunparse(fixed_url)
    return url


class URLLoader(Loader):
    def __init__(self):
        self.loaders: list[Loader] = [
            YoutubeTranscriptLoader(),
            YtdlpLoader(),
            PDFLoader(),
            CloudscraperLoader(),
            HttpxLoader(),
            SinglefileLoader(),
        ]

    def add_loader(self, loader: Loader) -> None:
        self.loaders.append(loader)

    def load(self, url: str) -> str:
        url = replace_domain(url)

        for loader in self.loaders:
            try:
                return loader.load(url)
            except Exception as e:
                logger.error("Failed to load URL: {}", e)

        raise LoaderError(f"Failed to load URL: {url}")
