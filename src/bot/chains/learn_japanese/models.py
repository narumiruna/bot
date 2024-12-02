from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class DifficultyLevel(str, Enum):
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4_N5 = "N4-N5"

    def get_emoji(self) -> str:
        return {
            DifficultyLevel.N1: "🔴",
            DifficultyLevel.N2: "🟡",
            DifficultyLevel.N3: "🟢",
            DifficultyLevel.N4_N5: "⚪",
        }[self]


class ExampleSentence(BaseModel):
    japanese: str = Field(..., description="日文範例句子")
    chinese: str = Field(..., description="對應的繁體中文翻譯")

    def __str__(self) -> str:
        return f"    ⋮ 日：{self.japanese}\n    ⋮ 中：{self.chinese}"


class VocabularyItem(BaseModel):
    word: str = Field(..., description="單字/語彙")
    reading: str = Field(..., description="假名讀音")
    difficulty: DifficultyLevel = Field(..., description="JLPT難度等級")
    original: str = Field(..., description="原文中出現的形式")
    explanation: str = Field(..., description="詳細解釋與用法說明")
    example_sentences: list[ExampleSentence] = Field(default_factory=list, description="相關例句列表")

    def __str__(self) -> str:
        examples = "\n".join(str(ex) for ex in self.example_sentences)
        emoji = self.difficulty.get_emoji()
        return (
            f"【詞彙】 {self.word}（{self.reading}） {emoji} {self.difficulty.value}\n"
            f"┣━━ 原文：{self.original}\n"
            f"┣━━ 解釋：{self.explanation}\n"
            f"┗━━ 例句\n{examples}"
        )


class GrammarItem(BaseModel):
    grammar_pattern: str = Field(..., description="文法句型")
    difficulty: DifficultyLevel = Field(..., description="JLPT難度等級")
    original: str = Field(..., description="原文中出現的形式")
    explanation: str = Field(..., description="文法的基本意思和功能說明")
    conjugation: str = Field(..., description="接續變化規則")
    usage: str = Field(..., description="使用場合與注意事項")
    comparison: str = Field(..., description="與相似文法的比較")
    example_sentences: list[ExampleSentence] = Field(default_factory=list, description="示例句子列表")

    def __str__(self) -> str:
        examples = "\n".join(str(ex) for ex in self.example_sentences)
        emoji = self.difficulty.get_emoji()
        return (
            f"【文法】 {self.grammar_pattern} {emoji} {self.difficulty.value}\n"
            f"┣━━ 原文：{self.original}\n"
            f"┣━━ 解釋：{self.explanation}\n"
            f"┣━━ 接續：{self.conjugation}\n"
            f"┣━━ 場合：{self.usage}\n"
            f"┣━━ 比較：{self.comparison}\n"
            f"┗━━ 例句\n{examples}"
        )


class JLPTResponse(BaseModel):
    vocabulary_section: list[VocabularyItem] = Field(default_factory=list, description="詞彙分析區段")
    grammar_section: list[GrammarItem] = Field(default_factory=list, description="文法分析區段")

    def __str__(self) -> str:
        vocab_section = "\n\n".join(str(v) for v in self.vocabulary_section)
        grammar_section = "\n\n".join(str(g) for g in self.grammar_section)

        return (
            "⭒⭒⭒⭒⭒⭒⭒⭒⭒⭒ 📚 詞彙分析 ⭒⭒⭒⭒⭒⭒⭒⭒⭒⭒\n\n"
            f"{vocab_section}\n\n"
            "⭒⭒⭒⭒⭒⭒⭒⭒⭒⭒ 📓 文法分析 ⭒⭒⭒⭒⭒⭒⭒⭒⭒⭒\n\n"
            f"{grammar_section}"
        )
