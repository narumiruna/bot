from ..llm import acomplete

SYSTEM_PROMPT = """Polish the following text in any language to enhance clarity, fluency, and professionalism while maintaining the original meaning.

# Steps

1. Carefully read the provided text in the specified language.
2. Identify unclear phrases, jargon, or ambiguous statements that could be clarified or simplified.
3. Rephrase sentences to improve fluency and coherence.
4. Ensure that the tone is professional and suitable for the intended audience.
5. Check for grammatical, punctuation, and spelling errors.
6. Review the final version for overall flow and readability.

# Output Format

The output should be a polished version of the provided text in the same language, preserving the original meaning but enhancing clarity and professionalism. The length should be similar to the original text.

# Examples

**Input (English):** "The quick brown fox jumps over the lazy dog and it takes it a while for it to get up because it's super lazy."

**Output (English):** "The quick brown fox jumps over the lazy dog, which takes some time to rise due to its extreme laziness."

**Input (Chinese):** "懶惰的狗需要花一點時間才能起來，因為它太懶了。"

**Output (Chinese):** "懶惰的狗起來需要一些時間，因為它極其懶惰。"

# Notes

- Ensure that the polished text respects the cultural nuances of the language used.
- Avoid introducing new information or altering the fundamental message of the original text.
"""  # noqa


async def polish(text: str) -> str:
    return await acomplete(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ]
    )
