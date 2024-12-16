import markdown2
from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field

from ..utils import create_page

SUMMARY_PROMPT = """
請以台灣繁體中文為以下內容生成：

- **Chain of Thought**：提供一系列推理步驟，說明如何得出摘要、關鍵重點和重要啟示。
- **摘要**：對內容進行簡要總結。
- **關鍵重點**：使用項目符號列出內容中的主要重點。
- **重要啟示**：使用引言格式列出從內容中獲得的重要啟示。
- **Hashtags**：提供至少三個與主題相關的英文 Hashtags，以空格分隔（例如 #Sustainability #Innovation）。

# 步驟
1. 保留核心訊息，確保每條重點表達清晰且準確，避免加入任何虛構或未經證實的資訊。適度保留細節，避免過度簡潔。
2. 若發現相似或重複的資訊，將其合併為一條重點，以保持內容連貫且流暢。
3. 使用符合台灣用語習慣的表達方式，排除不必要的細節，提高可讀性。
4. 翻譯摘要、關鍵重點和重要啟示成**繁體中文**，並確保用詞皆為台灣習慣。

輸入：
{text}
""".strip()  # noqa


class ThoughtStep(BaseModel):
    context: str = Field(..., description="此步驟考慮的具體情境或條件。")
    reasoning: str = Field(..., description="此步驟推理過程的解釋。")
    conclusion: str = Field(..., description="此步驟得出的中間結論。")

    def __str__(self) -> str:
        return "\n\n".join(
            [
                f"  • Context: {self.context}",
                f"  • Reasoning: {self.reasoning}",
                f"  • Conclusion: {self.conclusion}",
            ]
        )


class ChainOfThought(BaseModel):
    steps: list[ThoughtStep] = Field(..., description="通往最終結論的一系列推理步驟。")
    final_conclusion: str = Field(..., description="所有推理步驟後的最終結論。")

    def __str__(self) -> str:
        steps = "\n\n".join([f"🔍 Step {i + 1}\n\n{step}" for i, step in enumerate(self.steps)])
        return "\n\n".join(
            [
                "🧠 Chain of Thought",
                steps,
                "🎯 Final Conclusion",
                self.final_conclusion,
            ]
        )


class Summary(BaseModel):
    chain_of_thought: ChainOfThought = Field(
        ..., description="通往摘要、關鍵重點和重要啟示的推理過程，翻譯成台灣繁體中文。"
    )
    summary: str = Field(..., description="對文本的簡要總結，翻譯成台灣繁體中文。")
    key_points: list[str] = Field(..., description="從文本中提取的關鍵重點，翻譯成台灣繁體中文。")
    takeaways: list[str] = Field(..., description="從文本中獲得的重要啟示，翻譯成台灣繁體中文。")
    hashtags: list[str] = Field(..., description="與文本相關的 Hashtags。")

    def __str__(self) -> str:
        key_points = "\n".join([f"  • {point}" for point in self.key_points])
        takeaways = "\n".join([f"  💡 {takeaway}" for takeaway in self.takeaways])
        hashtags = " ".join(self.hashtags)

        url = create_page(title="Chain of Thought", html_content=markdown2.markdown(str(self.chain_of_thought)))
        return "\n\n".join(
            [
                "📝 Summary",
                self.summary,
                "🎯 Key Points",
                key_points,
                "💫 Takeaways",
                takeaways,
                f"🏷️ Hashtags: {hashtags}",
                f"🔗 <a href='{url}'>Chain of Thought</a>",
            ]
        )


def summarize(text: str) -> str:
    """Generate a summary of the given text.

    Args:
        text (str): The text to summarize.

    Returns:
        str: A formatted string containing the summary, key points, takeaways, and hashtags.
    """
    # return translate(
    #     str(
    #         generate(
    #             SUMMARY_PROMPT.format(text=text),
    #             response_format=Summary,
    #         )
    #     ),
    #     "zh-TW",
    # ).strip('"')
    return str(generate(SUMMARY_PROMPT.format(text=text), response_format=Summary))
