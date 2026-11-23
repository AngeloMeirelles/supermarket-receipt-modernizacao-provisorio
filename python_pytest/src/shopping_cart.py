import math

from catalog import SupermarketCatalog
from model_objects import Discount, Offer, Product, ProductQuantity, SpecialOfferType
from offer_strategies import PercentDiscountStrategy
from receipt import Receipt


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
        if product in self._product_quantities:
            self._product_quantities[product] = (
                self._product_quantities[product] + quantity
            )
        else:
            self._product_quantities[product] = quantity

    def handle_offers(
        self,
        receipt: Receipt,
        offers: dict[Product, Offer],
        catalog: SupermarketCatalog,
    ) -> None:
        for product, quantity in self._product_quantities.items():
            if product not in offers:
                continue

            offer = offers[product]
            unit_price = catalog.unit_price(product)
            whole_units = int(quantity)
            discount: Discount | None = None
            group_size = 1
            if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
                group_size = 3

            elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
                group_size = 2
                if whole_units >= 2:
                    price_with_offer = (
                        offer.argument * (whole_units / group_size)
                        + whole_units % 2 * unit_price
                    )
                    discount_amount = unit_price * quantity - price_with_offer
                    discount = Discount(
                        product, "2 for " + str(offer.argument), -discount_amount
                    )

            if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
                group_size = 5

            number_of_groups = math.floor(whole_units / group_size)
            if offer.offer_type == SpecialOfferType.THREE_FOR_TWO and whole_units > 2:
                discount_amount = quantity * unit_price - (
                    (number_of_groups * 2 * unit_price) + whole_units % 3 * unit_price
                )
                discount = Discount(product, "3 for 2", -discount_amount)

            if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
                strategy = PercentDiscountStrategy(offer.argument)
                discount = strategy.calculate_discount(product, quantity, unit_price)

            if (
                offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT
                and whole_units >= 5
            ):
                discount_amount = unit_price * quantity - (
                    offer.argument * number_of_groups + whole_units % 5 * unit_price
                )
                discount = Discount(
                    product,
                    str(group_size) + " for " + str(offer.argument),
                    -discount_amount,
                )

            if discount:
                receipt.add_discount(discount)
