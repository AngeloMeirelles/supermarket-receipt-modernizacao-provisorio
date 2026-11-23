from enum import Enum


class ProductUnit(Enum):
    EACH = 1
    KILO = 2


class SpecialOfferType(Enum):
    THREE_FOR_TWO = 1
    TEN_PERCENT_DISCOUNT = 2
    TWO_FOR_AMOUNT = 3
    FIVE_FOR_AMOUNT = 4


class Product:
    def __init__(self, name: str, unit: ProductUnit) -> None:
        self.name = name
        self.unit = unit


class ProductQuantity:
    def __init__(self, product: Product, quantity: float) -> None:
        self.product = product
        self.quantity = quantity


class Offer:
    def __init__(
        self, offer_type: SpecialOfferType, product: Product, argument: float
    ) -> None:
        self.offer_type = offer_type
        self.product = product
        self.argument = argument


class Discount:
    def __init__(
        self, product: Product, description: str, discount_amount: float
    ) -> None:
        self.product = product
        self.description = description
        self.discount_amount = discount_amount


class Bundle:
    """Combo promocional: conjunto de produtos diferentes com desconto."""

    def __init__(self, products: list[Product]) -> None:
        if len(products) < 2 or len(set(products)) != len(products):
            raise ValueError("a bundle needs at least two different products")
        self.products = list(products)
