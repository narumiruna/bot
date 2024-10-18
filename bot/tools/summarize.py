from ..llm import Message
from ..llm import acomplete
from ..utils import save_text

SYSTEM_PROMPT = """
請以台灣繁體中文簡潔地總結以下內容的重點，限制最多 10 條，每條不超過 50 字。來源可以是網頁、文章、論文、影片字幕或逐字稿。

# 步驟
1. 提取內容中的關鍵重點，考慮上下文，確保重點完整且具代表性。
2. 使用台灣用語整理成條列式，每條必須簡短明確。
3. 限制總結為 10 條以下，每條不超過 50 字。
4. 總結後加入至少三個相關的英文 hashtag（如 #Sustainability、#Innovation），以空格分隔。

# 範例
輸入：
台灣的報告指出，環境保護的重要性日益增加。許多人開始選擇使用可重複使用的產品。政府也實施了多項政策來降低廢物。

輸出：
- 環境保護的重要性上升
- 越來越多民眾選擇可重複產品
- 政府實施減廢政策
#EnvironmentalProtection #Sustainability #Taiwan
""".strip()  # noqa


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
        return await acomplete(messages)
    except Exception as e:
        save_text(text, "message_text.txt")
        raise e
