import pytest

from bundle_calculator import BundleCalculator
from model_objects import Bundle, Product, ProductUnit, SpecialOfferType
from receipt_printer import ReceiptPrinter
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog

ESCOVA = Product("toothbrush", ProductUnit.EACH)
CREME_DENTAL = Product("toothpaste", ProductUnit.EACH)
FIO_DENTAL = Product("dental floss", ProductUnit.EACH)
MACA = Product("apples", ProductUnit.KILO)

COMBO = "bundle 10% off"


@pytest.fixture
def catalogo():
    catalogo = FakeCatalog()
    catalogo.add_product(ESCOVA, 10.00)
    catalogo.add_product(CREME_DENTAL, 15.00)
    catalogo.add_product(FIO_DENTAL, 5.00)
    catalogo.add_product(MACA, 2.00)
    return catalogo


@pytest.fixture
def caixa_com_combo(catalogo):
    caixa = Teller(catalogo)
    caixa.add_bundle_offer([ESCOVA, CREME_DENTAL])
    return caixa


def fechar_compra(caixa, *itens):
    carrinho = ShoppingCart()
    for produto, quantidade in itens:
        carrinho.add_item_quantity(produto, quantidade)
    return caixa.checks_out_articles_from(carrinho)


def linhas_de_desconto(recibo):
    return [(desconto.product, desconto.description, desconto.discount_amount) for desconto in recibo.discounts]


def test_combo_completo(caixa_com_combo):
    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 1), (CREME_DENTAL, 1))

    assert linhas_de_desconto(recibo) == [
        (ESCOVA, COMBO, pytest.approx(-1.00)),
        (CREME_DENTAL, COMBO, pytest.approx(-1.50)),
    ]
    assert recibo.total_price() == pytest.approx(22.50)


def test_combo_incompleto_nao_da_desconto(caixa_com_combo):
    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 1))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(10.00)


def test_combo_repetido(caixa_com_combo):
    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 2), (CREME_DENTAL, 2))

    assert linhas_de_desconto(recibo) == [
        (ESCOVA, COMBO, pytest.approx(-2.00)),
        (CREME_DENTAL, COMBO, pytest.approx(-3.00)),
    ]
    assert recibo.total_price() == pytest.approx(45.00)


def test_produto_excedente_paga_preco_normal(caixa_com_combo):
    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 2), (CREME_DENTAL, 1))

    assert linhas_de_desconto(recibo) == [
        (ESCOVA, COMBO, pytest.approx(-1.00)),
        (CREME_DENTAL, COMBO, pytest.approx(-1.50)),
    ]
    assert recibo.total_price() == pytest.approx(32.50)


def test_cadastro_de_combo_com_produtos_diferentes(catalogo):
    caixa = Teller(catalogo)

    caixa.add_bundle_offer([ESCOVA, CREME_DENTAL])

    [combo] = caixa.bundles
    assert combo.products == (ESCOVA, CREME_DENTAL)


@pytest.mark.parametrize(
    "produtos",
    [[], [ESCOVA], [ESCOVA, ESCOVA]],
    ids=["sem_produtos", "um_produto", "produto_repetido"],
)
def test_cadastro_de_combo_recusa_menos_de_dois_produtos_diferentes(catalogo, produtos):
    caixa = Teller(catalogo)

    with pytest.raises(ValueError):
        caixa.add_bundle_offer(produtos)

    assert caixa.bundles == []


def test_produto_por_peso_entra_no_combo_so_com_quilos_inteiros(catalogo):
    caixa = Teller(catalogo)
    caixa.add_bundle_offer([MACA, ESCOVA])

    recibo = fechar_compra(caixa, (MACA, 1.5), (ESCOVA, 1))

    assert linhas_de_desconto(recibo) == [
        (MACA, COMBO, pytest.approx(-0.20)),
        (ESCOVA, COMBO, pytest.approx(-1.00)),
    ]
    assert recibo.total_price() == pytest.approx(11.80)


def test_produto_por_peso_sem_quilo_inteiro_nao_forma_combo(catalogo):
    caixa = Teller(catalogo)
    caixa.add_bundle_offer([MACA, ESCOVA])

    recibo = fechar_compra(caixa, (MACA, 0.5), (ESCOVA, 1))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(11.00)


