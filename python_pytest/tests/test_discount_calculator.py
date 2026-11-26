import pytest

from discount_calculator import DiscountCalculator
from model_objects import Offer, Product, ProductUnit, SpecialOfferType
from tests.fake_catalog import FakeCatalog

TOOTHBRUSH = Product("toothbrush", ProductUnit.EACH)
RICE = Product("rice", ProductUnit.EACH)
APPLES = Product("apples", ProductUnit.KILO)


@pytest.fixture
def calculator():
    catalog = FakeCatalog()
    catalog.add_product(TOOTHBRUSH, 0.99)
    catalog.add_product(RICE, 2.49)
    catalog.add_product(APPLES, 1.99)
    return DiscountCalculator(catalog)


def test_no_offers_gives_no_discounts(calculator):
    assert calculator.offer_discounts({TOOTHBRUSH: 3}, {}) == []


def test_discounts_follow_the_product_order(calculator):
    offers = {
        TOOTHBRUSH: Offer(SpecialOfferType.THREE_FOR_TWO, TOOTHBRUSH, 0.0),
        RICE: Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, RICE, 10.0),
    }

    discounts = calculator.offer_discounts({RICE: 1, TOOTHBRUSH: 3}, offers)

    assert [discount.product for discount in discounts] == [RICE, TOOTHBRUSH]
    assert [discount.discount_amount for discount in discounts] == pytest.approx([-0.249, -0.99])


def test_offer_below_minimum_is_left_out_of_the_list(calculator):
    offers = {TOOTHBRUSH: Offer(SpecialOfferType.THREE_FOR_TWO, TOOTHBRUSH, 0.0)}

    assert calculator.offer_discounts({TOOTHBRUSH: 2}, offers) == []


def test_offer_for_product_not_in_purchase_gives_no_discount(calculator):
    offers = {TOOTHBRUSH: Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, TOOTHBRUSH, 10.0)}

    assert calculator.offer_discounts({APPLES: 2.5}, offers) == []


def test_offer_of_unknown_type_gives_no_discount(calculator):
    offers = {TOOTHBRUSH: Offer("unknown offer type", TOOTHBRUSH, 10.0)}

    assert calculator.offer_discounts({TOOTHBRUSH: 3}, offers) == []


def test_uses_the_catalog_price(calculator):
    offers = {APPLES: Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, APPLES, 10.0)}

    [discount] = calculator.offer_discounts({APPLES: 2.5}, offers)

    assert discount.discount_amount == pytest.approx(-0.4975)
