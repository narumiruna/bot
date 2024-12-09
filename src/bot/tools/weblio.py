import httpx
from bs4 import BeautifulSoup
from lazyopenai.types import BaseTool
from loguru import logger
from pydantic import Field


class Weblio(BaseTool):
    """A tool to fetch detailed explanations, usage, and related information of a Japanese word from Weblio."""

    query: str = Field(..., description="The Japanese word you want to search for in Weblio")

    def __call__(self) -> str:
        """
        Fetches the definitions of the query Japanese word from Weblio.

        Returns:
            str: A string containing the definitions of the word, separated by newlines.
        """
        logger.info(f"Querying Weblio for {self.query}")

        url = f"https://www.weblio.jp/content/{self.query}"
        response = httpx.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        res = []
        definitions = soup.find_all("div", class_="kiji")
        for definition in definitions:
            res.append(definition.text.strip())
        return "\n".join(res)
