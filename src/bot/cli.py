import os

import typer
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from .bot import run_bot


def configure_logfire() -> None:
    logfire_token = os.getenv("LOGFIRE_TOKEN")
    if logfire_token is not None:
        logger.info("Logfire token found, configuring logfire")

        import logfire

        logfire.configure()
        logger.configure(handlers=[logfire.loguru_handler()])


def main():
    load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))
    configure_logfire()
    typer.run(run_bot)
