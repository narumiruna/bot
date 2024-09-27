from dotenv import find_dotenv
from dotenv import load_dotenv

from .bot import Bot
from .utils import set_sqlite_llm_cache


def main():
    load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))
    set_sqlite_llm_cache()
    Bot.from_env()
