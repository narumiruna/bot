from langchain_core.messages import AIMessage

from .chain import get_chain
from .utils import ai_message_repr

PROMPT_TEMPLATE = """用台灣用語的繁體中文，簡潔地以條列式總結文章重點。
在摘要後直接加入相關的英文 hashtag，以空格分隔。

文章內容：
{text}

摘要："""  # noqa


def summarize(text: str) -> str:
    chain = get_chain(PROMPT_TEMPLATE)
    ai_message: AIMessage = chain.invoke({"text": text})
    return ai_message_repr(ai_message)
