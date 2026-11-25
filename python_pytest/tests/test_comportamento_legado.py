"""Testes de caracterização do código original (commit c72d68a).

Registram o que o sistema faz hoje, antes da refatoração. O valor esperado de cada teste é o
que o código original devolve, inclusive nos itens mantidos por decisão da equipe (D5, D8,
D10, D12 e D13, seção 3.1 do plano de contingência). Estes testes não são alterados durante a
refatoração: se um deles falhar, a refatoração mudou um comportamento.
"""
import pytest

from catalog import SupermarketCatalog
from model_objects import Discount, Offer, Product, ProductQuantity, ProductUnit, SpecialOfferType
from receipt import Receipt
from receipt_printer import ReceiptPrinter
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog

ESCOVA = Product("toothbrush", ProductUnit.EACH)
MACA = Product("apples", ProductUnit.KILO)
ARROZ = Product("rice", ProductUnit.EACH)
CREME_DENTAL = Product("toothpaste", ProductUnit.EACH)
TOMATE = Product("cherry tomatoes", ProductUnit.EACH)

MENSAGEM_DO_CATALOGO = "cannot be called from a unit test - it accesses the database"


@pytest.fixture
def catalogo():
    """Catálogo de teste com os preços do README do kata."""
    catalogo = FakeCatalog()
    catalogo.add_product(ESCOVA, 0.99)
    catalogo.add_product(MACA, 1.99)
    catalogo.add_product(ARROZ, 2.49)
    catalogo.add_product(CREME_DENTAL, 1.79)
    catalogo.add_product(TOMATE, 0.69)
    return catalogo


@pytest.fixture
def caixa(catalogo):
    return Teller(catalogo)


def fechar_compra(caixa, *itens):
    """Monta um carrinho com os pares (produto, quantidade) e fecha a compra no caixa."""
    carrinho = ShoppingCart()
    for produto, quantidade in itens:
        carrinho.add_item_quantity(produto, quantidade)
    return caixa.checks_out_articles_from(carrinho)


# Carrinho e recibo sem oferta (RF01, RF02 e RF03)

def test_carrinho_vazio_gera_recibo_vazio(caixa):
    recibo = fechar_compra(caixa)

    assert recibo.items == []
    assert recibo.discounts == []
    assert recibo.total_price() == 0


def test_recibo_tem_uma_linha_por_item_na_ordem_do_carrinho(caixa):
    recibo = fechar_compra(caixa, (ESCOVA, 1), (MACA, 2.5))

    escova, maca = recibo.items
    assert escova.product is ESCOVA
    assert escova.quantity == 1
    assert escova.price == 0.99
    assert escova.total_price == pytest.approx(0.99)
    assert maca.product is MACA
    assert maca.quantity == 2.5
    assert maca.price == 1.99
    assert maca.total_price == pytest.approx(4.975)


def test_total_sem_oferta_e_a_soma_dos_itens(caixa):
    recibo = fechar_compra(caixa, (ESCOVA, 1), (MACA, 2.5))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(5.965)


def test_mesmo_produto_adicionado_duas_vezes_gera_duas_linhas(caixa):
    recibo = fechar_compra(caixa, (ESCOVA, 2), (ESCOVA, 1))

    primeira, segunda = recibo.items
    assert primeira.quantity == 2
    assert primeira.total_price == pytest.approx(1.98)
    assert segunda.quantity == 1
    assert segunda.total_price == pytest.approx(0.99)
    assert recibo.total_price() == pytest.approx(2.97)


def test_oferta_considera_a_soma_das_linhas_do_mesmo_produto(caixa):
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)

    recibo = fechar_compra(caixa, (ESCOVA, 2), (ESCOVA, 1))

    assert len(recibo.items) == 2
    [desconto] = recibo.discounts
    assert desconto.discount_amount == pytest.approx(-0.99)
    assert recibo.total_price() == pytest.approx(1.98)


# Oferta de produto que não está no carrinho (RF04)

def test_oferta_de_produto_fora_do_carrinho_nao_gera_desconto(caixa):
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ESCOVA, 10.0)

    recibo = fechar_compra(caixa, (MACA, 2.5))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(4.975)


# Troca de oferta (RF05)

