import inspect

from lazyopenai import generate


def translate_to_taiwanese(text: str) -> str:
    prompt = f"""
    你是翻譯專家，你會適當的保留專有名詞，並確保翻譯的準確性。將以下的文字翻譯成台灣繁體中文：

    {text}
    """
    return generate(inspect.cleandoc(prompt))


def translate(text: str, lang: str) -> str:
    user_prompt = f'"""{text}"""'

    system_prompt = f"""
    Translate the text delimited by triple quotation marks into {lang}.
    """.strip()
    return generate(user_prompt, system=system_prompt).strip('"')


def translate_and_explain(text: str, lang: str) -> str:
    user_prompt = f'"""{text}"""'

    system_prompt = f"""
    Translate the text delimited by triple quotation marks into {lang}, and provide a concise explanation of grammar and usage in {lang}, along with example sentences to enhance understanding."
    """.strip()  # noqa
    return generate(user_prompt, system=system_prompt).strip('"')
