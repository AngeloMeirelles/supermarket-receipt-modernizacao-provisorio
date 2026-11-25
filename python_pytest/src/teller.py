from catalog import SupermarketCatalog
from model_objects import Offer, Product, SpecialOfferType
from receipt import Receipt
from shopping_cart import ShoppingCart


class Teller:

    def __init__(self, catalog: SupermarketCatalog) -> None:
        self.catalog = catalog
        self.offers: dict[Product, Offer] = {}

    def add_special_offer(self, offer_type: SpecialOfferType, product: Product, argument: float) -> None:
        self.offers[product] = Offer(offer_type, product, argument)

    def checks_out_articles_from(self, the_cart: ShoppingCart) -> Receipt:
        receipt = Receipt()
        for item in the_cart.items:
            product = item.product
            quantity = item.quantity
            unit_price = self.catalog.unit_price(product)
            total_price = quantity * unit_price
            receipt.add_product(product, quantity, unit_price, total_price)

        the_cart.handle_offers(receipt, self.offers, self.catalog)

        return receipt

    def product_with_name(self, name: str) -> Product | None:
        return self.catalog.products.get(name, None)