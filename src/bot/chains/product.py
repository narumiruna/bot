from typing import cast

from lazyopenai import generate
from pydantic import BaseModel
from pydantic import Field


class Price(BaseModel):
    amount: float
    currency: str = Field(..., description="Currency code, e.g. USD, EUR, etc.")

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"


class Product(BaseModel):
    name: str
    price: Price
    color: str
    url: str
    product_number: str
    features: list[str]

    def __str__(self) -> str:
        lines = [
            f"{'Product:':<10} {self.name} ({self.product_number})",
            f"{'Price:':<10} {self.price}",
            f"{'Color:':<10} {self.color}",
            f"{'URL:':<10} {self.url}",
        ]

        if self.features:
            lines += ["Features:"]
            lines += [f"  • {feature}" for feature in self.features]

        return "\n".join(lines)


class Products(BaseModel):
    products: list[Product]

    def __str__(self) -> str:
        return "\n\n".join(str(product) for product in self.products)


def extract_product(text: str) -> Products:
    response = generate(
        text,
        system="Use only the information directly provided in the context—do not fabricate or include placeholders.",  # noqa: E501
        response_format=Products,
    )
    return cast(Products, response)
