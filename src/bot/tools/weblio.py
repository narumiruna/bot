import httpx
import logfire
from agents import function_tool
from bs4 import BeautifulSoup


@function_tool
def query_weblio(query: str) -> str:
    """Fetches the definitions of the query Japanese word from Weblio.

    Args:
        query (str): The Japanese word you want to search for in Weblio.

    Returns:
        str: A string containing the definitions of the word.
    """
    logfire.info(f"Querying Weblio for {query}")

    url = f"https://www.weblio.jp/content/{query}"
    response = httpx.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    res = []
    definitions = soup.find_all("div", class_="kiji")
    for definition in definitions:
        res.append(definition.text.strip())
    return "\n".join(res)
