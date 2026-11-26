"""Testes de cada regra de oferta isolada (RNF05).

Cada teste chama a estratégia da oferta direto, sem criar Teller, ShoppingCart nem Receipt.
Os itens mantidos (D8, D12 e D13) aparecem com o mesmo resultado do código original.
"""
import pytest

from model_objects import Product, ProductUnit
from offer_strategies import (
    FiveForAmountStrategy,
    IOfferStrategy,
    PercentDiscountStrategy,
    ThreeForTwoStrategy,
    TwoForAmountStrategy,
)

ESCOVA = Product("toothbrush", ProductUnit.EACH)
MACA = Product("apples", ProductUnit.KILO)
ARROZ = Product("rice", ProductUnit.EACH)
CREME_DENTAL = Product("toothpaste", ProductUnit.EACH)
TOMATE = Product("cherry tomatoes", ProductUnit.EACH)


# Interface comum das ofertas

@pytest.mark.parametrize(
    "estrategia",
    [
        ThreeForTwoStrategy(),
        PercentDiscountStrategy(10.0),
        TwoForAmountStrategy(0.99),
        FiveForAmountStrategy(7.49),
    ],
)
def test_todas_as_ofertas_seguem_a_mesma_interface(estrategia):
    assert isinstance(estrategia, IOfferStrategy)


def test_interface_nao_pode_ser_criada_sozinha():
    with pytest.raises(TypeError):
        IOfferStrategy()


# Leve 3, pague 2 (RF06)

def test_leve_3_pague_2_abaixo_do_minimo_nao_da_desconto():
    assert ThreeForTwoStrategy().calculate_discount(ESCOVA, 2, 0.99) is None


@pytest.mark.parametrize(
    "quantidade, desconto_esperado",
    [
        (3, -0.99),
        (7, -1.98),
    ],
)
def test_leve_3_pague_2(quantidade, desconto_esperado):
    desconto = ThreeForTwoStrategy().calculate_discount(ESCOVA, quantidade, 0.99)

    assert desconto.product is ESCOVA
    assert desconto.description == "3 for 2"
    assert desconto.discount_amount == pytest.approx(desconto_esperado)


def test_leve_3_pague_2_nao_cobra_fracao_de_peso_item_mantido_d13():
    desconto = ThreeForTwoStrategy().calculate_discount(MACA, 3.5, 1.99)

    assert desconto.discount_amount == pytest.approx(-2.985)


# Desconto percentual (RF07)

def test_desconto_percentual():
    desconto = PercentDiscountStrategy(10.0).calculate_discount(ARROZ, 2, 2.49)

    assert desconto.product is ARROZ
    assert desconto.description == "10.0% off"
    assert desconto.discount_amount == pytest.approx(-0.498)


def test_desconto_percentual_aplica_o_percentual_cadastrado_item_mantido_d8():
    desconto = PercentDiscountStrategy(20.0).calculate_discount(MACA, 1, 1.99)

    assert desconto.description == "20.0% off"
    assert desconto.discount_amount == pytest.approx(-0.398)


# 2 por um valor (RF08)

def test_dois_por_valor_com_1_unidade_nao_da_desconto():
    assert TwoForAmountStrategy(0.99).calculate_discount(TOMATE, 1, 0.69) is None


@pytest.mark.parametrize(
    "quantidade, desconto_esperado",
    [
        (2, -0.39),
        (4, -0.78),
    ],
)
def test_dois_por_valor_com_quantidade_par(quantidade, desconto_esperado):
    desconto = TwoForAmountStrategy(0.99).calculate_discount(TOMATE, quantidade, 0.69)

    assert desconto.product is TOMATE
    assert desconto.description == "2 for 0.99"
    assert desconto.discount_amount == pytest.approx(desconto_esperado)


@pytest.mark.parametrize(
    "quantidade, desconto_esperado",
    [
        (3, 0.105),
        (5, -0.285),
    ],
)
def test_dois_por_valor_com_quantidade_impar_cobra_a_mais_item_mantido_d12(quantidade, desconto_esperado):
    desconto = TwoForAmountStrategy(0.99).calculate_discount(TOMATE, quantidade, 0.69)

    assert desconto.discount_amount == pytest.approx(desconto_esperado)


# 5 por um valor (RF09)

def test_cinco_por_valor_abaixo_do_minimo_nao_da_desconto():
    assert FiveForAmountStrategy(7.49).calculate_discount(CREME_DENTAL, 4, 1.79) is None


@pytest.mark.parametrize(
    "quantidade, desconto_esperado",
    [
        (5, -1.46),
        (6, -1.46),
    ],
)
def test_cinco_por_valor(quantidade, desconto_esperado):
    desconto = FiveForAmountStrategy(7.49).calculate_discount(CREME_DENTAL, quantidade, 1.79)

    assert desconto.product is CREME_DENTAL
    assert desconto.description == "5 for 7.49"
    assert desconto.discount_amount == pytest.approx(desconto_esperado)