def test_produto_com_oferta_propria_fica_fora_do_combo(caixa_com_combo):
    caixa_com_combo.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)

    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 3), (CREME_DENTAL, 1))

    assert linhas_de_desconto(recibo) == [(ESCOVA, "3 for 2", pytest.approx(-10.00))]
    assert recibo.total_price() == pytest.approx(35.00)


def test_produto_com_oferta_propria_fica_fora_mesmo_sem_desconto_da_oferta(caixa_com_combo):
    caixa_com_combo.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)

    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 1), (CREME_DENTAL, 1))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(25.00)


@pytest.fixture
def caixa_com_dois_combos(catalogo):
    caixa = Teller(catalogo)
    caixa.add_bundle_offer([ESCOVA, CREME_DENTAL])
    caixa.add_bundle_offer([ESCOVA, FIO_DENTAL])
    return caixa


def test_combo_cadastrado_primeiro_fica_com_a_unidade_em_comum(caixa_com_dois_combos):
    recibo = fechar_compra(caixa_com_dois_combos, (ESCOVA, 1), (CREME_DENTAL, 1), (FIO_DENTAL, 1))

    assert linhas_de_desconto(recibo) == [
        (ESCOVA, COMBO, pytest.approx(-1.00)),
        (CREME_DENTAL, COMBO, pytest.approx(-1.50)),
    ]
    assert recibo.total_price() == pytest.approx(27.50)


def test_multiplos_combos_com_produto_em_comum(caixa_com_dois_combos):
    recibo = fechar_compra(caixa_com_dois_combos, (ESCOVA, 2), (CREME_DENTAL, 1), (FIO_DENTAL, 1))

    assert linhas_de_desconto(recibo) == [
        (ESCOVA, COMBO, pytest.approx(-1.00)),
        (CREME_DENTAL, COMBO, pytest.approx(-1.50)),
        (ESCOVA, COMBO, pytest.approx(-1.00)),
        (FIO_DENTAL, COMBO, pytest.approx(-0.50)),
    ]
    assert recibo.total_price() == pytest.approx(36.00)


def test_descontos_de_combo_vem_depois_dos_descontos_das_ofertas(caixa_com_combo):
    caixa_com_combo.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, FIO_DENTAL, 10.0)

    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 1), (CREME_DENTAL, 1), (FIO_DENTAL, 1))

    assert linhas_de_desconto(recibo) == [
        (FIO_DENTAL, "10.0% off", pytest.approx(-0.50)),
        (ESCOVA, COMBO, pytest.approx(-1.00)),
        (CREME_DENTAL, COMBO, pytest.approx(-1.50)),
    ]
    assert recibo.total_price() == pytest.approx(27.00)


def test_recibo_sem_combo_cadastrado_nao_tem_desconto_de_combo(catalogo):
    recibo = fechar_compra(Teller(catalogo), (ESCOVA, 1), (CREME_DENTAL, 1))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(25.00)


def test_recibo_impresso_com_combo(caixa_com_combo):
    recibo = fechar_compra(caixa_com_combo, (ESCOVA, 1), (CREME_DENTAL, 1))

    impresso = ReceiptPrinter().print_receipt(recibo)

    assert impresso == (
        "toothbrush                         10.00\n"
        "toothpaste                         15.00\n"
        "bundle 10% off (toothbrush)        -1.00\n"
        "bundle 10% off (toothpaste)        -1.50\n"
        "\n"
        "Total:                             22.50\n"
    )


def test_calculadora_de_combos_isolada(catalogo):
    calculadora = BundleCalculator(catalogo)

    descontos = calculadora.bundle_discounts(
        {ESCOVA: 2, CREME_DENTAL: 1}, [Bundle([ESCOVA, CREME_DENTAL])], {}
    )

    assert [(desconto.product, desconto.discount_amount) for desconto in descontos] == [
        (ESCOVA, pytest.approx(-1.00)),
        (CREME_DENTAL, pytest.approx(-1.50)),
    ]
