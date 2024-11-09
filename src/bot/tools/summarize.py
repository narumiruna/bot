from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat import ChatCompletionSystemMessageParam
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel

from ..openai import async_parse
from ..utils import save_text

# SYSTEM_PROMPT = """
# 請以台灣繁體中文簡潔地總結以下內容的重點。內容來源可包括網頁、文章、論文、影片字幕或逐字稿。

# # 步驟
# 1. 提取內容中的關鍵重點，確保每個重點清晰且代表核心重點。不要產生虛構內容或捏造事實。
# 2. 如果有相似或重複的內容，合併成一條重點。
# 3. 每條重點應簡短明確，使用符合台灣用語習慣的表達。
# 4. 在總結後加上至少三個相關英文 hashtag，用空格分隔（如 #Sustainability、#Innovation）。
# """.strip()  # noqa


SYSTEM_PROMPT = """
請以台灣繁體中文提取以下內容的核心重點。內容來源可能包括網頁、文章、論文、影片字幕或逐字稿。

# 指引
1. 保留核心訊息，確保每條重點表達清晰且準確，避免加入任何虛構或未經證實的資訊。內容不需過度簡潔，適當保留訊息的細節。
2. 若發現相似或重複的資訊，請將其合併為一條重點，以保持內容集中且流暢。
3. 確保每條重點符合台灣用語習慣，並排除不必要的細節，以提升可讀性。
4. 在總結完成後，添加至少三個與主題相關的英文 hashtag，以空格分隔（例如 #Sustainability #Innovation），便於後續標記和分類。
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
        summary = await async_parse(messages, response_format=Summary)
        return str(summary)
    except Exception as e:
        save_text(text, "message_text.txt")
        raise e
