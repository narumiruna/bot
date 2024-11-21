from lazyopenai import generate


def translate(text: str, lang: str) -> str:
    user_prompt = f'"""{text}"""'

    system_prompt = f"""
    Translate the text delimited by triple quotes into {lang}.
    """.strip()
    return generate(user_prompt, system=system_prompt)


def translate_and_explain(text: str, lang: str) -> str:
    user_prompt = f'"""{text}"""'

    system_prompt = f"""
    Translate the text delimited by triple quotes into {lang}, and provide a concise explanation of grammar and usage, along with example sentences to enhance understanding."
    """.strip()  # noqa
    return generate(user_prompt, system=system_prompt)