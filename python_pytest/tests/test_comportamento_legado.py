"""Testes de caracterização do sistema legado.

Registram o comportamento do código original, antes de qualquer refatoração.
Funcionam como rede de segurança: se um destes testes falhar depois de uma
mudança interna, o comportamento visível do sistema foi alterado.

Preços usados: escova 0,99; creme dental 1,79; arroz 2,49; tomate-cereja 0,69;
maçã 1,99 o quilo.
"""

import pytest

from catalog import SupermarketCatalog
from model_objects import Offer, SpecialOfferType
from receipt import Receipt
from tests.receipt_printer import ReceiptPrinter


def checkout_with_offer(teller, cart, product, quantity, offer_type, argument):
    """Cadastra uma oferta, coloca o produto no carrinho e devolve o recibo."""
    teller.add_special_offer(offer_type, product, argument)
    cart.add_item_quantity(product, quantity)
    return teller.checks_out_articles_from(cart)


# ---------------------------------------------------------------------------
# Carrinho sem ofertas
# ---------------------------------------------------------------------------


def test_empty_cart_produces_empty_receipt(teller, cart):
    receipt = teller.checks_out_articles_from(cart)

    assert receipt.items == []
    assert receipt.discounts == []
    assert receipt.total_price() == 0


def test_single_unit_is_charged_the_unit_price(teller, cart, rice):
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    item = receipt.items[0]
    assert item.product == rice
    assert item.quantity == 1.0
    assert item.price == 2.49
    assert item.total_price == pytest.approx(2.49)
    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(2.49)


def test_weighed_product_is_charged_by_kilo(teller, cart, apples):
    cart.add_item_quantity(apples, 2.5)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.items[0].total_price == pytest.approx(4.975)
    assert receipt.total_price() == pytest.approx(4.975)


def test_total_is_the_sum_of_all_items(teller, cart, rice, toothbrush, apples):
    cart.add_item_quantity(rice, 2)
    cart.add_item(toothbrush)
    cart.add_item_quantity(apples, 0.5)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.items) == 3
    assert receipt.total_price() == pytest.approx(6.965)


def test_same_product_added_twice_keeps_two_receipt_lines(teller, cart, rice):
    cart.add_item(rice)
    cart.add_item_quantity(rice, 2)

    receipt = teller.checks_out_articles_from(cart)

    assert [item.quantity for item in receipt.items] == [1.0, 2]
    assert cart.product_quantities == {rice: 3.0}
    assert receipt.total_price() == pytest.approx(7.47)


def test_cart_keeps_items_in_the_order_they_were_added(cart, rice, apples):
    cart.add_item(rice)
    cart.add_item_quantity(apples, 1.5)

    assert [(item.product, item.quantity) for item in cart.items] == [
        (rice, 1.0),
        (apples, 1.5),
    ]


# ---------------------------------------------------------------------------
# Oferta "leve 3, pague 2"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("quantity", [1, 2])
def test_three_for_two_gives_no_discount_below_three_units(
    teller, cart, toothbrush, quantity
):
    receipt = checkout_with_offer(
        teller, cart, toothbrush, quantity, SpecialOfferType.THREE_FOR_TWO, 0
    )

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(quantity * 0.99)


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (3, -0.99),
        (4, -0.99),
        (5, -0.99),
        (6, -1.98),
        (7, -1.98),
    ],
)
def test_three_for_two_gives_one_free_unit_for_every_three(
    teller, cart, toothbrush, quantity, expected_discount
):
    receipt = checkout_with_offer(
        teller, cart, toothbrush, quantity, SpecialOfferType.THREE_FOR_TWO, 0
    )

    assert len(receipt.discounts) == 1
    discount = receipt.discounts[0]
    assert discount.product == toothbrush
    assert discount.description == "3 for 2"
    assert discount.discount_amount == pytest.approx(expected_discount)
    assert receipt.total_price() == pytest.approx(quantity * 0.99 + expected_discount)


# ---------------------------------------------------------------------------
# Oferta de desconto percentual
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "quantity, percent, expected_discount",
    [
        (1, 10.0, -0.249),
        (2, 10.0, -0.498),
        (3, 20.0, -1.494),
    ],
)
def test_percent_discount_applies_to_any_quantity(
    teller, cart, rice, quantity, percent, expected_discount
):
    receipt = checkout_with_offer(
        teller, cart, rice, quantity, SpecialOfferType.TEN_PERCENT_DISCOUNT, percent
    )

    assert len(receipt.discounts) == 1
    discount = receipt.discounts[0]
    assert discount.product == rice
    assert discount.description == f"{percent}% off"
    assert discount.discount_amount == pytest.approx(expected_discount)
    assert receipt.total_price() == pytest.approx(quantity * 2.49 + expected_discount)


def test_percent_discount_applies_to_weighed_product(teller, cart, apples):
    receipt = checkout_with_offer(
        teller, cart, apples, 2.5, SpecialOfferType.TEN_PERCENT_DISCOUNT, 20.0
    )

    assert receipt.discounts[0].description == "20.0% off"
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.995)
    assert receipt.total_price() == pytest.approx(3.98)


