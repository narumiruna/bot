from agents import function_tool

from ...callbacks.utils import async_load_url


@function_tool
async def extract_content(url: str) -> str:
    """Extract the main content from a webpage.

    Args:
        url: The URL of the webpage to extract the content from.

    Returns:
        The extracted content as a string.
    """

    content = await async_load_url(url)
    return content
