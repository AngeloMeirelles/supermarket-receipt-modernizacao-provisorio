import pytest

from bundle_calculator import BundleCalculator
from model_objects import Bundle, Product, ProductUnit, SpecialOfferType
from receipt_printer import ReceiptPrinter
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog

TOOTHBRUSH = Product("toothbrush", ProductUnit.EACH)
TOOTHPASTE = Product("toothpaste", ProductUnit.EACH)
DENTAL_FLOSS = Product("dental floss", ProductUnit.EACH)
APPLES = Product("apples", ProductUnit.KILO)

BUNDLE_DESCRIPTION = "bundle 10% off"


@pytest.fixture
def catalog():
    catalog = FakeCatalog()
    catalog.add_product(TOOTHBRUSH, 10.00)
    catalog.add_product(TOOTHPASTE, 15.00)
    catalog.add_product(DENTAL_FLOSS, 5.00)
    catalog.add_product(APPLES, 2.00)
    return catalog


@pytest.fixture
def teller_with_bundle(catalog):
    teller = Teller(catalog)
    teller.add_bundle_offer([TOOTHBRUSH, TOOTHPASTE])
    return teller


def check_out(teller, *items):
    cart = ShoppingCart()
    for product, quantity in items:
        cart.add_item_quantity(product, quantity)
    return teller.checks_out_articles_from(cart)


def discount_lines(receipt):
    return [(discount.product, discount.description, discount.discount_amount) for discount in receipt.discounts]


def test_complete_bundle(teller_with_bundle):
    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 1), (TOOTHPASTE, 1))

    assert discount_lines(receipt) == [
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-1.00)),
        (TOOTHPASTE, BUNDLE_DESCRIPTION, pytest.approx(-1.50)),
    ]
    assert receipt.total_price() == pytest.approx(22.50)


def test_incomplete_bundle_gives_no_discount(teller_with_bundle):
    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 1))

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(10.00)


def test_repeated_bundle(teller_with_bundle):
    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 2), (TOOTHPASTE, 2))

    assert discount_lines(receipt) == [
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-2.00)),
        (TOOTHPASTE, BUNDLE_DESCRIPTION, pytest.approx(-3.00)),
    ]
    assert receipt.total_price() == pytest.approx(45.00)


def test_surplus_product_pays_regular_price(teller_with_bundle):
    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 2), (TOOTHPASTE, 1))

    assert discount_lines(receipt) == [
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-1.00)),
        (TOOTHPASTE, BUNDLE_DESCRIPTION, pytest.approx(-1.50)),
    ]
    assert receipt.total_price() == pytest.approx(32.50)


def test_bundle_registration_with_different_products(catalog):
    teller = Teller(catalog)

    teller.add_bundle_offer([TOOTHBRUSH, TOOTHPASTE])

    [bundle] = teller.bundles
    assert bundle.products == (TOOTHBRUSH, TOOTHPASTE)


@pytest.mark.parametrize(
    "products",
    [[], [TOOTHBRUSH], [TOOTHBRUSH, TOOTHBRUSH]],
    ids=["no_products", "single_product", "repeated_product"],
)
def test_bundle_registration_rejects_fewer_than_two_different_products(catalog, products):
    teller = Teller(catalog)

    with pytest.raises(ValueError):
        teller.add_bundle_offer(products)

    assert teller.bundles == []


def test_weighed_product_enters_bundle_only_with_whole_kilos(catalog):
    teller = Teller(catalog)
    teller.add_bundle_offer([APPLES, TOOTHBRUSH])

    receipt = check_out(teller, (APPLES, 1.5), (TOOTHBRUSH, 1))

    assert discount_lines(receipt) == [
        (APPLES, BUNDLE_DESCRIPTION, pytest.approx(-0.20)),
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-1.00)),
    ]
    assert receipt.total_price() == pytest.approx(11.80)


def test_weighed_product_without_a_whole_kilo_forms_no_bundle(catalog):
    teller = Teller(catalog)
    teller.add_bundle_offer([APPLES, TOOTHBRUSH])

    receipt = check_out(teller, (APPLES, 0.5), (TOOTHBRUSH, 1))

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(11.00)