# ---------------------------------------------------------------------------
# Oferta "2 unidades por um valor fechado"
# ---------------------------------------------------------------------------


def test_two_for_amount_gives_no_discount_for_single_unit(
    teller, cart, cherry_tomatoes
):
    receipt = checkout_with_offer(
        teller, cart, cherry_tomatoes, 1, SpecialOfferType.TWO_FOR_AMOUNT, 0.99
    )

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(0.69)


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (2, -0.39),
        (4, -0.78),
        (6, -1.17),
    ],
)
def test_two_for_amount_charges_the_offer_price_for_each_pair(
    teller, cart, cherry_tomatoes, quantity, expected_discount
):
    receipt = checkout_with_offer(
        teller, cart, cherry_tomatoes, quantity, SpecialOfferType.TWO_FOR_AMOUNT, 0.99
    )

    assert len(receipt.discounts) == 1
    discount = receipt.discounts[0]
    assert discount.product == cherry_tomatoes
    assert discount.description == "2 for 0.99"
    assert discount.discount_amount == pytest.approx(expected_discount)
    assert receipt.total_price() == pytest.approx(quantity * 0.69 + expected_discount)


@pytest.mark.parametrize(
    "quantity, expected_discount, expected_total",
    [
        (3, -0.39, 1.68),
        (5, -0.78, 2.67),
    ],
)
def test_two_for_amount_with_odd_quantity_charges_leftover_unit_at_unit_price(
    teller, cart, cherry_tomatoes, quantity, expected_discount, expected_total
):
    """DEFEITO DO LEGADO CORRIGIDO (única mudança intencional de comportamento).

    Com quantidade ímpar o legado cobrava "meio par" a mais: 3 unidades saíam
    por 2,175, acima do preço sem oferta (2,07), e 5 unidades por 3,165.
    Agora a unidade que sobra paga o preço normal: 0,99 + 0,69 = 1,68.
    """
    receipt = checkout_with_offer(
        teller, cart, cherry_tomatoes, quantity, SpecialOfferType.TWO_FOR_AMOUNT, 0.99
    )

    assert receipt.discounts[0].discount_amount == pytest.approx(expected_discount)
    assert receipt.total_price() == pytest.approx(expected_total)


# ---------------------------------------------------------------------------
# Oferta "5 unidades por um valor fechado"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("quantity", [1, 4])
def test_five_for_amount_gives_no_discount_below_five_units(
    teller, cart, toothpaste, quantity
):
    receipt = checkout_with_offer(
        teller, cart, toothpaste, quantity, SpecialOfferType.FIVE_FOR_AMOUNT, 7.49
    )

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(quantity * 1.79)


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        (5, -1.46),
        (6, -1.46),
        (9, -1.46),
        (10, -2.92),
    ],
)
def test_five_for_amount_charges_the_offer_price_for_each_group_of_five(
    teller, cart, toothpaste, quantity, expected_discount
):
    receipt = checkout_with_offer(
        teller, cart, toothpaste, quantity, SpecialOfferType.FIVE_FOR_AMOUNT, 7.49
    )

    assert len(receipt.discounts) == 1
    discount = receipt.discounts[0]
    assert discount.product == toothpaste
    assert discount.description == "5 for 7.49"
    assert discount.discount_amount == pytest.approx(expected_discount)
    assert receipt.total_price() == pytest.approx(quantity * 1.79 + expected_discount)


# ---------------------------------------------------------------------------
# Ofertas por quantidade em produto vendido por peso
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "offer_type, argument, quantity, expected_discount, expected_total",
    [
        (SpecialOfferType.THREE_FOR_TWO, 0, 3.5, -2.985, 3.98),
        (SpecialOfferType.TWO_FOR_AMOUNT, 2.99, 2.5, -1.985, 2.99),
        (SpecialOfferType.FIVE_FOR_AMOUNT, 7.99, 5.5, -2.955, 7.99),
    ],
)
def test_quantity_offers_do_not_charge_the_fraction_of_a_weighed_product(
    teller,
    cart,
    apples,
    offer_type,
    argument,
    quantity,
    expected_discount,
    expected_total,
):
    """Comportamento do legado, registrado como está.

    As ofertas por quantidade contam só a parte inteira do peso, e a fração
    que sobra não é cobrada: 3,5 kg no "leve 3, pague 2" custam o mesmo que 2 kg.
    """
    receipt = checkout_with_offer(teller, cart, apples, quantity, offer_type, argument)

    assert receipt.discounts[0].discount_amount == pytest.approx(expected_discount)
    assert receipt.total_price() == pytest.approx(expected_total)


# ---------------------------------------------------------------------------
# Combinações de ofertas e de itens
# ---------------------------------------------------------------------------


def test_offer_considers_the_total_quantity_of_the_product(teller, cart, toothbrush):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item(toothbrush)

    receipt = teller.checks_out_articles_from(cart)

    assert len(receipt.items) == 2
    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == pytest.approx(-0.99)
    assert receipt.total_price() == pytest.approx(1.98)


