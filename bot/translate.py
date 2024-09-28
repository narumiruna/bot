import functools

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable

from .utils import ai_message_repr
from .utils import get_llm_from_env

PROMPT_TEMPLATE = """翻譯以下文字為{lang}：{text}"""


@functools.cache
def get_chain() -> RunnableSerializable:
    llm = get_llm_from_env()
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    return chain


def translate(text: str, lang: str) -> str:
    chain = get_chain()
    ai_message: AIMessage = chain.invoke({"text": text, "lang": lang})
    return ai_message_repr(ai_message)
