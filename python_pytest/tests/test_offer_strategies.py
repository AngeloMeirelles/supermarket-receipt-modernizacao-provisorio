import pytest

from model_objects import Product, ProductUnit
from offer_strategies import (
    FiveForAmountStrategy,
    IOfferStrategy,
    PercentDiscountStrategy,
    QuantityOfferStrategy,
    ThreeForTwoStrategy,
    TwoForAmountStrategy,
)

TOOTHBRUSH = Product("toothbrush", ProductUnit.EACH)
APPLES = Product("apples", ProductUnit.KILO)
RICE = Product("rice", ProductUnit.EACH)
TOOTHPASTE = Product("toothpaste", ProductUnit.EACH)
CHERRY_TOMATOES = Product("cherry tomatoes", ProductUnit.EACH)


@pytest.mark.parametrize(
    "strategy",
    [
        ThreeForTwoStrategy(),
        PercentDiscountStrategy(10.0),
        TwoForAmountStrategy(0.99),
        FiveForAmountStrategy(7.49),
    ],
)
def test_all_offers_follow_the_same_interface(strategy):
    assert isinstance(strategy, IOfferStrategy)


def test_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        IOfferStrategy()


def test_three_for_two_below_minimum_gives_no_discount():
    assert ThreeForTwoStrategy().calculate_discount(TOOTHBRUSH, 2, 0.99) is None


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (3, -0.99),
        (7, -1.98),
    ],
)
def test_three_for_two(quantity, expected_discount):
    discount = ThreeForTwoStrategy().calculate_discount(TOOTHBRUSH, quantity, 0.99)

    assert discount.product is TOOTHBRUSH
    assert discount.description == "3 for 2"
    assert discount.discount_amount == pytest.approx(expected_discount)


def test_three_for_two_does_not_charge_weight_fraction_kept_item_d13():
    discount = ThreeForTwoStrategy().calculate_discount(APPLES, 3.5, 1.99)

    assert discount.discount_amount == pytest.approx(-2.985)


def test_percent_discount():
    discount = PercentDiscountStrategy(10.0).calculate_discount(RICE, 2, 2.49)

    assert discount.product is RICE
    assert discount.description == "10.0% off"
    assert discount.discount_amount == pytest.approx(-0.498)


def test_percent_discount_applies_the_registered_percentage_kept_item_d8():
    discount = PercentDiscountStrategy(20.0).calculate_discount(APPLES, 1, 1.99)

    assert discount.description == "20.0% off"
    assert discount.discount_amount == pytest.approx(-0.398)


def test_two_for_amount_with_1_unit_gives_no_discount():
    assert TwoForAmountStrategy(0.99).calculate_discount(CHERRY_TOMATOES, 1, 0.69) is None


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (2, -0.39),
        (4, -0.78),
    ],
)
def test_two_for_amount_with_even_quantity(quantity, expected_discount):
    discount = TwoForAmountStrategy(0.99).calculate_discount(CHERRY_TOMATOES, quantity, 0.69)

    assert discount.product is CHERRY_TOMATOES
    assert discount.description == "2 for 0.99"
    assert discount.discount_amount == pytest.approx(expected_discount)


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (3, 0.105),
        (5, -0.285),
    ],
)
def test_two_for_amount_with_odd_quantity_overcharges_kept_item_d12(quantity, expected_discount):
    discount = TwoForAmountStrategy(0.99).calculate_discount(CHERRY_TOMATOES, quantity, 0.69)

    assert discount.discount_amount == pytest.approx(expected_discount)


def test_five_for_amount_below_minimum_gives_no_discount():
    assert FiveForAmountStrategy(7.49).calculate_discount(TOOTHPASTE, 4, 1.79) is None


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (5, -1.46),
        (6, -1.46),
    ],
)
def test_five_for_amount(quantity, expected_discount):
    discount = FiveForAmountStrategy(7.49).calculate_discount(TOOTHPASTE, quantity, 1.79)

    assert discount.product is TOOTHPASTE
    assert discount.description == "5 for 7.49"
    assert discount.discount_amount == pytest.approx(expected_discount)


@pytest.mark.parametrize(
    "strategy",
    [
        ThreeForTwoStrategy(),
        TwoForAmountStrategy(0.99),
        FiveForAmountStrategy(7.49),
    ],
)
def test_quantity_offers_share_the_same_base_class(strategy):
    assert isinstance(strategy, QuantityOfferStrategy)


def test_base_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        QuantityOfferStrategy()


class FourForSixStrategy(QuantityOfferStrategy):
    def _group_size(self):
        return 4

    def _price_per_group(self, unit_price):
        return 6.0

    def _description(self):
        return "4 for 6.0"


def test_new_quantity_offer_below_minimum_gives_no_discount():
    assert FourForSixStrategy().calculate_discount(TOOTHPASTE, 3, 1.79) is None


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (4, -1.16),
        (5, -1.16),
        (8, -2.32),
    ],
)
def test_new_quantity_offer_only_implements_the_abstract_methods(quantity, expected_discount):
    discount = FourForSixStrategy().calculate_discount(TOOTHPASTE, quantity, 1.79)

    assert discount.product is TOOTHPASTE
    assert discount.description == "4 for 6.0"
    assert discount.discount_amount == pytest.approx(expected_discount)
