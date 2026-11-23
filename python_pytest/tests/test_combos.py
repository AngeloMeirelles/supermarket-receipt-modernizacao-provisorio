"""Testes da promoção de combos: 10% de desconto nos itens dos combos completos.

Regras adotadas (registradas em docs/decisoes_tecnicas.md):
- o desconto vale apenas para as unidades que formam combos completos;
- o desconto aparece no recibo em uma linha por produto do combo;
- produto com oferta individual cadastrada não participa de combos;
- cada unidade entra em no máximo um combo, na ordem de cadastro dos combos;
- só unidades inteiras formam combo.

Preços usados: escova 0,99; creme dental 1,79; arroz 2,49; tomate-cereja 0,69;
maçã 1,99 o quilo.
"""

import pytest

from model_objects import Bundle, Product, ProductUnit, SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog
from tests.receipt_printer import ReceiptPrinter

BUNDLE_DESCRIPTION = "bundle 10% off"


def discount_lines(receipt):
    """Resume os descontos do recibo em pares (descrição, nome do produto)."""
    return [
        (discount.description, discount.product.name) for discount in receipt.discounts
    ]


# ---------------------------------------------------------------------------
# Tabela do enunciado
# ---------------------------------------------------------------------------


def test_complete_bundle_gets_ten_percent_off_its_products(
    teller, cart, toothbrush, toothpaste
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert discount_lines(receipt) == [
        (BUNDLE_DESCRIPTION, "toothbrush"),
        (BUNDLE_DESCRIPTION, "toothpaste"),
    ]
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.099)
    assert receipt.discounts[1].discount_amount == pytest.approx(-0.179)
    assert receipt.total_price() == pytest.approx(2.502)


def test_bundle_example_from_the_assignment():
    """Escova 10,00 + creme dental 15,00 = 25,00; desconto 2,50; total 22,50."""
    toothbrush = Product("toothbrush", ProductUnit.EACH)
    toothpaste = Product("toothpaste", ProductUnit.EACH)
    catalog = FakeCatalog()
    catalog.add_product(toothbrush, 10.00)
    catalog.add_product(toothpaste, 15.00)
    teller = Teller(catalog)
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart = ShoppingCart()
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    total_discount = sum(discount.discount_amount for discount in receipt.discounts)
    assert total_discount == pytest.approx(-2.50)
    assert receipt.total_price() == pytest.approx(22.50)


def test_extra_unit_outside_the_bundle_pays_full_price(
    teller, cart, toothbrush, toothpaste
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts[0].discount_amount == pytest.approx(-0.099)
    assert receipt.discounts[1].discount_amount == pytest.approx(-0.179)
    assert receipt.total_price() == pytest.approx(2 * 0.99 + 1.79 - 0.278)


def test_two_complete_bundles_are_both_discounted(teller, cart, toothbrush, toothpaste):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item_quantity(toothpaste, 2)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.discounts) == 2
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.198)
    assert receipt.discounts[1].discount_amount == pytest.approx(-0.358)
    assert receipt.total_price() == pytest.approx(5.004)


