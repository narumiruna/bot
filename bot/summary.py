import functools

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable

from .utils import get_llm_from_env

PROMPT_TEMPLATE = """以台灣用語的繁體中文撰寫文章的重點摘要，使用條列式，每個條目簡潔聚焦於關鍵內容。
最後，根據文章內容創造準確反映主題與重點的英文 hashtag。直接呈現，不要加上 "Hashtags:" 或其他標題，並以空格分隔。

Hashtag 範例：
#Technology #Innovation #AI #MachineLearning #DeepLearning

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
