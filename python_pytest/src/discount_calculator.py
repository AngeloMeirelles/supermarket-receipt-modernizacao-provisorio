"""Cálculo dos descontos de uma compra."""

from catalog import SupermarketCatalog
from model_objects import Bundle, Discount, Offer, Product
from offer_strategy_factory import OfferStrategyFactory

BUNDLE_DISCOUNT_PERCENT = 10.0
BUNDLE_DESCRIPTION = f"bundle {BUNDLE_DISCOUNT_PERCENT:g}% off"


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

    def bundle_discounts(
        self,
        product_quantities: dict[Product, float],
        bundles: list[Bundle],
        offers: dict[Product, Offer],
    ) -> list[Discount]:
        """Descontos dos combos completos, na ordem em que foram cadastrados.

        Regras de convivência:
        - produto com oferta individual cadastrada não participa de combos;
        - cada unidade entra em no máximo um combo;
        - só unidades inteiras formam combo.
        """
        available_units = {
            product: int(quantity)
            for product, quantity in product_quantities.items()
            if product not in offers
        }
        discounts = []
        for bundle in bundles:
            complete_bundles = min(
                available_units.get(product, 0) for product in bundle.products
            )
            if complete_bundles < 1:
                continue

            for product in bundle.products:
                available_units[product] -= complete_bundles
                discounts.append(self._bundle_discount(product, complete_bundles))
        return discounts

    def _bundle_discount(self, product: Product, units: int) -> Discount:
        full_price = units * self._catalog.unit_price(product)
        discount_amount = full_price * BUNDLE_DISCOUNT_PERCENT / 100.0
        return Discount(product, BUNDLE_DESCRIPTION, -discount_amount)
