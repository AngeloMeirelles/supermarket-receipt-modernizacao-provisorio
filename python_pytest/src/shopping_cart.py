from catalog import SupermarketCatalog
from model_objects import Offer, Product, ProductQuantity, SpecialOfferType
from offer_strategies import (
    IOfferStrategy,
    LegacyTwoForAmountStrategy,
    PercentDiscountStrategy,
    QuantityForAmountStrategy,
    ThreeForTwoStrategy,
)
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
            strategy: IOfferStrategy | None = None
            if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
                strategy = ThreeForTwoStrategy()
            elif offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
                strategy = PercentDiscountStrategy(offer.argument)
            elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
                strategy = LegacyTwoForAmountStrategy(offer.argument)
            elif offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
                strategy = QuantityForAmountStrategy(5, offer.argument)

            if strategy is None:
                continue

            discount = strategy.calculate_discount(product, quantity, unit_price)
            if discount:
                receipt.add_discount(discount)
