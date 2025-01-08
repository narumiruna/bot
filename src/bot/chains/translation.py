from lazyopenai import generate


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
