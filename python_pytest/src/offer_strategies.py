"""Regras de cálculo das ofertas especiais (padrão Strategy)."""

import abc

from model_objects import Discount, Product


class IOfferStrategy(abc.ABC):
    """Contrato de uma oferta: calcula o desconto de um produto do carrinho."""

    @abc.abstractmethod
    def calculate_discount(
        self, product: Product, quantity: float, unit_price: float
    ) -> Discount | None:
        """Devolve o desconto do produto, ou None quando a oferta não se aplica."""


class PercentDiscountStrategy(IOfferStrategy):
    """Desconto percentual sobre o valor total do produto."""

    def __init__(self, percent: float) -> None:
        self._percent = percent

    def calculate_discount(
        self, product: Product, quantity: float, unit_price: float
    ) -> Discount | None:
        discount_amount = quantity * unit_price * self._percent / 100.0
        return Discount(product, f"{self._percent}% off", -discount_amount)


class QuantityOfferStrategy(IOfferStrategy):
    """Base das ofertas por quantidade: grupos de unidades com preço especial.

    O método calculate_discount é um Template Method: define os passos comuns
    do cálculo e deixa para as subclasses apenas o que muda entre as ofertas.
    """

    def __init__(self, group_size: int) -> None:
        self._group_size = group_size

    def calculate_discount(
        self, product: Product, quantity: float, unit_price: float
    ) -> Discount | None:
        whole_units = int(quantity)
        if whole_units < self._group_size:
            return None

        leftover_units = whole_units % self._group_size
        price_with_offer = (
            self._number_of_groups(whole_units) * self._group_price(unit_price)
            + leftover_units * unit_price
        )
        discount_amount = quantity * unit_price - price_with_offer
        return Discount(product, self._description(), -discount_amount)

    def _number_of_groups(self, whole_units: int) -> float:
        return whole_units // self._group_size

    @abc.abstractmethod
    def _group_price(self, unit_price: float) -> float:
        """Preço cobrado por um grupo completo de unidades."""

    @abc.abstractmethod
    def _description(self) -> str:
        """Texto da oferta exibido no recibo."""


class ThreeForTwoStrategy(QuantityOfferStrategy):
    """Leve 3, pague 2: a cada três unidades, uma sai de graça."""

    GROUP_SIZE = 3
    PAID_UNITS = 2

    def __init__(self) -> None:
        super().__init__(self.GROUP_SIZE)

    def _group_price(self, unit_price: float) -> float:
        return self.PAID_UNITS * unit_price

    def _description(self) -> str:
        return f"{self.GROUP_SIZE} for {self.PAID_UNITS}"


class QuantityForAmountStrategy(QuantityOfferStrategy):
    """Um grupo de unidades por um valor fechado (ex.: 5 unidades por 7,49)."""

    def __init__(self, group_size: int, amount: float) -> None:
        super().__init__(group_size)
        self._amount = amount

    def _group_price(self, unit_price: float) -> float:
        return self._amount

    def _description(self) -> str:
        return f"{self._group_size} for {self._amount}"


class LegacyTwoForAmountStrategy(QuantityForAmountStrategy):
    """Oferta "2 por um valor" exatamente como o legado calcula.

    Reproduz um defeito conhecido: com quantidade ímpar, o número de pares
    fica fracionado (3 unidades viram 1,5 par) e o cliente paga a mais.
    """

    def __init__(self, amount: float) -> None:
        super().__init__(2, amount)

    def _number_of_groups(self, whole_units: int) -> float:
        return whole_units / self._group_size
