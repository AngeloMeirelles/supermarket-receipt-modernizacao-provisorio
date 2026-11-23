"""Cálculo dos descontos de uma compra."""

from catalog import SupermarketCatalog
from model_objects import Discount, Offer, Product
from offer_strategy_factory import OfferStrategyFactory


class DiscountCalculator:
    """Calcula os descontos de um carrinho com base nas ofertas cadastradas."""

    def __init__(self, catalog: SupermarketCatalog) -> None:
        self._catalog = catalog

    def product_discounts(
        self, product_quantities: dict[Product, float], offers: dict[Product, Offer]
    ) -> list[Discount]:
        """Descontos das ofertas por produto, na ordem em que entraram no carrinho."""
        discounts = []
        for product, quantity in product_quantities.items():
            if product not in offers:
                continue

            strategy = OfferStrategyFactory.create(offers[product])
            discount = strategy.calculate_discount(
                product, quantity, self._catalog.unit_price(product)
            )
            if discount is not None:
                discounts.append(discount)
        return discounts
