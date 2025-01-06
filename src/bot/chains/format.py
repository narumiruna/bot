from lazyopenai import generate


def format(text: str, lang: str = "台灣話") -> str:
    return generate(
        f'"""{text}"""',
        system=f"Format and normalize the document in Markdown format with {lang}.",
    ).strip('"')
