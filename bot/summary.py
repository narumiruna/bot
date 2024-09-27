import functools

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_openai import ChatOpenAI




PROMPT_TEMPLATE = """請使用台灣用語的繁體中文撰寫以下文章的簡明重點摘要，並以條列式呈現：
{text}

摘要："""


@functools.cache
def get_chain() -> RunnableSerializable:
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    return chain


def summarize(text: str) -> str:
    chain = get_chain()
    ai_message: AIMessage = chain.invoke({"text": text})
    return ai_message.pretty_repr()
