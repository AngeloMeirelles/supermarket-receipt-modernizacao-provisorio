"""Testes da calculadora de descontos, sem criar Teller, ShoppingCart nem Receipt."""
import pytest

from discount_calculator import DiscountCalculator
from model_objects import Offer, Product, ProductUnit, SpecialOfferType
from tests.fake_catalog import FakeCatalog

ESCOVA = Product("toothbrush", ProductUnit.EACH)
ARROZ = Product("rice", ProductUnit.EACH)
MACA = Product("apples", ProductUnit.KILO)


@pytest.fixture
def calculadora():
    catalogo = FakeCatalog()
    catalogo.add_product(ESCOVA, 0.99)
    catalogo.add_product(ARROZ, 2.49)
    catalogo.add_product(MACA, 1.99)
    return DiscountCalculator(catalogo)


def test_sem_ofertas_nao_ha_descontos(calculadora):
    assert calculadora.offer_discounts({ESCOVA: 3}, {}) == []


def test_descontos_seguem_a_ordem_dos_produtos(calculadora):
    ofertas = {
        ESCOVA: Offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0),
        ARROZ: Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ARROZ, 10.0),
    }

    descontos = calculadora.offer_discounts({ARROZ: 1, ESCOVA: 3}, ofertas)

    assert [desconto.product for desconto in descontos] == [ARROZ, ESCOVA]
    assert [desconto.discount_amount for desconto in descontos] == pytest.approx([-0.249, -0.99])


def test_oferta_que_nao_atinge_o_minimo_nao_entra_na_lista(calculadora):
    ofertas = {ESCOVA: Offer(SpecialOfferType.THREE_FOR_TWO, ESCOVA, 0.0)}

    assert calculadora.offer_discounts({ESCOVA: 2}, ofertas) == []


def test_oferta_de_produto_fora_da_compra_nao_gera_desconto(calculadora):
    ofertas = {ESCOVA: Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, ESCOVA, 10.0)}

    assert calculadora.offer_discounts({MACA: 2.5}, ofertas) == []


def test_oferta_de_tipo_desconhecido_nao_gera_desconto(calculadora):
    ofertas = {ESCOVA: Offer("tipo desconhecido", ESCOVA, 10.0)}

    assert calculadora.offer_discounts({ESCOVA: 3}, ofertas) == []


def test_usa_o_preco_do_catalogo(calculadora):
    ofertas = {MACA: Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, MACA, 10.0)}

    [desconto] = calculadora.offer_discounts({MACA: 2.5}, ofertas)

    assert desconto.discount_amount == pytest.approx(-0.4975)
