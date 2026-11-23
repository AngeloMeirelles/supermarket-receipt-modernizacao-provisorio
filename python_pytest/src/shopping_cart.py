from catalog import SupermarketCatalog
from model_objects import Offer, Product, ProductQuantity
from offer_strategy_factory import OfferStrategyFactory
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

            strategy = OfferStrategyFactory.create(offers[product])
            discount = strategy.calculate_discount(
                product, quantity, catalog.unit_price(product)
            )
            if discount is not None:
                receipt.add_discount(discount)
