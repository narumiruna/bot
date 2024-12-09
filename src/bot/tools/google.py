import httpx
from lazyopenai.types import BaseTool
from markdownify import markdownify as md
from pydantic import Field


class GoogleSearch(BaseTool):
    """A tool to perform Google searches and return the results as markdown.

    This tool sends a GET request to Google's search API with the provided keywords,
    retrieves the HTML content, and converts it to markdown format.
    """

    keywords: list[str] = Field(..., description="A list of keywords to search for on Google.")

    def __call__(self) -> str:
        """Executes the search and returns the results in markdown format."""
        resp = httpx.get(url="https://www.google.com/search", params={"q": " ".join(self.keywords)})
        resp.raise_for_status()
        return md(resp.text, strip=["a", "img"]).strip()
