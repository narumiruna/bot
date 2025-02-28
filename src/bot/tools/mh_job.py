import random

from lazyopenai.types import BaseTool
from pydantic import Field

mh_jobs: list[str] = [
    "大劍 (グレートソード)",
    "太刀 (太刀)",
    "片手劍 (片手剣)",
    "雙劍 (双剣)",
    "槌 (ハンマー)",
    "狩獵笛 (狩猟笛)",
    "槍 (ランス)",
    "銃槍 (ガンランス)",
    "斬擊斧 (スラッシュアックス)",
    "充能斧 (チャージアックス)",
    "操蟲棍 (操虫棍)",
    "弓 (弓)",
    "輕弩 (ライトボウガン)",
    "重弩 (ヘビィボウガン)",
]


class MHJobSelector(BaseTool):
    """Monster Hunter job selection tool."""

    n: int = Field(..., description="Number of jobs to select.")

    def __call__(self) -> str:
        """Select n random Monster Hunter jobs."""
        res = []
        for i in range(self.n):
            job = random.choice(mh_jobs)
            res += [f"Job #{i + 1}: {job}"]
        return "\n".join(res)
