import pytest

from model_objects import Offer, Product, ProductUnit, SpecialOfferType
from offer_strategies import (
    FiveForAmountStrategy,
    PercentDiscountStrategy,
    ThreeForTwoStrategy,
    TwoForAmountStrategy,
)
from offer_strategy_factory import OfferStrategyFactory

TOOTHBRUSH = Product("toothbrush", ProductUnit.EACH)


@pytest.mark.parametrize(
    "offer_type, strategy_class",
    [
        (SpecialOfferType.THREE_FOR_TWO, ThreeForTwoStrategy),
        (SpecialOfferType.TEN_PERCENT_DISCOUNT, PercentDiscountStrategy),
        (SpecialOfferType.TWO_FOR_AMOUNT, TwoForAmountStrategy),
        (SpecialOfferType.FIVE_FOR_AMOUNT, FiveForAmountStrategy),
    ],
)
def test_factory_chooses_the_strategy_by_offer_type(offer_type, strategy_class):
    strategy = OfferStrategyFactory.create(Offer(offer_type, TOOTHBRUSH, 10.0))

    assert isinstance(strategy, strategy_class)


@pytest.mark.parametrize(
    "offer_type, argument, description",
    [
        (SpecialOfferType.TEN_PERCENT_DISCOUNT, 15.0, "15.0% off"),
        (SpecialOfferType.TWO_FOR_AMOUNT, 0.99, "2 for 0.99"),
        (SpecialOfferType.FIVE_FOR_AMOUNT, 7.49, "5 for 7.49"),
    ],
)
def test_factory_passes_the_registered_argument_to_the_strategy(offer_type, argument, description):
    strategy = OfferStrategyFactory.create(Offer(offer_type, TOOTHBRUSH, argument))

    discount = strategy.calculate_discount(TOOTHBRUSH, 5, 1.0)

    assert discount.description == description


def test_factory_returns_none_for_unknown_offer_type():
    assert OfferStrategyFactory.create(Offer("unknown offer type", TOOTHBRUSH, 10.0)) is None
