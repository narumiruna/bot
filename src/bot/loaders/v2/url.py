from loguru import logger

from .cloudscraper import CloudscraperLoader
from .loader import Loader
from .loader import LoaderError
from .singlefile import SinglefileLoader
from .youtube import YoutubeTranscriptLoader


class URLLoader:
    def __init__(self):
        self.loaders: list[Loader] = [
            CloudscraperLoader(),
            SinglefileLoader(),
        ]

        self.video_loaders: list[Loader] = [YoutubeTranscriptLoader()]

    def add_loader(self, loader: Loader, index: int = -1) -> None:
        if index >= 0:
            self.loaders.insert(index, loader)
        else:
            self.loaders.append(loader)

    def add_video_loader(self, loader: Loader, index: int = -1) -> None:
        if index >= 0:
            self.video_loaders.insert(index, loader)
        else:
            self.video_loaders.append(loader)

    def load_html(self, url: str) -> str:
        for loader in self.loaders:
            try:
                return loader.load(url)
            except Exception as e:
                logger.error("Failed to load URL: {}", e)

        raise LoaderError(f"Failed to load URL: {url}")

    def load_video(self, url: str) -> str:
        for loader in self.video_loaders:
            try:
                return loader.load(url)
            except Exception as e:
                logger.error("Failed to load video URL: {}", e)

        raise LoaderError(f"Failed to load video URL: {url}")

    def load(self, url: str) -> str:
        result = self.load_html(url)

        try:
            video_content = self.load_video(url)
            result += "\n" + video_content
        except LoaderError as e:
            logger.info("No video content found: {}", e)

        return result