def test_nova_oferta_substitui_a_anterior_do_mesmo_produto(caixa):
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ESCOVA, 10.0)
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)

    recibo = fechar_compra(caixa, (ESCOVA, 3))

    assert caixa.offers[ESCOVA].offer_type == SpecialOfferType.THREE_FOR_TWO
    [desconto] = recibo.discounts
    assert desconto.description == "3 for 2"
    assert recibo.total_price() == pytest.approx(1.98)


# Leve 3, pague 2 (RF06)

def test_leve_3_pague_2_abaixo_do_minimo_nao_gera_desconto(caixa):
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)

    recibo = fechar_compra(caixa, (ESCOVA, 2))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(1.98)


@pytest.mark.parametrize(
    "quantidade, desconto_esperado, total_esperado",
    [
        (3, -0.99, 1.98),
        (6, -1.98, 3.96),
        (7, -1.98, 4.95),
    ],
)
def test_leve_3_pague_2(caixa, quantidade, desconto_esperado, total_esperado):
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)

    recibo = fechar_compra(caixa, (ESCOVA, quantidade))

    [desconto] = recibo.discounts
    assert desconto.product is ESCOVA
    assert desconto.description == "3 for 2"
    assert desconto.discount_amount == pytest.approx(desconto_esperado)
    assert recibo.total_price() == pytest.approx(total_esperado)


# Desconto percentual (RF07)

@pytest.mark.parametrize(
    "quantidade, desconto_esperado, total_esperado",
    [
        (1, -0.249, 2.241),
        (2, -0.498, 4.482),
    ],
)
def test_desconto_percentual(caixa, quantidade, desconto_esperado, total_esperado):
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ARROZ, 10.0)

    recibo = fechar_compra(caixa, (ARROZ, quantidade))

    [desconto] = recibo.discounts
    assert desconto.product is ARROZ
    assert desconto.description == "10.0% off"
    assert desconto.discount_amount == pytest.approx(desconto_esperado)
    assert recibo.total_price() == pytest.approx(total_esperado)


def test_desconto_percentual_vale_sobre_fracao_de_peso(caixa):
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, MACA, 10.0)

    recibo = fechar_compra(caixa, (MACA, 2.5))

    [desconto] = recibo.discounts
    assert desconto.discount_amount == pytest.approx(-0.4975)
    assert recibo.total_price() == pytest.approx(4.4775)


def test_ten_percent_discount_aplica_o_percentual_cadastrado_item_mantido_d8(caixa):
    # Item mantido D8: o nome diz 10%, mas a oferta aplica o percentual cadastrado.
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, MACA, 20.0)

    recibo = fechar_compra(caixa, (MACA, 1))

    [desconto] = recibo.discounts
    assert desconto.description == "20.0% off"
    assert desconto.discount_amount == pytest.approx(-0.398)
    assert recibo.total_price() == pytest.approx(1.592)


# 2 por um valor (RF08)

def test_dois_por_valor_com_1_unidade_nao_gera_desconto(caixa):
    caixa.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, TOMATE, 0.99)

    recibo = fechar_compra(caixa, (TOMATE, 1))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(0.69)


@pytest.mark.parametrize(
    "quantidade, desconto_esperado, total_esperado",
    [
        (2, -0.39, 0.99),
        (4, -0.78, 1.98),
    ],
)
def test_dois_por_valor_com_quantidade_par(caixa, quantidade, desconto_esperado, total_esperado):
    caixa.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, TOMATE, 0.99)

    recibo = fechar_compra(caixa, (TOMATE, quantidade))

    [desconto] = recibo.discounts
    assert desconto.product is TOMATE
    assert desconto.description == "2 for 0.99"
    assert desconto.discount_amount == pytest.approx(desconto_esperado)
    assert recibo.total_price() == pytest.approx(total_esperado)


def test_dois_por_valor_com_3_unidades_cobra_a_mais_item_mantido_d12(caixa):
    # Item mantido D12: o código conta 1,5 par e ainda cobra a unidade que sobra.
    # O "desconto" fica positivo e o total passa dos 2,07 sem oferta. O certo seria 1,68.
    caixa.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, TOMATE, 0.99)

    recibo = fechar_compra(caixa, (TOMATE, 3))

    [desconto] = recibo.discounts
    assert desconto.description == "2 for 0.99"
    assert desconto.discount_amount == pytest.approx(0.105)
    assert recibo.total_price() == pytest.approx(2.175)


