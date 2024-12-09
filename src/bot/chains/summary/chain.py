from lazyopenai import generate
from pydantic import BaseModel

from .prompt import QA_PROMPT
from .prompt import SUMMARY_PROMPT


class Summary(BaseModel):
    lines: list[str]
    hashtags: list[str]

    def __str__(self) -> str:
        lines = []

        for line in self.lines:
            lines += [f"- {line}"]

        return "\n".join(lines) + f"\n{' '.join(self.hashtags)}"


def summarize(text: str, question: str | None = None) -> str:
    summary = generate(
        SUMMARY_PROMPT.format(text=text),
        response_format=Summary,
    )

    res = str(summary)

    if question:
        res += "\n\n" + str(generate(QA_PROMPT.format(text=text, question=question)))

    return res
