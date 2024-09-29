from langchain_core.messages import AIMessage

from .chain import get_chain
from .utils import ai_message_repr

TRANSLATE_PROMPT_TEMPLATE = """翻譯以下文字為{lang}：

{text}"""

EXPLAIN_PROMPT_TEMPLATE = """翻譯以下文字為{lang}，並提供簡潔的文法和用法說明，搭配範例句子以增強理解：

{text}"""


def translate(text: str, lang: str) -> str:
    chain = get_chain(TRANSLATE_PROMPT_TEMPLATE)
    ai_message: AIMessage = chain.invoke({"text": text, "lang": lang})
    return ai_message_repr(ai_message)


def translate_and_explain(text: str, lang: str) -> str:
    chain = get_chain(EXPLAIN_PROMPT_TEMPLATE)
    ai_message: AIMessage = chain.invoke({"text": text, "lang": lang})
    return ai_message_repr(ai_message)
