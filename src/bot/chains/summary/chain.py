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


def summarize(text: str, question: str | None = None) -> str:
    prompt = f"輸入：\n{text}"
    if question:
        prompt += f"\n問題：\n{question}"

    summary = generate(
        prompt,
        system=SUMMARY_PROMPT,
        response_format=Summary,
    )
    return str(summary)
