from dotenv import find_dotenv
from dotenv import load_dotenv

from .bot import Bot
from .utils import setup_cache


def main():
    setup_cache()
    load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))
    Bot.from_env()
