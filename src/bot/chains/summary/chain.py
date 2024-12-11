import markdown2
from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field

from ...utils import create_page
from .prompt import SUMMARY_PROMPT


class ThoughtStep(BaseModel):
    context: str = Field(..., description="The specific context or condition being evaluated in this step.")
    reasoning: str = Field(..., description="Explanation of the reasoning process at this step.")
    conclusion: str = Field(..., description="Intermediate conclusion reached at this step.")

    def __str__(self) -> str:
        """Returns a formatted string representation of the thought step."""
        return "\n\n".join(
            [
                f"  • Context: {self.context}",
                f"  • Reasoning: {self.reasoning}",
                f"  • Conclusion: {self.conclusion}",
            ]
        )


class ChainOfThought(BaseModel):
    steps: list[ThoughtStep] = Field(..., description="A list of reasoning steps leading to the final conclusion.")
    final_conclusion: str = Field(..., description="The final conclusion reached after all reasoning steps.")

    def __str__(self) -> str:
        """Returns a formatted string representation of the chain of thought."""
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
    """A model representing the summary of a text, including key points, takeaways, and hashtags."""

    chain_of_thoughts: list[ChainOfThought] = Field(
        ..., description="A list of chains of thought leading to the summary, key points, and takeaways."
    )
    summary: str = Field(..., description="A concise summary of the text.")
    key_points: list[str] = Field(..., description="A list of key points extracted from the text.")
    takeaways: list[str] = Field(..., description="Important takeaways from the text.")
    hashtags: list[str] = Field(..., description="Relevant hashtags related to the text.")

    def __str__(self) -> str:
        """Returns a formatted string representation of the summary."""
        key_points = "\n".join([f"  • {point}" for point in self.key_points])
        takeaways = "\n".join([f"  💡 {takeaway}" for takeaway in self.takeaways])
        hashtags = " ".join(self.hashtags)

        url = create_page(
            title="Chain of Thought",
            html_content=markdown2.markdown("\n\n".join([str(cot) for cot in self.chain_of_thoughts])),
        )

        return "\n\n".join(
            [
                "📝 Summary",
                self.summary,
                "🎯 Key Points",
                key_points,
                "💫 Takeaways",
                takeaways,
                f"🏷️ Tags: {hashtags}",
                f"🔗 Chain of Thought: {url}",
            ]
        )


def summarize(text: str) -> str:
    """Generates a summary of the given text.

    Args:
        text (str): The text to be summarized.

    Returns:
        str: A formatted string containing the summary, key points, takeaways, and hashtags.
    """
    return str(
        generate(
            SUMMARY_PROMPT.format(text=text),
            response_format=Summary,
        )
    )
