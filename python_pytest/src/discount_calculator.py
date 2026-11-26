from catalog import SupermarketCatalog
from model_objects import Discount, Offer, Product
from offer_strategy_factory import OfferStrategyFactory


class DiscountCalculator:
    def __init__(self, catalog: SupermarketCatalog) -> None:
        self._catalog = catalog

    def offer_discounts(self, product_quantities: dict[Product, float], offers: dict[Product, Offer]) -> list[Discount]:
        discounts: list[Discount] = []
        for product, quantity in product_quantities.items():
            if product in offers:
                unit_price = self._catalog.unit_price(product)
                strategy = OfferStrategyFactory.create(offers[product])
                if strategy:
                    discount = strategy.calculate_discount(product, quantity, unit_price)
                    if discount:
                        discounts.append(discount)
        return discounts
