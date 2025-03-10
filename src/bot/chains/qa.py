from .utils import generate

QA_PROMPT = """
根據文章內容回答問題

# 步驟
1. 根據文章內容準確回答問題，確保答案清晰且準確，避免加入任何虛構或未經證實的資訊。
2. 如果文章中沒有直接回答，請根據相關資訊進行合理推斷，但不要編造答案。
3. 使用符合台灣用語習慣的表達方式，提高可讀性。
4. 確保最終輸出內容為台灣繁體中文。

問題：
{question}

文章：
{text}
""".strip()  # noqa


async def answer_question(text: str, question: str | None = None) -> str:
    return str(await generate(QA_PROMPT.format(text=text, question=question)))
