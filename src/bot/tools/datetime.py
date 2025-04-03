from datetime import datetime

from agents import function_tool


@function_tool
def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
