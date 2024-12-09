from lazyopenai import generate

from .prompt import QA_PROMPT


def answer_question(text: str, question: str | None = None) -> str:
    return str(generate(QA_PROMPT.format(text=text, question=question)))
