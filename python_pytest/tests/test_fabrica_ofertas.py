import pytest

from model_objects import Offer, Product, ProductUnit, SpecialOfferType
from offer_strategies import (
    FiveForAmountStrategy,
    PercentDiscountStrategy,
    ThreeForTwoStrategy,
    TwoForAmountStrategy,
)
from offer_strategy_factory import OfferStrategyFactory

ESCOVA = Product("toothbrush", ProductUnit.EACH)


@pytest.mark.parametrize(
    "tipo, classe",
    [
        (SpecialOfferType.THREE_FOR_TWO, ThreeForTwoStrategy),
        (SpecialOfferType.TEN_PERCENT_DISCOUNT, PercentDiscountStrategy),
        (SpecialOfferType.TWO_FOR_AMOUNT, TwoForAmountStrategy),
        (SpecialOfferType.FIVE_FOR_AMOUNT, FiveForAmountStrategy),
    ],
)
def test_fabrica_escolhe_a_estrategia_pelo_tipo_da_oferta(tipo, classe):
    estrategia = OfferStrategyFactory.create(Offer(tipo, ESCOVA, 10.0))

    assert isinstance(estrategia, classe)


@pytest.mark.parametrize(
    "tipo, valor, texto",
    [
        (SpecialOfferType.TEN_PERCENT_DISCOUNT, 15.0, "15.0% off"),
        (SpecialOfferType.TWO_FOR_AMOUNT, 0.99, "2 for 0.99"),
        (SpecialOfferType.FIVE_FOR_AMOUNT, 7.49, "5 for 7.49"),
    ],
)
def test_fabrica_passa_o_valor_cadastrado_para_a_estrategia(tipo, valor, texto):
    estrategia = OfferStrategyFactory.create(Offer(tipo, ESCOVA, valor))

    desconto = estrategia.calculate_discount(ESCOVA, 5, 1.0)

    assert desconto.description == texto


def test_fabrica_devolve_none_para_tipo_de_oferta_desconhecido():
    assert OfferStrategyFactory.create(Offer("tipo desconhecido", ESCOVA, 10.0)) is None
