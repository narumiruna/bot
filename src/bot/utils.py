import functools
import re
from pathlib import Path

import telegraph
from loguru import logger


def save_text(text: str, f: str) -> None:
    """Save text content to a file.

    Args:
        text: The text content to save.
        f: The file path where the text should be saved.

    Raises:
        OSError: If there's an error writing to the file.
    """
    try:
        path = Path(f)
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(text)
    except OSError as e:
        logger.error("Failed to save text to {}: {}", f, str(e))
        raise


def parse_url(s: str) -> str:
    """Extract the first URL from a string.

    Args:
        s: The input string to parse.

    Returns:
        str: The extracted URL, or an empty string if no URL is found.
    """
    if not s:
        return ""

    url_pattern = r"https?://[^\s]+"
    match = re.search(url_pattern, s)
    return match.group(0) if match else ""


@functools.cache
def get_telegraph_client() -> telegraph.Telegraph:
    """Get or create a cached Telegraph client instance.

    Returns:
        telegraph.Telegraph: A configured Telegraph client.

    Raises:
        telegraph.TelegraphException: If client creation or account creation fails.
    """
    try:
        client = telegraph.Telegraph()
        client.create_account(short_name="Narumi's Bot")
        return client
    except telegraph.TelegraphException as e:
        logger.error("Failed to create Telegraph client: {}", str(e))
        raise


def create_page(title: str, **kwargs) -> str:
    """Create a Telegraph page with the given title and content.

    Args:
        title: The title for the Telegraph page.
        **kwargs: Additional arguments to pass to Telegraph's create_page method.

    Returns:
        str: The URL of the created Telegraph page.

    Raises:
        telegraph.TelegraphException: If page creation fails.
        ValueError: If the title is empty or invalid.
    """
    if not title or not title.strip():
        raise ValueError("Page title cannot be empty")

    try:
        client = get_telegraph_client()
        resp = client.create_page(title=title, **kwargs)
        if not resp.get("url"):
            raise ValueError("Failed to get page URL from Telegraph response")
        return resp["url"]
    except (telegraph.TelegraphException, ValueError) as e:
        logger.error("Failed to create Telegraph page: {}", str(e))
        raise
