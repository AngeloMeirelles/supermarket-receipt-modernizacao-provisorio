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


class PercentDiscountStrategy(IOfferStrategy):
    """Desconto percentual (RF07). Aplica o percentual cadastrado, qualquer que seja (D8)."""

    def __init__(self, percent: float) -> None:
        self._percent = percent

    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        return Discount(product, str(self._percent) + "% off",
                        -quantity * unit_price * self._percent / PERCENT_BASE)


class QuantityOfferStrategy(IOfferStrategy):
    """Passos comuns das ofertas por quantidade (Template Method).

    Cada oferta informa o tamanho do grupo, o preço do grupo e o texto do desconto. Os grupos
    são contados só com as unidades inteiras, mas o preço sem oferta usa a quantidade completa,
    então a fração de peso não é cobrada. É o defeito D13, mantido como no código original.
    """

    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        whole_units = int(quantity)
        if whole_units < self._group_size():
            return None
        price_with_offer = (self._price_per_group(unit_price) * self._number_of_groups(whole_units)
                            + whole_units % self._group_size() * unit_price)
        discount_amount = quantity * unit_price - price_with_offer
        return Discount(product, self._description(), -discount_amount)

    @abc.abstractmethod
    def _group_size(self) -> int:
        """Quantas unidades formam um grupo da oferta."""

    @abc.abstractmethod
    def _price_per_group(self, unit_price: float) -> float:
        """Quanto o cliente paga por um grupo completo."""

    @abc.abstractmethod
    def _description(self) -> str:
        """Texto do desconto no recibo."""

    def _number_of_groups(self, whole_units: int) -> float:
        """Quantos grupos completos cabem nas unidades inteiras."""
        return math.floor(whole_units / self._group_size())


class ThreeForTwoStrategy(QuantityOfferStrategy):
    """Leve 3, pague 2 (RF06)."""

    def _group_size(self) -> int:
        return THREE_FOR_TWO_GROUP_SIZE

    def _price_per_group(self, unit_price: float) -> float:
        return THREE_FOR_TWO_PAID_UNITS * unit_price

    def _description(self) -> str:
        return "3 for 2"


class TwoForAmountStrategy(QuantityOfferStrategy):
    """2 por um valor (RF08). Mantém o defeito D12."""

    def __init__(self, pair_price: float) -> None:
        self._pair_price = pair_price

    def _group_size(self) -> int:
        return TWO_FOR_AMOUNT_GROUP_SIZE

    def _price_per_group(self, unit_price: float) -> float:
        return self._pair_price

    def _description(self) -> str:
        return "2 for " + str(self._pair_price)

    def _number_of_groups(self, whole_units: int) -> float:
        # D12: a divisão comum conta meio par na quantidade ímpar, e a unidade que sobra ainda
        # paga preço normal. Sem este método, valeria a contagem de grupos inteiros da classe base.
        return whole_units / TWO_FOR_AMOUNT_GROUP_SIZE


class FiveForAmountStrategy(QuantityOfferStrategy):
    """5 por um valor (RF09)."""

    def __init__(self, group_price: float) -> None:
        self._group_price = group_price

    def _group_size(self) -> int:
        return FIVE_FOR_AMOUNT_GROUP_SIZE

    def _price_per_group(self, unit_price: float) -> float:
        return self._group_price

    def _description(self) -> str:
        return str(FIVE_FOR_AMOUNT_GROUP_SIZE) + " for " + str(self._group_price)
