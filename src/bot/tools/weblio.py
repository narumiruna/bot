import httpx
from bs4 import BeautifulSoup
from lazyopenai.types import BaseTool
from loguru import logger
from pydantic import Field


class Weblio(BaseTool):
    """您可以直接查看該詞彙的詳細解釋、用法和相關資訊。"""

    query: str = Field(..., description="The word you want to search for in Weblio")

    def __call__(self) -> str:
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