def test_product_with_its_own_offer_stays_out_of_the_bundle(teller_with_bundle):
    teller_with_bundle.add_special_offer(SpecialOfferType.THREE_FOR_TWO, TOOTHBRUSH, 0.0)

    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 3), (TOOTHPASTE, 1))

    assert discount_lines(receipt) == [(TOOTHBRUSH, "3 for 2", pytest.approx(-10.00))]
    assert receipt.total_price() == pytest.approx(35.00)


def test_product_with_its_own_offer_stays_out_even_without_offer_discount(teller_with_bundle):
    teller_with_bundle.add_special_offer(SpecialOfferType.THREE_FOR_TWO, TOOTHBRUSH, 0.0)

    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 1), (TOOTHPASTE, 1))

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(25.00)


@pytest.fixture
def teller_with_two_bundles(catalog):
    teller = Teller(catalog)
    teller.add_bundle_offer([TOOTHBRUSH, TOOTHPASTE])
    teller.add_bundle_offer([TOOTHBRUSH, DENTAL_FLOSS])
    return teller


def test_bundle_registered_first_takes_the_shared_unit(teller_with_two_bundles):
    receipt = check_out(teller_with_two_bundles, (TOOTHBRUSH, 1), (TOOTHPASTE, 1), (DENTAL_FLOSS, 1))

    assert discount_lines(receipt) == [
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-1.00)),
        (TOOTHPASTE, BUNDLE_DESCRIPTION, pytest.approx(-1.50)),
    ]
    assert receipt.total_price() == pytest.approx(27.50)


def test_multiple_bundles_with_a_shared_product(teller_with_two_bundles):
    receipt = check_out(teller_with_two_bundles, (TOOTHBRUSH, 2), (TOOTHPASTE, 1), (DENTAL_FLOSS, 1))

    assert discount_lines(receipt) == [
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-1.00)),
        (TOOTHPASTE, BUNDLE_DESCRIPTION, pytest.approx(-1.50)),
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-1.00)),
        (DENTAL_FLOSS, BUNDLE_DESCRIPTION, pytest.approx(-0.50)),
    ]
    assert receipt.total_price() == pytest.approx(36.00)


def test_bundle_discounts_come_after_offer_discounts(teller_with_bundle):
    teller_with_bundle.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, DENTAL_FLOSS, 10.0)

    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 1), (TOOTHPASTE, 1), (DENTAL_FLOSS, 1))

    assert discount_lines(receipt) == [
        (DENTAL_FLOSS, "10.0% off", pytest.approx(-0.50)),
        (TOOTHBRUSH, BUNDLE_DESCRIPTION, pytest.approx(-1.00)),
        (TOOTHPASTE, BUNDLE_DESCRIPTION, pytest.approx(-1.50)),
    ]
    assert receipt.total_price() == pytest.approx(27.00)


def test_receipt_without_registered_bundle_has_no_bundle_discount(catalog):
    receipt = check_out(Teller(catalog), (TOOTHBRUSH, 1), (TOOTHPASTE, 1))

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(25.00)


def test_printed_receipt_with_bundle(teller_with_bundle):
    receipt = check_out(teller_with_bundle, (TOOTHBRUSH, 1), (TOOTHPASTE, 1))

    printed = ReceiptPrinter().print_receipt(receipt)

    assert printed == (
        "toothbrush                         10.00\n"
        "toothpaste                         15.00\n"
        "bundle 10% off (toothbrush)        -1.00\n"
        "bundle 10% off (toothpaste)        -1.50\n"
        "\n"
        "Total:                             22.50\n"
    )


def test_bundle_calculator_in_isolation(catalog):
    calculator = BundleCalculator(catalog)

    discounts = calculator.bundle_discounts(
        {TOOTHBRUSH: 2, TOOTHPASTE: 1}, [Bundle([TOOTHBRUSH, TOOTHPASTE])], {}
    )

    assert [(discount.product, discount.discount_amount) for discount in discounts] == [
        (TOOTHBRUSH, pytest.approx(-1.00)),
        (TOOTHPASTE, pytest.approx(-1.50)),
    ]
