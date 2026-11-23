"""Fixtures compartilhadas pelos testes: produtos, catálogo, caixa e carrinho.

Os preços são os mesmos dos exemplos do README do projeto.
"""

import pytest

from model_objects import Product, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


@pytest.fixture
def toothbrush():
    return Product("toothbrush", ProductUnit.EACH)


@pytest.fixture
def toothpaste():
    return Product("toothpaste", ProductUnit.EACH)


@pytest.fixture
def rice():
    return Product("rice", ProductUnit.EACH)


@pytest.fixture
def cherry_tomatoes():
    return Product("cherry tomatoes", ProductUnit.EACH)


@pytest.fixture
def apples():
    return Product("apples", ProductUnit.KILO)


@pytest.fixture
def catalog(toothbrush, toothpaste, rice, cherry_tomatoes, apples):
    """Catálogo falso (stub): substitui o catálogo real, que acessa o banco de dados."""
    catalog = FakeCatalog()
    catalog.add_product(toothbrush, 0.99)
    catalog.add_product(toothpaste, 1.79)
    catalog.add_product(rice, 2.49)
    catalog.add_product(cherry_tomatoes, 0.69)
    catalog.add_product(apples, 1.99)
    return catalog


@pytest.fixture
def teller(catalog):
    return Teller(catalog)


@pytest.fixture
def cart():
    return ShoppingCart()
