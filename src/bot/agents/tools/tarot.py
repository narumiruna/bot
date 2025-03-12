import random

from agents import function_tool

tarot_cards: list[str] = [
    "🃏 愚者 (The Fool)",
    "🎭 魔術師 (The Magician)",
    "🔮 女祭司 (The High Priestess)",
    "👸 女皇 (The Empress)",
    "🤴 皇帝 (The Emperor)",
    "⛪ 教皇 (The Hierophant)",
    "💕 戀人 (The Lovers)",
    "🏎️ 戰車 (The Chariot)",
    "💪 力量 (Strength)",
    "🏮 隱者 (The Hermit)",
    "🎡 命運之輪 (Wheel of Fortune)",
    "⚖️ 正義 (Justice)",
    "🔗 吊人 (The Hanged Man)",
    "💀 死神 (Death)",
    "⚖️ 節制 (Temperance)",
    "😈 惡魔 (The Devil)",
    "🏰 塔 (The Tower)",
    "⭐ 星星 (The Star)",
    "🌙 月亮 (The Moon)",
    "🌞 太陽 (The Sun)",
    "🎺 審判 (Judgement)",
    "🌍 世界 (The World)",
]

orientations: list[str] = [
    "正位 (Upright)",
    "逆位 (Reversed)",
]


@function_tool
def draw_tarot_card(n: int) -> str:
    """Draw n tarot cards and return their names with orientations.

    Args:
        n (int): Number of cards to draw.
    """
    res = []
    for i in range(n):
        card = random.choice(tarot_cards)
        orientation = random.choice(orientations)
        res += [f"Card #{i + 1}: {card} ({orientation})"]
    return "\n".join(res)
