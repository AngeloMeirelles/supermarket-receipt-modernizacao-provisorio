import math

from model_objects import ProductQuantity, SpecialOfferType, Discount


class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        return self._items

    def add_item(self, product):
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        return self._product_quantities

    def add_item_quantity(self, product, quantity):
        self._items.append(ProductQuantity(product, quantity))
        if product in self._product_quantities.keys():
            self._product_quantities[product] = self._product_quantities[product] + quantity
        else:
            self._product_quantities[product] = quantity

    def handle_offers(self, receipt, offers, catalog):
        for product in self._product_quantities.keys():
            quantity = self._product_quantities[product]
            if product in offers.keys():
                offer = offers[product]
                unit_price = catalog.unit_price(product)
                quantity_as_int = int(quantity)
                discount = None
                group_size = 1
                if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
                    group_size = 3

                elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
                    group_size = 2
                    if quantity_as_int >= 2:
                        total_with_offer = offer.argument * (quantity_as_int / group_size) + quantity_as_int % 2 * unit_price
                        discount_amount = unit_price * quantity - total_with_offer
                        discount = Discount(product, "2 for " + str(offer.argument), -discount_amount)

                if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
                    group_size = 5

                number_of_groups = math.floor(quantity_as_int / group_size)
                if offer.offer_type == SpecialOfferType.THREE_FOR_TWO and quantity_as_int > 2:
                    discount_amount = quantity * unit_price - (
                                (number_of_groups * 2 * unit_price) + quantity_as_int % 3 * unit_price)
                    discount = Discount(product, "3 for 2", -discount_amount)

                if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
                    discount = Discount(product, str(offer.argument) + "% off",
                                        -quantity * unit_price * offer.argument / 100.0)

                if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT and quantity_as_int >= 5:
                    discount_amount = unit_price * quantity - (
                                offer.argument * number_of_groups + quantity_as_int % 5 * unit_price)
                    discount = Discount(product, str(group_size) + " for " + str(offer.argument), -discount_amount)

                if discount:
                    receipt.add_discount(discount)
