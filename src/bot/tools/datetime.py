from datetime import datetime

from lazyopenai.types import BaseTool


class GetCurrentTime(BaseTool):
    """
    A tool to get the current date and time formatted as a string.
    """

    def __call__(self) -> str:
        """
        Returns the current date and time as a string in the format 'YYYY-MM-DD HH:MM:SS'.

        :return: The current date and time as a formatted string.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
