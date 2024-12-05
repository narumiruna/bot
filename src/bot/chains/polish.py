from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field


class PolishedText(BaseModel):
    polished_text: str = Field(..., description="The polished text.")
    detected_language: str = Field(..., description="The detected language of the input text.")

    def __str__(self) -> str:
        return self.polished_text


SYSTEM_PROMPT = """Your task is to **polish** the input text in any language to improve clarity, fluency, and professionalism while preserving the original meaning.

## Steps

1. Carefully read the provided text in its original language.
2. Identify unclear phrases, jargon, or ambiguous statements to clarify or simplify.
3. Rephrase sentences to enhance fluency and coherence.
4. Ensure the tone is professional and appropriate for the intended audience.
5. Correct grammatical, punctuation, and spelling errors.
6. Review the final version for overall flow and readability.

## Output Format

Provide a refined version of the text in the same language, maintaining the original meaning but enhancing clarity and professionalism. The length should be similar to the original text.

## Notes

- Respect the cultural nuances of the language used.
- Avoid introducing new information or altering the fundamental message of the original text.
"""  # noqa


def polish(text: str) -> str:
    return str(generate(f"Polish the following text:\n{text}", system=SYSTEM_PROMPT, response_format=PolishedText))
