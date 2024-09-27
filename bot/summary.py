import functools

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable

from .utils import get_llm_from_env

PROMPT_TEMPLATE = """以台灣用語的繁體中文撰寫以下文章的簡明重點摘要，並以條列式呈現，每個條目簡明扼要，聚焦於文章的關鍵內容。  
最後根據文章內容，創造並添加 3-5 個相關的英文 hashtag（例如：#Technology, #Innovation）。這些 hashtag 應準確反映文章的主題與重點。

文章內容：  
{text}

摘要："""  # noqa


@functools.cache
def get_chain() -> RunnableSerializable:
    llm = get_llm_from_env()
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    return chain


def summarize(text: str) -> str:
    chain = get_chain()
    ai_message: AIMessage = chain.invoke({"text": text})

    content: str | list[str | dict] = ai_message.content
    if isinstance(content, str):
        return content

    contents = []
    for item in content:
        if isinstance(item, str):
            contents.append(f"• {item}")

        if isinstance(item, dict):
            for k, v in item.items():
                contents.append(f"• {k}: {v}")

    return "\n".join(contents)
