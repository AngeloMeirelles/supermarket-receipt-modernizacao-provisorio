"""Testes unitários das estratégias de oferta, da fábrica e da calculadora."""

import pytest

from discount_calculator import DiscountCalculator
from model_objects import Discount, Offer, SpecialOfferType
from offer_strategies import (
    IOfferStrategy,
    NoOfferStrategy,
    PercentDiscountStrategy,
    QuantityForAmountStrategy,
    ThreeForTwoStrategy,
)
from offer_strategy_factory import OfferStrategyFactory

# ---------------------------------------------------------------------------
# Estratégias (Strategy e Template Method)
# ---------------------------------------------------------------------------


def test_percent_discount_strategy(rice):
    discount = PercentDiscountStrategy(10.0).calculate_discount(rice, 2, 2.49)

    assert discount.product == rice
    assert discount.description == "10.0% off"
    assert discount.discount_amount == pytest.approx(-0.498)


def test_three_for_two_strategy_charges_two_of_every_three_units(toothbrush):
    discount = ThreeForTwoStrategy().calculate_discount(toothbrush, 6, 0.99)

    assert discount.description == "3 for 2"
    assert discount.discount_amount == pytest.approx(-1.98)


def test_three_for_two_strategy_does_not_apply_below_three_units(toothbrush):
    assert ThreeForTwoStrategy().calculate_discount(toothbrush, 2, 0.99) is None


def test_quantity_for_amount_strategy_accepts_any_group_size(rice):
    """Um novo tamanho de grupo não exige classe nova nem mudança no cálculo.

    9 unidades em "4 por 8,00": 2 grupos (16,00) + 1 avulsa (2,49) = 18,49.
    Sem a oferta seriam 22,41, então o desconto é de 3,92.
    """
    discount = QuantityForAmountStrategy(4, 8.0).calculate_discount(rice, 9, 2.49)

    assert discount.description == "4 for 8.0"
    assert discount.discount_amount == pytest.approx(-3.92)


def test_no_offer_strategy_never_gives_discount(rice):
    assert NoOfferStrategy().calculate_discount(rice, 10, 2.49) is None


@pytest.mark.parametrize(
    "strategy",
    [
        ThreeForTwoStrategy(),
        PercentDiscountStrategy(10.0),
        QuantityForAmountStrategy(5, 7.49),
        NoOfferStrategy(),
    ],
)
@pytest.mark.parametrize("quantity", [1, 5])
def test_every_strategy_respects_the_interface_contract(rice, strategy, quantity):
    """Qualquer estratégia pode ser usada no lugar da interface (LSP)."""
    discount = strategy.calculate_discount(rice, quantity, 2.49)

    assert isinstance(strategy, IOfferStrategy)
    assert discount is None or isinstance(discount, Discount)


# ---------------------------------------------------------------------------
# Fábrica
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "offer_type, expected_strategy",
    [
        (SpecialOfferType.THREE_FOR_TWO, ThreeForTwoStrategy),
        (SpecialOfferType.TEN_PERCENT_DISCOUNT, PercentDiscountStrategy),
        (SpecialOfferType.TWO_FOR_AMOUNT, QuantityForAmountStrategy),
        (SpecialOfferType.FIVE_FOR_AMOUNT, QuantityForAmountStrategy),
        ("UNKNOWN", NoOfferStrategy),
    ],
)
def test_factory_creates_the_strategy_of_each_offer_type(
    rice, offer_type, expected_strategy
):
    strategy = OfferStrategyFactory.create(Offer(offer_type, rice, 1.0))

    assert type(strategy) is expected_strategy


def test_factory_passes_the_offer_argument_to_the_strategy(toothpaste):
    offer = Offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)

    strategy = OfferStrategyFactory.create(offer)
    discount = strategy.calculate_discount(toothpaste, 5, 1.79)

    assert discount.description == "5 for 7.49"
    assert discount.discount_amount == pytest.approx(-1.46)


# ---------------------------------------------------------------------------
# Calculadora de descontos
# ---------------------------------------------------------------------------


def test_calculator_only_discounts_products_that_have_an_offer(
    catalog, rice, toothbrush
):
    offers = {toothbrush: Offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)}
    product_quantities = {rice: 3, toothbrush: 3}

    discounts = DiscountCalculator(catalog).product_discounts(
        product_quantities, offers
    )

    assert [discount.product for discount in discounts] == [toothbrush]


def test_calculator_leaves_out_offers_that_do_not_apply(catalog, toothbrush):
    offers = {toothbrush: Offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)}

    discounts = DiscountCalculator(catalog).product_discounts({toothbrush: 2}, offers)

    assert discounts == []
