from dotenv import find_dotenv
from dotenv import load_dotenv

from .bot import Bot


def main():
    load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))
    Bot.from_env()
