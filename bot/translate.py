import functools

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable

from .utils import ai_message_repr
from .utils import get_llm_from_env

PROMPT_TEMPLATE = """翻譯文本為{lang}，並提供簡潔的文法和用法說明，搭配範例句子以增強理解。

文本：
{text}

翻譯："""  # noqa


@functools.cache
def get_chain() -> RunnableSerializable:
    llm = get_llm_from_env()
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    return chain


def translate(text: str, lang: str = "日文") -> str:
    chain = get_chain()
    ai_message: AIMessage = chain.invoke({"text": text, "lang": lang})
    return ai_message_repr(ai_message)
