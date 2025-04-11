from __future__ import annotations

import markdown2
from agents import Agent
from agents import ModelSettings
from agents import Runner
from pydantic import BaseModel
from pydantic import Field

from ..model import get_openai_model
from ..utils import create_page

PROMPT_TEMPLATE = """
請以台灣繁體中文為以下內容生成：

- **推理過程**：提供一系列推理步驟，說明如何得出摘要、見解。
- **摘要**：對內容進行總結。
- **見解**：使用項目符號列出內容中的主要重點和重要啟示。
- **Hashtags**：提供至少三個與主題相關的英文 Hashtags，以空格分隔（例如 #Sustainability #Innovation）。

# 步驟
1. 保留核心訊息，確保每條重點表達清晰且準確，避免加入任何虛構或未經證實的資訊。適度保留細節，避免過度簡潔。
2. 若發現相似或重複的資訊，將其合併為一條重點，以保持內容連貫且流暢。
3. 使用符合台灣用語習慣的表達方式，排除不必要的細節，提高可讀性。
4. 翻譯摘要、見解成**繁體中文**，並確保用詞皆為台灣習慣。

輸入：
{text}
""".strip()  # noqa


class ThoughtStep(BaseModel):
    context: str = Field(..., description="此步驟考慮的具體情境或條件")
    reasoning: str = Field(..., description="此步驟推理過程的解釋")
    conclusion: str = Field(..., description="此步驟得出的中間結論")

    def __str__(self) -> str:
        return "\n\n".join(
            [
                f"  • <b>情境</b>: {self.context}",
                f"  • <b>推理</b>: {self.reasoning}",
                f"  • <b>結論</b>: {self.conclusion}",
            ]
        )


class ChainOfThought(BaseModel):
    steps: list[ThoughtStep] = Field(..., description="通往最終結論的一系列推理步驟")
    final_conclusion: str = Field(..., description="所有推理步驟後的最終結論")

    def __str__(self) -> str:
        steps = "\n\n".join([f"🔍 <b>步驟 {i + 1}</b>\n\n{step}" for i, step in enumerate(self.steps)])
        return "\n\n".join(
            [
                "🧠 <b>推理過程</b>",
                steps,
                "🎯 <b>最終結論</b>",
                self.final_conclusion,
            ]
        )


class Summary(BaseModel):
    chain_of_thought: ChainOfThought = Field(
        ...,
        description=("通往摘要、見解的推理過程，翻譯成台灣繁體中文。提供一系列推理步驟，說明如何得出摘要、見解。"),
    )
    summary_text: str = Field(
        ...,
        description="對文本的總結，翻譯成台灣繁體中文。保留核心訊息，確保每條重點表達清晰且準確，避免加入任何虛構或未經證實的資訊。",
    )
    insights: list[str] = Field(
        ..., description="從文本中提取的見解，翻譯成台灣繁體中文。使用項目符號列出內容中的主要重點和重要啟示。"
    )
    hashtags: list[str] = Field(
        ...,
        description="與文本相關的 Hashtags",
    )

    def __str__(self) -> str:
        insights = "\n".join([f"  • {insight.strip()}" for insight in self.insights])
        hashtags = " ".join(self.hashtags)

        url = create_page(title="推理過程", html_content=markdown2.markdown(str(self.chain_of_thought)))
        return "\n\n".join(
            [
                "📝 <b>摘要</b>",
                self.summary_text.strip(),
                "💡 <b>見解</b>",
                insights,
                f"🏷️ <b>Hashtags</b>: {hashtags}",
                f"🔗 <a href='{url}'>推理過程</a>",
            ]
        )


async def summarize(text: str) -> str:
    """Generate a summary of the given text.

    Args:
        text (str): The text to summarize.

    Returns:
        str: A formatted string containing the summary, key points, takeaways, and hashtags.
    """
    agent = Agent(
        "summary",
        output_type=Summary,
        model=get_openai_model(),
        model_settings=ModelSettings(temperature=0.0),
    )
    result = await Runner.run(
        agent,
        input=PROMPT_TEMPLATE.format(text=text),
    )
    return str(result.final_output)
