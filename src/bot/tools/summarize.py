from pydantic import BaseModel

from ..llm import Message
from ..llm import aparse
from ..utils import save_text

SYSTEM_PROMPT = """
請以台灣繁體中文簡潔地總結以下內容的重點。限制最多 10 條，每條不超過 50 字。內容來源可包括網頁、文章、論文、影片字幕或逐字稿。

# 步驟
1. 提取內容中的關鍵重點，確保每個重點清晰且代表核心重點。
2. 如果有相似或重複的內容，請合併成一條重點。
3. 每條重點應簡短明確，使用符合台灣用語習慣的表達。
4. 最多列出 10 條，每條不超過 50 字。
5. 在總結後加上至少三個相關英文 hashtag，用空格分隔（如 #Sustainability、#Innovation）。

# 範例
輸入：
台灣的報告指出，環境保護的重要性日益增加。許多人開始選擇使用可重複使用的產品。政府也實施了多項政策來降低廢物。

輸出：
- 環境保護的重要性上升，更多人選擇可重複使用產品
- 政府推行減少廢物的政策
#EnvironmentalProtection #Sustainability #Taiwan
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
    messages: list[Message] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"輸入：\n{text}",
        },
    ]

    if question:
        messages += [
            {
                "role": "user",
                "content": f"問題：\n{question}",
            }
        ]
    try:
        summary = await aparse(messages, response_format=Summary)
        return str(summary)
    except Exception as e:
        save_text(text, "message_text.txt")
        raise e
