from lazyopenai import generate
from pydantic import BaseModel

SYSTEM_PROMPT = """
你是位專業的廚師，精通各式料理，熟悉各種食材的搭配。
使用繁體中文回答，確保回答符合台灣用語習慣。
""".strip()  # noqa


class InstructionStep(BaseModel):
    step_number: int
    instruction: str


class RecipeIngredient(BaseModel):
    name: str
    quantity: float
    unit: str


class Recipe(BaseModel):
    name: str
    ingredients: list[RecipeIngredient]
    instructions: list[InstructionStep]

    def __str__(self) -> str:
        s = f"\n🍳 {self.name}\n\n"

        s += "📋 食材：\n"
        for ingredient in self.ingredients:
            s += f"・{ingredient.name:<10} {ingredient.quantity:>4} {ingredient.unit}\n"

        s += "\n👨‍🍳 料理步驟：\n"
        for instruction in self.instructions:
            s += f"{instruction.step_number:>2}. {instruction.instruction}\n"

        s += "\n"
        return s


def generate_recipe(text: str) -> str:
    recipe = generate(
        text,
        system=SYSTEM_PROMPT,
        response_format=Recipe,
    )
    return str(recipe)
