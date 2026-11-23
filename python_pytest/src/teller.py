from catalog import SupermarketCatalog
from discount_calculator import DiscountCalculator
from model_objects import Bundle, Offer, Product, SpecialOfferType
from receipt import Receipt
from shopping_cart import ShoppingCart


class Teller:
    def __init__(self, catalog: SupermarketCatalog) -> None:
        self.catalog = catalog
        self.offers: dict[Product, Offer] = {}
        self.bundles: list[Bundle] = []

    def add_special_offer(
        self, offer_type: SpecialOfferType, product: Product, argument: float
    ) -> None:
        self.offers[product] = Offer(offer_type, product, argument)

    def add_bundle_offer(self, products: list[Product]) -> None:
        """Cadastra um combo: quem leva todos os produtos ganha 10% neles."""
        self.bundles.append(Bundle(products))

    def checks_out_articles_from(self, the_cart: ShoppingCart) -> Receipt:
        receipt = Receipt()
        for item in the_cart.items:
            unit_price = self.catalog.unit_price(item.product)
            total_price = item.quantity * unit_price
            receipt.add_product(item.product, item.quantity, unit_price, total_price)

        the_cart.handle_offers(receipt, self.offers, self.catalog)
        self._apply_bundles(the_cart, receipt)

        return receipt

    def _apply_bundles(self, the_cart: ShoppingCart, receipt: Receipt) -> None:
        calculator = DiscountCalculator(self.catalog)
        bundle_discounts = calculator.bundle_discounts(
            the_cart.product_quantities, self.bundles, self.offers
        )
        for discount in bundle_discounts:
            receipt.add_discount(discount)

    def product_with_name(self, name: str) -> Product | None:
        return self.catalog.products.get(name, None)
