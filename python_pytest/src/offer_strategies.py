"""Regras de cálculo das ofertas especiais (padrão Strategy)."""

import abc

from model_objects import Discount, Product


class IOfferStrategy(abc.ABC):
    """Contrato de uma oferta: calcula o desconto de um produto do carrinho."""

    @abc.abstractmethod
    def calculate_discount(
        self, product: Product, quantity: float, unit_price: float
    ) -> Discount | None:
        """Devolve o desconto do produto, ou None quando a oferta não se aplica."""


class PercentDiscountStrategy(IOfferStrategy):
    """Desconto percentual sobre o valor total do produto."""

    def __init__(self, percent: float) -> None:
        self._percent = percent

    def calculate_discount(
        self, product: Product, quantity: float, unit_price: float
    ) -> Discount | None:
        discount_amount = quantity * unit_price * self._percent / 100.0
        return Discount(product, f"{self._percent}% off", -discount_amount)
