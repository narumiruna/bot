import markdown2
from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field

from ..utils import create_page
from .translate import translate

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
4. 確保最終輸出內容為台灣繁體中文。

輸入：
{text}
""".strip()  # noqa


class ThoughtStep(BaseModel):
    context: str = Field(..., description="The specific context or condition considered in this step.")
    reasoning: str = Field(..., description="An explanation of the reasoning process at this step.")
    conclusion: str = Field(..., description="The intermediate conclusion reached at this step.")

    def __str__(self) -> str:
        """Return a formatted string representation of the thought step."""
        return "\n\n".join(
            [
                f"  • Context: {self.context}",
                f"  • Reasoning: {self.reasoning}",
                f"  • Conclusion: {self.conclusion}",
            ]
        )


class ChainOfThought(BaseModel):
    steps: list[ThoughtStep] = Field(..., description="A list of reasoning steps leading to the final conclusion.")
    final_conclusion: str = Field(..., description="The final conclusion after all reasoning steps.")

    def __str__(self) -> str:
        """Return a formatted string representation of the chain of thought."""
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
    """Represents a summary of the text, including key points, takeaways, and hashtags."""

    chain_of_thought: ChainOfThought = Field(
        ..., description="The chain of thought leading to the summary, key points, and takeaways."
    )
    summary: str = Field(..., description="A concise summary of the text.")
    key_points: list[str] = Field(..., description="Key points extracted from the text.")
    takeaways: list[str] = Field(..., description="Important takeaways from the text.")
    hashtags: list[str] = Field(..., description="Relevant hashtags related to the text.")
    is_chinese: bool = Field(..., description="Whether the summary text is in Traditional Chinese or not.")

    def __str__(self) -> str:
        """Return a formatted string representation of the summary."""
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
    summary = generate(
        SUMMARY_PROMPT.format(text=text),
        response_format=Summary,
    )

    if summary.is_chinese:
        return str(summary)

    return translate(str(summary), "zh-TW")
