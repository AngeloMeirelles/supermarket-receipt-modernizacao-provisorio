from bundle_calculator import BundleCalculator
from catalog import SupermarketCatalog
from model_objects import Bundle, Offer, Product, SpecialOfferType
from receipt import Receipt
from shopping_cart import ShoppingCart


class Teller:

    def __init__(self, catalog: SupermarketCatalog) -> None:
        self.catalog = catalog
        self.offers: dict[Product, Offer] = {}
        self.bundles: list[Bundle] = []

    def add_special_offer(self, offer_type: SpecialOfferType, product: Product, argument: float) -> None:
        self.offers[product] = Offer(offer_type, product, argument)

    def add_bundle_offer(self, products: list[Product]) -> None:
        """Cadastra um combo de dois ou mais produtos diferentes (RF12)."""
        self.bundles.append(Bundle(products))

    def checks_out_articles_from(self, the_cart: ShoppingCart) -> Receipt:
        receipt = Receipt()
        for item in the_cart.items:
            product = item.product
            quantity = item.quantity
            unit_price = self.catalog.unit_price(product)
            total_price = quantity * unit_price
            receipt.add_product(product, quantity, unit_price, total_price)

        the_cart.handle_offers(receipt, self.offers, self.catalog)
        bundle_calculator = BundleCalculator(self.catalog)
        for discount in bundle_calculator.bundle_discounts(the_cart.product_quantities, self.bundles, self.offers):
            receipt.add_discount(discount)

        return receipt

    def product_with_name(self, name: str) -> Product | None:
        return self.catalog.products.get(name, None)