def test_dois_por_valor_com_5_unidades_cobra_a_mais_item_mantido_d12(caixa):
    # Item mantido D12: o código conta 2,5 pares e ainda cobra a unidade que sobra.
    # O certo seria 2,67.
    caixa.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, TOMATE, 0.99)

    recibo = fechar_compra(caixa, (TOMATE, 5))

    [desconto] = recibo.discounts
    assert desconto.discount_amount == pytest.approx(-0.285)
    assert recibo.total_price() == pytest.approx(3.165)


# 5 por um valor (RF09)

def test_cinco_por_valor_abaixo_do_minimo_nao_gera_desconto(caixa):
    caixa.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, CREME_DENTAL, 7.49)

    recibo = fechar_compra(caixa, (CREME_DENTAL, 4))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(7.16)


@pytest.mark.parametrize(
    "quantidade, desconto_esperado, total_esperado",
    [
        (5, -1.46, 7.49),
        (6, -1.46, 9.28),
        (10, -2.92, 14.98),
    ],
)
def test_cinco_por_valor(caixa, quantidade, desconto_esperado, total_esperado):
    caixa.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, CREME_DENTAL, 7.49)

    recibo = fechar_compra(caixa, (CREME_DENTAL, quantidade))

    [desconto] = recibo.discounts
    assert desconto.product is CREME_DENTAL
    assert desconto.description == "5 for 7.49"
    assert desconto.discount_amount == pytest.approx(desconto_esperado)
    assert recibo.total_price() == pytest.approx(total_esperado)


# Frações de peso nas ofertas por quantidade (RF10)

def test_fracao_de_peso_nao_completa_grupo_da_oferta(caixa):
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, MACA, 0.0)

    recibo = fechar_compra(caixa, (MACA, 2.5))

    assert recibo.discounts == []
    assert recibo.total_price() == pytest.approx(4.975)


def test_fracao_de_peso_sai_de_graca_item_mantido_d13(caixa):
    # Item mantido D13: os grupos usam só os 3 kg inteiros, mas o desconto é calculado
    # sobre os 3,5 kg. O 0,5 kg não é cobrado. O certo seria 4,975.
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, MACA, 0.0)

    recibo = fechar_compra(caixa, (MACA, 3.5))

    [desconto] = recibo.discounts
    assert desconto.discount_amount == pytest.approx(-2.985)
    assert recibo.total_price() == pytest.approx(3.98)


# Ordem dos descontos e combinação de ofertas (RF11)

def test_descontos_seguem_a_ordem_do_carrinho(caixa):
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ARROZ, 10.0)

    recibo = fechar_compra(caixa, (ARROZ, 1), (ESCOVA, 3))

    arroz, escova = recibo.discounts
    assert arroz.product is ARROZ
    assert arroz.discount_amount == pytest.approx(-0.249)
    assert escova.product is ESCOVA
    assert escova.discount_amount == pytest.approx(-0.99)


def test_todas_as_ofertas_no_mesmo_carrinho(caixa):
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ARROZ, 10.0)
    caixa.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, CREME_DENTAL, 7.49)
    caixa.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, TOMATE, 0.99)

    recibo = fechar_compra(
        caixa, (ESCOVA, 3), (ARROZ, 2), (CREME_DENTAL, 5), (TOMATE, 2), (MACA, 1)
    )

    descricoes = [desconto.description for desconto in recibo.discounts]
    assert descricoes == ["3 for 2", "10.0% off", "5 for 7.49", "2 for 0.99"]
    assert recibo.total_price() == pytest.approx(16.932)


# Recibo impresso pelo ReceiptPrinter (RNF02)

def test_recibo_impresso_com_itens_e_desconto(caixa):
    caixa.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ARROZ, 10.0)
    recibo = fechar_compra(caixa, (ESCOVA, 1), (ARROZ, 2), (MACA, 2.5))

    impresso = ReceiptPrinter().print_receipt(recibo)

    assert impresso == (
        "toothbrush                          0.99\n"
        "rice                                4.98\n"
        "  2.49 * 2\n"
        "apples                              4.97\n"
        "  1.99 * 2.500\n"
        "10.0% off (rice)                   -0.50\n"
        "\n"
        "Total:                             10.45\n"
    )


