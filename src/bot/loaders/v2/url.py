from loguru import logger

from .cloudscraper import CloudscraperLoader
from .httpx import HttpxLoader
from .loader import Loader
from .loader import LoaderError
from .pdf import PDFLoader
from .singlefile import SinglefileLoader
from .youtube import YoutubeTranscriptLoader


class URLLoader(Loader):
    def __init__(self):
        self.loaders: list[Loader] = [
            YoutubeTranscriptLoader(),
            PDFLoader(),
            CloudscraperLoader(),
            HttpxLoader(),
            SinglefileLoader(),
        ]

    def add_loader(self, loader: Loader) -> None:
        self.loaders.append(loader)

    def load(self, url: str) -> str:
        for loader in self.loaders:
            try:
                return loader.load(url)
            except Exception as e:
                logger.error("Failed to load URL: {}", e)

        raise LoaderError(f"Failed to load URL: {url}")
