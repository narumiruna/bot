from lazyopenai import generate
from pydantic import BaseModel

from .prompt import SUMMARY_PROMPT


class Summary(BaseModel):
    lines: list[str]
    hashtags: list[str]

    def __str__(self) -> str:
        lines = []

        for line in self.lines:
            lines += [f"- {line}"]

        return "\n".join(lines) + f"\n{' '.join(self.hashtags)}"


def summarize(text: str) -> str:
    return str(
        generate(
            SUMMARY_PROMPT.format(text=text),
            response_format=Summary,
        )
    )
