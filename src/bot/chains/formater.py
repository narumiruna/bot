from typing import cast

from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field


class FormatResponse(BaseModel):
    title: str = Field(..., description="The main title for the document.")
    content: str = Field(..., description="Markdown content representing the formatted, normalized document.")
    content_in_taiwanese: str = Field(
        ..., description="代表格式化、標準化文件的Markdown內容，使用台灣繁體中文，適當的保留專有名詞原文。"
    )  # noqa: E501


def format(text: str, lang: str = "台灣話") -> FormatResponse:
    response = generate(
        f'"""{text}"""',
        system=f"Provide a well-structured and properly normalized version of the text in Markdown format with {lang}.",  # noqa: E501
        response_format=FormatResponse,
    )
    return cast(FormatResponse, response)
