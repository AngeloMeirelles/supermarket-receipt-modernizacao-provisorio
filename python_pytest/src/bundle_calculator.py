from catalog import SupermarketCatalog
from model_objects import Bundle, Discount, Offer, Product

BUNDLE_DISCOUNT_PERCENT = 10.0
PERCENT_BASE = 100.0
BUNDLE_DESCRIPTION = "bundle 10% off"


class BundleCalculator:
    """Calcula os descontos dos combos de uma compra (RF13 a RF17)."""

    def __init__(self, catalog: SupermarketCatalog) -> None:
        self._catalog = catalog

    def bundle_discounts(self, product_quantities: dict[Product, float], bundles: list[Bundle],
                         offers: dict[Product, Offer]) -> list[Discount]:
        """Devolve uma linha de desconto por produto de cada combo formado, na ordem de cadastro."""
        # Só unidades inteiras entram em combo (RF15), e produto com oferta própria fica fora (RF16).
        available_units = {
            product: int(quantity)
            for product, quantity in product_quantities.items()
            if product not in offers
        }
        discounts: list[Discount] = []
        for bundle in bundles:
            number_of_bundles = min(available_units.get(product, 0) for product in bundle.products)
            if number_of_bundles == 0:
                continue
            for product in bundle.products:
                # Cada unidade entra num combo só, na ordem de cadastro dos combos (RF17).
                available_units[product] -= number_of_bundles
                bundle_price = self._catalog.unit_price(product) * number_of_bundles
                discounts.append(Discount(product, BUNDLE_DESCRIPTION,
                                          -bundle_price * BUNDLE_DISCOUNT_PERCENT / PERCENT_BASE))
        return discounts
