from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat import ChatCompletionSystemMessageParam
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel

from ..openai import aparse
from ..utils import save_text

SYSTEM_PROMPT = """
請以台灣繁體中文簡潔地總結以下內容的重點。。內容來源可包括網頁、文章、論文、影片字幕或逐字稿。

# 步驟
1. 提取內容中的關鍵重點，確保每個重點清晰且代表核心重點。
2. 如果有相似或重複的內容，請合併成一條重點。
3. 每條重點應簡短明確，使用符合台灣用語習慣的表達。
4. 在總結後加上至少三個相關英文 hashtag，用空格分隔（如 #Sustainability、#Innovation）。
""".strip()  # noqa


class Summary(BaseModel):
    lines: list[str]
    hashtags: list[str]

    def __str__(self) -> str:
        lines = []

        for line in self.lines:
            lines += [f"- {line}"]

        return "\n".join(lines) + f"\n{' '.join(self.hashtags)}"


async def summarize(text: str, question: str | None = None) -> str:
    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT),
        ChatCompletionUserMessageParam(role="user", content=f"輸入：\n{text}"),
    ]

    if question:
        messages += [ChatCompletionUserMessageParam(role="user", content=f"問題：\n{question}")]

    try:
        summary = await aparse(messages, response_format=Summary)
        return str(summary)
    except Exception as e:
        save_text(text, "message_text.txt")
        raise e
