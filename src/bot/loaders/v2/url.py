from loguru import logger

from .cloudscraper import CloudscraperLoader
from .loader import Loader
from .singlefile import SinglefileLoader


class LoaderError(Exception):
    pass


class URLLoader:
    def __init__(self):
        self.loaders: list[Loader] = [
            CloudscraperLoader(),
            SinglefileLoader(),
        ]

    def add_loader(self, loader: Loader, index: int = -1) -> None:
        if index >= 0:
            self.loaders.insert(index, loader)
        else:
            self.loaders.append(loader)

    def load(self, url: str) -> str:
        for loader in self.loaders:
            try:
                return loader.load(url)
            except Exception as e:
                logger.error("Failed to load URL: {}", e)

        raise LoaderError(f"Failed to load URL: {url}")
