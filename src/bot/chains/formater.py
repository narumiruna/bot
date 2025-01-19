from typing import cast

from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field

from .translation import translate_to_taiwanese


class FormatResponse(BaseModel):
    title: str = Field(..., description="The main title for the document.")
    content: str = Field(..., description="Markdown content representing the formatted, normalized document.")


def format(text: str, lang: str = "台灣話") -> FormatResponse:
    response = cast(
        FormatResponse,
        generate(
            f'"""{text}"""',
            system=f"Provide a well-structured and properly normalized version of the text in Markdown format with {lang}.",  # noqa: E501
            response_format=FormatResponse,
        ),
    )

    return FormatResponse(
        title=translate_to_taiwanese(response.title),
        content=translate_to_taiwanese(response.content),
    )
