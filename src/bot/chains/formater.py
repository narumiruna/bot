from typing import cast

from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field


class FormatResponse(BaseModel):
    title: str = Field(..., description="The main title for the document.")
    content: str = Field(..., description="Markdown content representing the formatted, normalized document.")


def format(text: str, lang: str = "台灣話") -> FormatResponse:
    response = generate(
        f'"""{text}"""',
        system=f"Provide a well-structured and properly normalized version of the text in Telegraph Content format with {lang}.",  # noqa: E501
        response_format=FormatResponse,
    )
    return cast(FormatResponse, response)
