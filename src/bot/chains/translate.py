from lazyopenai import generate


def translate(text: str, lang: str) -> str:
    user_prompt = f'"""{text}"""'

    translated = generate(user_prompt, system=f"Translate the text delimited by triple quotation marks into {lang}.")
    formatted = generate(translated, system=f"Normalize the text in {lang}.")
    return formatted


def translate_and_explain(text: str, lang: str) -> str:
    user_prompt = f'"""{text}"""'

    system_prompt = f"""
    Translate the text delimited by triple quotation marks into {lang}, and provide a concise explanation of grammar and usage in {lang}, along with example sentences to enhance understanding."
    """.strip()  # noqa
    return generate(user_prompt, system=system_prompt).strip('"')