def test_new_offer_for_the_same_product_replaces_the_previous_one(
    teller, cart, toothbrush
):
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    cart.add_item_quantity(toothbrush, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert [discount.description for discount in receipt.discounts] == ["3 for 2"]


def test_offer_does_not_affect_other_products(teller, cart, toothbrush, rice):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    cart.add_item_quantity(rice, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(7.47)


def test_unrecognized_offer_type_is_ignored(teller, cart, rice):
    receipt = checkout_with_offer(teller, cart, rice, 5, "UNKNOWN", 1.0)

    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(12.45)


def test_discounts_follow_the_order_products_entered_the_cart(
    teller, cart, rice, toothpaste, toothbrush
):
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)
    cart.add_item(rice)
    cart.add_item_quantity(toothpaste, 5)
    cart.add_item_quantity(toothbrush, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert [discount.product for discount in receipt.discounts] == [
        rice,
        toothpaste,
        toothbrush,
    ]
    assert [discount.description for discount in receipt.discounts] == [
        "10.0% off",
        "5 for 7.49",
        "3 for 2",
    ]


# ---------------------------------------------------------------------------
# Recibo impresso
# ---------------------------------------------------------------------------


def test_printed_receipt_of_empty_cart(teller, cart):
    receipt = teller.checks_out_articles_from(cart)

    assert ReceiptPrinter().print_receipt(receipt) == (
        "\nTotal:                              0.00\n"
    )


def test_printed_receipt_without_offers(teller, cart, rice, toothbrush, apples):
    cart.add_item(rice)
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item_quantity(apples, 1.5)

    receipt = teller.checks_out_articles_from(cart)

    assert ReceiptPrinter().print_receipt(receipt) == (
        "rice                                2.49\n"
        "toothbrush                          1.98\n"
        "  0.99 * 2\n"
        "apples                              2.98\n"
        "  1.99 * 1.500\n"
        "\n"
        "Total:                              7.46\n"
    )


def test_printed_receipt_with_all_offer_types(
    teller, cart, toothbrush, apples, cherry_tomatoes, toothpaste, rice
):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, apples, 20.0)
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)
    cart.add_item_quantity(toothbrush, 3)
    cart.add_item_quantity(apples, 2.5)
    cart.add_item_quantity(cherry_tomatoes, 2)
    cart.add_item_quantity(toothpaste, 5)
    cart.add_item(rice)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(16.93)
    assert ReceiptPrinter().print_receipt(receipt) == (
        "toothbrush                          2.97\n"
        "  0.99 * 3\n"
        "apples                              4.97\n"
        "  1.99 * 2.500\n"
        "cherry tomatoes                     1.38\n"
        "  0.69 * 2\n"
        "toothpaste                          8.95\n"
        "  1.79 * 5\n"
        "rice                                2.49\n"
        "3 for 2 (toothbrush)               -0.99\n"
        "20.0% off (apples)                 -0.99\n"
        "2 for 0.99 (cherry tomatoes)       -0.39\n"
        "5 for 7.49 (toothpaste)            -1.46\n"
        "\n"
        "Total:                             16.93\n"
    )


def test_printed_receipt_of_two_for_amount_with_odd_quantity(
    teller, cart, cherry_tomatoes
):
    """DEFEITO DO LEGADO CORRIGIDO: antes o "desconto" saía positivo (0.10)."""
    receipt = checkout_with_offer(
        teller, cart, cherry_tomatoes, 3, SpecialOfferType.TWO_FOR_AMOUNT, 0.99
    )

    assert ReceiptPrinter().print_receipt(receipt) == (
        "cherry tomatoes                     2.07\n"
        "  0.69 * 3\n"
        "2 for 0.99 (cherry tomatoes)       -0.39\n"
        "\n"
        "Total:                              1.68\n"
    )


# ---------------------------------------------------------------------------
# Contrato das interfaces públicas
# ---------------------------------------------------------------------------


def test_handle_offers_can_be_called_directly_on_the_cart(catalog, cart, toothbrush):
    offers = {toothbrush: Offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)}
    cart.add_item_quantity(toothbrush, 3)
    receipt = Receipt()

    cart.handle_offers(receipt, offers, catalog)

    assert [discount.description for discount in receipt.discounts] == ["3 for 2"]
    assert receipt.total_price() == pytest.approx(-0.99)


def test_receipt_returns_copies_of_its_lists(rice):
    receipt = Receipt()
    receipt.add_product(rice, 1, 2.49, 2.49)

    receipt.items.clear()
    receipt.discounts.append("qualquer coisa")

    assert len(receipt.items) == 1
    assert receipt.discounts == []


def test_teller_finds_product_by_name(teller, rice):
    assert teller.product_with_name("rice") == rice
    assert teller.product_with_name("unknown") is None


def test_real_catalog_cannot_be_used_in_unit_tests(rice):
    catalog = SupermarketCatalog()

    with pytest.raises(Exception, match="accesses the database"):
        catalog.add_product(rice, 2.49)
    with pytest.raises(Exception, match="accesses the database"):
        catalog.unit_price(rice)
