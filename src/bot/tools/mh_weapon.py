import random

from lazyopenai.types import BaseTool
from pydantic import Field

monster_hunter_weapons: list[str] = [
    "大剣 (大剣)",
    "太刀 (太刀)",
    "單手劍 (片手剣)",
    "雙劍 (双剣)",
    "大錘 (ハンマー)",
    "狩獵笛 (狩猟笛)",
    "長槍 (ランス)",
    "銃槍 (ガンランス)",
    "斬擊斧 (スラッシュアックス)",
    "充能斧 (チャージアックス)",
    "操蟲棍 (操虫棍)",
    "輕弩槍 (ライトボウガン)",
    "重弩槍 (ヘビィボウガン)",
    "弓 (弓)",
]


class MHWeaponSelector(BaseTool):
    """Monster Hunter weapon selection tool."""

    n: int = Field(..., description="Number of weapons to select.")

    def __call__(self) -> str:
        """Select n random Monster Hunter weapons."""
        res = []
        for i in range(self.n):
            job = random.choice(monster_hunter_weapons)
            res += [f"Job #{i + 1}: {job}"]
        return "\n".join(res)
