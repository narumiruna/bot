from pydantic import BaseModel

from .utils import generate

SYSTEM_PROMPT = """
Extract the most relevant keywords from the provided text to use them for Google search.

# Steps
1. **Analyze the Text**: Carefully break down the given text and identify its core concepts.
2. **Identify Keywords**: Extract key terms, phrases, or concepts that represent the main idea. Focus on nouns or noun phrases. Avoid common words, like prepositions or articles, unless they are crucial for specificity.
3. **Rank by Relevance**: Prioritize keywords that are likely to yield the most targeted and meaningful search results.
4. **Combine Keywords for Optimal Search**: Arrange the selected keywords into a coherent search query, ensuring coverage of all important aspects of the text while avoiding redundancy.
""".strip()  # noqa


class Keywords(BaseModel):
    """Extract keywords from the text and use them as search query."""

    keywords: list[str]

    def __str__(self) -> str:
        return " ".join(self.keywords)


async def extract_keywords(text: str) -> str:
    keywords = await generate(
        f"Extract keywords from the following text:\n{text}",
        system=SYSTEM_PROMPT,
        response_format=Keywords,
    )
    return str(keywords)
