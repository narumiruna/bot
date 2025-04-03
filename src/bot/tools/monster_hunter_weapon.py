import random

from agents import function_tool

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


@function_tool
def draw_monster_hunter_weapon(n: int) -> str:
    """Draw n Monster Hunter weapons and return their names.

    Args:
        n (int): Number of weapons to draw.
    """
    res = []
    for i in range(n):
        job = random.choice(monster_hunter_weapons)
        res += [f"Job #{i + 1}: {job}"]
    return "\n".join(res)
