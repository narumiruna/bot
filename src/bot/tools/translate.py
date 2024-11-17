from lazyopenai import generate


def translate(text: str, lang: str) -> str:
    return generate(text, system=f"翻譯文字為{lang}。")


def translate_and_explain(text: str, lang: str) -> str:
    return generate(text, system=f"翻譯文字為{lang}，並提供簡潔的文法和用法說明，搭配範例句子以增強理解。")