def test_recibo_impresso_com_leve_3_pague_2(caixa):
    caixa.add_special_offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)
    recibo = fechar_compra(caixa, (ESCOVA, 3))

    impresso = ReceiptPrinter().print_receipt(recibo)

    assert impresso == (
        "toothbrush                          2.97\n"
        "  0.99 * 3\n"
        "3 for 2 (toothbrush)               -0.99\n"
        "\n"
        "Total:                              1.98\n"
    )


def test_recibo_impresso_vazio(caixa):
    recibo = fechar_compra(caixa)

    impresso = ReceiptPrinter().print_receipt(recibo)

    assert impresso == "\nTotal:                              0.00\n"


# Interfaces públicas que o teste original não usa (RNF01)

def test_add_item_adiciona_uma_unidade():
    carrinho = ShoppingCart()

    carrinho.add_item(ESCOVA)

    [item] = carrinho.items
    assert isinstance(item, ProductQuantity)
    assert item.product is ESCOVA
    assert item.quantity == 1.0
    assert carrinho.product_quantities == {ESCOVA: 1.0}


def test_product_quantities_soma_as_quantidades_do_mesmo_produto():
    carrinho = ShoppingCart()

    carrinho.add_item_quantity(MACA, 1.5)
    carrinho.add_item_quantity(MACA, 2.0)

    assert len(carrinho.items) == 2
    assert carrinho.product_quantities == {MACA: 3.5}


def test_handle_offers_chamado_diretamente_adiciona_so_os_descontos(catalogo):
    carrinho = ShoppingCart()
    carrinho.add_item_quantity(ESCOVA, 3)
    ofertas = {ESCOVA: Offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)}
    recibo = Receipt()

    carrinho.handle_offers(recibo, ofertas, catalogo)

    assert recibo.items == []
    [desconto] = recibo.discounts
    assert desconto.description == "3 for 2"
    assert desconto.discount_amount == pytest.approx(-0.99)


def test_recibo_montado_diretamente():
    recibo = Receipt()

    recibo.add_product(ESCOVA, 2, 0.99, 1.98)
    recibo.add_discount(Discount(ESCOVA, "teste", -0.5))

    [item] = recibo.items
    assert item.product is ESCOVA
    assert item.quantity == 2
    assert item.price == 0.99
    assert item.total_price == 1.98
    [desconto] = recibo.discounts
    assert desconto.product is ESCOVA
    assert desconto.description == "teste"
    assert desconto.discount_amount == -0.5
    assert recibo.total_price() == pytest.approx(1.48)


def test_items_e_discounts_do_recibo_devolvem_copias():
    recibo = Receipt()
    recibo.add_product(ESCOVA, 1, 0.99, 0.99)
    recibo.add_discount(Discount(ESCOVA, "teste", -0.5))

    recibo.items.clear()
    recibo.discounts.clear()

    assert len(recibo.items) == 1
    assert len(recibo.discounts) == 1


def test_caixa_guarda_o_catalogo_e_comeca_sem_ofertas(catalogo):
    caixa = Teller(catalogo)

    assert caixa.catalog is catalogo
    assert caixa.offers == {}


# Itens mantidos D5 e D10 (seção 3.1 do plano de contingência)

def test_product_with_name_com_catalogo_de_teste(caixa):
    assert caixa.product_with_name("toothbrush") is ESCOVA
    assert caixa.product_with_name("produto inexistente") is None


def test_product_with_name_falha_com_catalogo_real_item_mantido_d5():
    # Item mantido D5: o caixa lê catalog.products, que só o FakeCatalog tem.
    caixa = Teller(SupermarketCatalog())

    with pytest.raises(AttributeError, match="products"):
        caixa.product_with_name("toothbrush")


def test_catalogo_real_lanca_exception_generica_item_mantido_d10():
    # Item mantido D10: os dois métodos lançam Exception genérica com a mesma mensagem.
    catalogo = SupermarketCatalog()

    with pytest.raises(Exception, match=MENSAGEM_DO_CATALOGO) as erro_add_product:
        catalogo.add_product(ESCOVA, 0.99)
    with pytest.raises(Exception, match=MENSAGEM_DO_CATALOGO) as erro_unit_price:
        catalogo.unit_price(ESCOVA)

    assert erro_add_product.type is Exception
    assert erro_unit_price.type is Exception