@pytest.mark.parametrize("quantity", [1, 3])
def test_incomplete_bundle_gives_no_discount(
    teller, cart, toothbrush, toothpaste, quantity
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item_quantity(toothbrush, quantity)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(quantity * 0.99)


# ---------------------------------------------------------------------------
# Quantidades, excedentes e composição do combo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "toothbrushes, toothpastes, complete_bundles",
    [
        (1, 1, 1),
        (1, 4, 1),
        (3, 2, 2),
        (5, 5, 5),
    ],
)
def test_number_of_bundles_is_limited_by_the_scarcest_product(
    teller, cart, toothbrush, toothpaste, toothbrushes, toothpastes, complete_bundles
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item_quantity(toothbrush, toothbrushes)
    cart.add_item_quantity(toothpaste, toothpastes)

    receipt = teller.checks_out_articles_from(cart)

    full_price = toothbrushes * 0.99 + toothpastes * 1.79
    bundle_discount = complete_bundles * (0.99 + 1.79) * 0.10
    assert receipt.total_price() == pytest.approx(full_price - bundle_discount)


def test_products_outside_the_bundle_pay_full_price(
    teller, cart, toothbrush, toothpaste, rice
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    assert "rice" not in [discount.product.name for discount in receipt.discounts]
    assert receipt.total_price() == pytest.approx(2.502 + 2.49)


def test_bundle_of_three_products_needs_all_of_them(
    teller, cart, toothbrush, toothpaste, rice
):
    teller.add_bundle_offer([toothbrush, toothpaste, rice])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    incomplete_receipt = teller.checks_out_articles_from(cart)
    cart.add_item(rice)
    complete_receipt = teller.checks_out_articles_from(cart)

    assert incomplete_receipt.discounts == []
    assert len(complete_receipt.discounts) == 3
    assert complete_receipt.total_price() == pytest.approx(5.27 * 0.90)


def test_same_product_added_twice_counts_as_one_quantity(
    teller, cart, toothbrush, toothpaste
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothbrush)
    cart.add_item_quantity(toothpaste, 2)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(5.004)


def test_weighed_product_only_forms_bundles_with_whole_kilos(
    teller, cart, apples, rice
):
    """2,5 kg de maçã formam 2 combos: o desconto vale para 2 kg, não para 2,5 kg."""
    teller.add_bundle_offer([apples, rice])
    cart.add_item_quantity(apples, 2.5)
    cart.add_item_quantity(rice, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts[0].discount_amount == pytest.approx(-0.398)
    assert receipt.discounts[1].discount_amount == pytest.approx(-0.498)
    assert receipt.total_price() == pytest.approx(2.5 * 1.99 + 3 * 2.49 - 0.896)


def test_less_than_one_kilo_does_not_form_a_bundle(teller, cart, apples, rice):
    teller.add_bundle_offer([apples, rice])
    cart.add_item_quantity(apples, 0.5)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts == []


# ---------------------------------------------------------------------------
# Múltiplos combos
# ---------------------------------------------------------------------------


def test_different_bundles_are_discounted_independently(
    teller, cart, toothbrush, toothpaste, rice, cherry_tomatoes
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    teller.add_bundle_offer([rice, cherry_tomatoes])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)
    cart.add_item(rice)
    cart.add_item(cherry_tomatoes)

    receipt = teller.checks_out_articles_from(cart)

    assert [discount.product.name for discount in receipt.discounts] == [
        "toothbrush",
        "toothpaste",
        "rice",
        "cherry tomatoes",
    ]
    assert receipt.total_price() == pytest.approx(5.96 * 0.90)


def test_unit_shared_by_two_bundles_is_discounted_only_once(
    teller, cart, toothbrush, toothpaste, rice
):
    """A única escova entra no primeiro combo cadastrado; o segundo fica incompleto."""
    teller.add_bundle_offer([toothbrush, toothpaste])
    teller.add_bundle_offer([toothbrush, rice])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    assert discount_lines(receipt) == [
        (BUNDLE_DESCRIPTION, "toothbrush"),
        (BUNDLE_DESCRIPTION, "toothpaste"),
    ]
    assert receipt.total_price() == pytest.approx(2.502 + 2.49)


def test_two_bundles_sharing_a_product_apply_when_there_are_enough_units(
    teller, cart, toothbrush, toothpaste, rice
):
    teller.add_bundle_offer([toothbrush, toothpaste])
    teller.add_bundle_offer([toothbrush, rice])
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item(toothpaste)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    assert discount_lines(receipt) == [
        (BUNDLE_DESCRIPTION, "toothbrush"),
        (BUNDLE_DESCRIPTION, "toothpaste"),
        (BUNDLE_DESCRIPTION, "toothbrush"),
        (BUNDLE_DESCRIPTION, "rice"),
    ]
    assert receipt.total_price() == pytest.approx(6.26 * 0.90)


# ---------------------------------------------------------------------------
# Convivência com as ofertas que já existiam
# ---------------------------------------------------------------------------


def test_product_with_its_own_offer_does_not_join_a_bundle(
    teller, cart, toothbrush, toothpaste
):
    """Evita desconto duplicado: a oferta individual do produto tem prioridade."""
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert discount_lines(receipt) == [("10.0% off", "toothbrush")]
    assert receipt.total_price() == pytest.approx(0.99 - 0.099 + 1.79)


def test_product_with_offer_stays_out_of_bundles_even_when_offer_does_not_apply(
    teller, cart, toothbrush, toothpaste
):
    """A regra depende do cadastro da oferta, não da quantidade comprada."""
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item(toothbrush)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(2.78)


def test_existing_offers_keep_their_values_when_a_bundle_is_registered(
    teller, cart, toothbrush, toothpaste, rice, cherry_tomatoes
):
    """Regressão: os descontos antigos não mudam e os de combo vêm depois deles."""
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)
    teller.add_bundle_offer([rice, cherry_tomatoes])
    cart.add_item(rice)
    cart.add_item_quantity(toothbrush, 3)
    cart.add_item(cherry_tomatoes)
    cart.add_item_quantity(toothpaste, 5)

    receipt = teller.checks_out_articles_from(cart)

    assert discount_lines(receipt) == [
        ("3 for 2", "toothbrush"),
        ("5 for 7.49", "toothpaste"),
        (BUNDLE_DESCRIPTION, "rice"),
        (BUNDLE_DESCRIPTION, "cherry tomatoes"),
    ]
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.99)
    assert receipt.discounts[1].discount_amount == pytest.approx(-1.46)
    assert receipt.discounts[2].discount_amount == pytest.approx(-0.249)
    assert receipt.discounts[3].discount_amount == pytest.approx(-0.069)


def test_registered_bundle_does_not_change_carts_without_its_products(
    teller, cart, toothbrush, toothpaste, rice
):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item_quantity(rice, 2)

    receipt = teller.checks_out_articles_from(cart)

    assert discount_lines(receipt) == [("10.0% off", "rice")]
    assert receipt.total_price() == pytest.approx(4.98 - 0.498)


# ---------------------------------------------------------------------------
# Recibo impresso e cadastro do combo
# ---------------------------------------------------------------------------


def test_printed_receipt_with_bundle(teller, cart, toothbrush, toothpaste):
    teller.add_bundle_offer([toothbrush, toothpaste])
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item(toothpaste)

    receipt = teller.checks_out_articles_from(cart)

    assert ReceiptPrinter().print_receipt(receipt) == (
        "toothbrush                          1.98\n"
        "  0.99 * 2\n"
        "toothpaste                          1.79\n"
        "bundle 10% off (toothbrush)        -0.10\n"
        "bundle 10% off (toothpaste)        -0.18\n"
        "\n"
        "Total:                              3.49\n"
    )


def test_bundle_keeps_its_products(toothbrush, toothpaste):
    bundle = Bundle([toothbrush, toothpaste])

    assert bundle.products == [toothbrush, toothpaste]


def test_bundle_needs_at_least_two_products(toothbrush):
    with pytest.raises(ValueError, match="at least two different products"):
        Bundle([toothbrush])


def test_bundle_cannot_repeat_a_product(teller, toothbrush):
    with pytest.raises(ValueError, match="at least two different products"):
        teller.add_bundle_offer([toothbrush, toothbrush])
