import tempfile
from pathlib import Path

import httpx
from loguru import logger
from pypdf import PdfReader


def load_pdf(url: str) -> str:
    """Load and extract text from a PDF at the given URL.

    Args:
        url: The URL of the PDF file to load.

    Returns:
        str: The extracted text content from the PDF.

    Raises:
        httpx.HTTPError: If the HTTP request fails.
        ValueError: If the URL is empty or invalid.
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")

    logger.info("Loading PDF from URL: {}", url)

    headers = {
        "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
        "Cookie": "over18=1",  # ptt
    }

    try:
        resp = httpx.get(url=url, headers=headers, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("Failed to download PDF from {}: {}", url, str(e))
        raise

    # Determine file suffix based on content type
    suffix = ".pdf" if resp.headers.get("content-type", "").lower() == "application/pdf" else None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
            fp.write(resp.content)
            return load_pdf_file(fp.name)
    except Exception as e:
        logger.error("Failed to process PDF content: {}", str(e))
        raise


def load_pdf_file(f: str | Path) -> str:
    """Extract text from a local PDF file.

    Args:
        f: Path to the PDF file, can be string or Path object.

    Returns:
        str: The extracted text content from the PDF.

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        ValueError: If the file is not a valid PDF.
    """
    if isinstance(f, str):
        f = Path(f)

    if not f.exists():
        raise FileNotFoundError(f"PDF file not found: {f}")

    try:
        texts = []
        with PdfReader(f) as reader:
            texts = [page.extract_text(extraction_mode="plain") or "" for page in reader.pages]
        # Filter out empty pages and join with newlines
        return "\n".join(text for text in texts if text.strip())
    except Exception as e:
        logger.error("Failed to read PDF file {}: {}", f, str(e))
        raise ValueError(f"Invalid or corrupted PDF file: {f}") from e
