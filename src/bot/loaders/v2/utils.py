import charset_normalizer
from markdownify import markdownify


def html_to_markdown(content: str | bytes) -> str:
    """Convert HTML content to markdown format.

    Args:
        content: HTML content as string or bytes

    Returns:
        Converted markdown text with normalized whitespace
    """
    if isinstance(content, bytes):
        content = str(charset_normalizer.from_bytes(content).best())

    md = markdownify(content, strip=["a", "img"])
    lines = [line.strip() for line in md.splitlines() if line.strip()]
    return "\n".join(lines)
