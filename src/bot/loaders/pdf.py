from pathlib import Path

from pypdf import PdfReader


def load_pdf_file(f: str | Path) -> str:
    texts = []
    with PdfReader(f) as reader:
        texts = [page.extract_text(extraction_mode="plain") for page in reader.pages]
    return "\n".join(texts)
