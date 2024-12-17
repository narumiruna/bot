import cloudscraper

from .loader import Loader
from .utils import convert_to_markdown


class CloudscraperLoader(Loader):
    def load(self, url: str) -> str:
        client = cloudscraper.create_scraper()
        response = client.get(url)
        response.raise_for_status()
        return convert_to_markdown(response.text)
