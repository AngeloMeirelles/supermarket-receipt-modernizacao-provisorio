import abc
import math

from model_objects import Discount, Product

THREE_FOR_TWO_GROUP_SIZE = 3
THREE_FOR_TWO_PAID_UNITS = 2
TWO_FOR_AMOUNT_GROUP_SIZE = 2
FIVE_FOR_AMOUNT_GROUP_SIZE = 5
PERCENT_BASE = 100.0


class IOfferStrategy(abc.ABC):
    """Regra de desconto de um tipo de oferta."""

    @abc.abstractmethod
    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        """Devolve o desconto do produto, ou None quando a oferta não dá desconto."""


class ThreeForTwoStrategy(IOfferStrategy):
    """Leve 3, pague 2 (RF06). Mantém o defeito D13: a fração de peso não é cobrada."""

    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        quantity_as_int = int(quantity)
        if quantity_as_int < THREE_FOR_TWO_GROUP_SIZE:
            return None
        number_of_groups = math.floor(quantity_as_int / THREE_FOR_TWO_GROUP_SIZE)
        discount_amount = quantity * unit_price - (
                    (number_of_groups * THREE_FOR_TWO_PAID_UNITS * unit_price) + quantity_as_int % THREE_FOR_TWO_GROUP_SIZE * unit_price)
        return Discount(product, "3 for 2", -discount_amount)


class PercentDiscountStrategy(IOfferStrategy):
    """Desconto percentual (RF07). Aplica o percentual cadastrado, qualquer que seja (D8)."""

    def __init__(self, percent: float) -> None:
        self._percent = percent

    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        return Discount(product, str(self._percent) + "% off",
                        -quantity * unit_price * self._percent / PERCENT_BASE)


class TwoForAmountStrategy(IOfferStrategy):
    """2 por um valor (RF08). Mantém os defeitos D12 e D13."""

    def __init__(self, pair_price: float) -> None:
        self._pair_price = pair_price

    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        quantity_as_int = int(quantity)
        if quantity_as_int < TWO_FOR_AMOUNT_GROUP_SIZE:
            return None
        # D12: a divisão comum conta meio par na quantidade ímpar, e a unidade que sobra ainda paga preço normal.
        total_with_offer = self._pair_price * (quantity_as_int / TWO_FOR_AMOUNT_GROUP_SIZE) + quantity_as_int % TWO_FOR_AMOUNT_GROUP_SIZE * unit_price
        discount_amount = unit_price * quantity - total_with_offer
        return Discount(product, "2 for " + str(self._pair_price), -discount_amount)


class FiveForAmountStrategy(IOfferStrategy):
    """5 por um valor (RF09). Mantém o defeito D13: a fração de peso não é cobrada."""

    def __init__(self, group_price: float) -> None:
        self._group_price = group_price

    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        quantity_as_int = int(quantity)
        if quantity_as_int < FIVE_FOR_AMOUNT_GROUP_SIZE:
            return None
        number_of_groups = math.floor(quantity_as_int / FIVE_FOR_AMOUNT_GROUP_SIZE)
        discount_amount = unit_price * quantity - (
                    self._group_price * number_of_groups + quantity_as_int % FIVE_FOR_AMOUNT_GROUP_SIZE * unit_price)
        return Discount(product, str(FIVE_FOR_AMOUNT_GROUP_SIZE) + " for " + str(self._group_price), -discount_amount)
