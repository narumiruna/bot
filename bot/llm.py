import functools
import os

from langchain_core.language_models.chat_models import BaseChatModel


@functools.cache
def get_llm_from_env() -> BaseChatModel:
    if "OPENAI_API_KEY" in os.environ:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    elif "GOOGLE_API_KEY" in os.environ:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    else:
        raise ValueError("No API key found in environment variables")
