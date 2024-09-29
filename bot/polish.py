from langchain_core.messages import AIMessage

from .chain import get_chain
from .utils import ai_message_repr

PROMPT_TEMPLATE = """Polish the following text: {text}"""


def polish(text: str) -> str:
    chain = get_chain(PROMPT_TEMPLATE)
    ai_message: AIMessage = chain.invoke({"text": text})
    return ai_message_repr(ai_message)
