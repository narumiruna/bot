from ..llm import acomplete

TRANSLATE_SYSTEM_PROMPT = """翻譯文字為{lang}。"""

EXPLAIN_SYSTEM_PROMPT = """翻譯文字為{lang}，並提供簡潔的文法和用法說明，搭配範例句子以增強理解。"""


async def translate(text: str, lang: str) -> str:
    return await acomplete(
        [
            {
                "role": "system",
                "content": TRANSLATE_SYSTEM_PROMPT.format(lang=lang),
            },
            {
                "role": "user",
                "content": text,
            },
        ]
    )


async def translate_and_explain(text: str, lang: str) -> str:
    return await acomplete(
        [
            {
                "role": "system",
                "content": EXPLAIN_SYSTEM_PROMPT.format(lang=lang),
            },
            {
                "role": "user",
                "content": text,
            },
        ]
    )
