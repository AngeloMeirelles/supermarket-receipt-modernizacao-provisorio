import math

from catalog import SupermarketCatalog
from model_objects import ProductQuantity, SpecialOfferType, Discount, Offer, Product
from receipt import Receipt

THREE_FOR_TWO_GROUP_SIZE = 3
THREE_FOR_TWO_PAID_UNITS = 2
TWO_FOR_AMOUNT_GROUP_SIZE = 2
FIVE_FOR_AMOUNT_GROUP_SIZE = 5
PERCENT_BASE = 100.0


class ShoppingCart:

    def __init__(self) -> None:
        self._items: list[ProductQuantity] = []
        self._product_quantities: dict[Product, float] = {}

    @property
    def items(self) -> list[ProductQuantity]:
        return self._items

    def add_item(self, product: Product) -> None:
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self) -> dict[Product, float]:
        return self._product_quantities

    def add_item_quantity(self, product: Product, quantity: float) -> None:
        self._items.append(ProductQuantity(product, quantity))
        if product in self._product_quantities.keys():
            self._product_quantities[product] = self._product_quantities[product] + quantity
        else:
            self._product_quantities[product] = quantity

    def handle_offers(self, receipt: Receipt, offers: dict[Product, Offer], catalog: SupermarketCatalog) -> None:
        for product in self._product_quantities.keys():
            quantity = self._product_quantities[product]
            if product in offers.keys():
                offer = offers[product]
                unit_price = catalog.unit_price(product)
                quantity_as_int = int(quantity)
                discount: Discount | None = None
                group_size = 1
                if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
                    group_size = THREE_FOR_TWO_GROUP_SIZE

                elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
                    group_size = TWO_FOR_AMOUNT_GROUP_SIZE
                    if quantity_as_int >= TWO_FOR_AMOUNT_GROUP_SIZE:
                        total_with_offer = offer.argument * (quantity_as_int / group_size) + quantity_as_int % TWO_FOR_AMOUNT_GROUP_SIZE * unit_price
                        discount_amount = unit_price * quantity - total_with_offer
                        discount = Discount(product, "2 for " + str(offer.argument), -discount_amount)

                if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
                    group_size = FIVE_FOR_AMOUNT_GROUP_SIZE

                number_of_groups = math.floor(quantity_as_int / group_size)
                if offer.offer_type == SpecialOfferType.THREE_FOR_TWO and quantity_as_int >= THREE_FOR_TWO_GROUP_SIZE:
                    discount_amount = quantity * unit_price - (
                                (number_of_groups * THREE_FOR_TWO_PAID_UNITS * unit_price) + quantity_as_int % THREE_FOR_TWO_GROUP_SIZE * unit_price)
                    discount = Discount(product, "3 for 2", -discount_amount)

                if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
                    discount = Discount(product, str(offer.argument) + "% off",
                                        -quantity * unit_price * offer.argument / PERCENT_BASE)

                if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT and quantity_as_int >= FIVE_FOR_AMOUNT_GROUP_SIZE:
                    discount_amount = unit_price * quantity - (
                                offer.argument * number_of_groups + quantity_as_int % FIVE_FOR_AMOUNT_GROUP_SIZE * unit_price)
                    discount = Discount(product, str(group_size) + " for " + str(offer.argument), -discount_amount)

                if discount:
                    receipt.add_discount(discount)
