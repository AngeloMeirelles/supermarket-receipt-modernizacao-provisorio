# Supermarket Receipt: modernização de sistema legado

Trabalho prático da disciplina Alta Qualidade de Software.

O sistema calcula o valor de um carrinho de supermercado, aplica as promoções
cadastradas e gera o recibo. Este repositório parte do código original do
[SupermarketReceipt-Refactoring-Kata](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata)
(versão `python_pytest`) e contém:

- testes de caracterização do comportamento original;
- refatoração com os padrões Strategy, Template Method e fábrica;
- a nova promoção de combos (10% de desconto nos combos completos);
- evidências de testes e de segurança, antes e depois.

## Requisitos

- Python 3.10 ou superior (desenvolvido e testado com Python 3.11.5, no Windows 10)
- Git

Dependências do projeto (`requirements.txt`): `pytest`, `coverage`,
`approvaltests` e `pytest-approvaltests`. Nenhuma dependência foi adicionada
em relação ao repositório original.

## Preparação do ambiente

Na pasta do projeto (`python_pytest`):

```
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt
```

No Linux ou macOS, a ativação é `source venv/bin/activate`.

## Execução dos testes

```
pytest
pytest -v
```

Cobertura de testes:

```
coverage run --source=src -m pytest
coverage report -m
```

Resultado atual: 94 testes passando e 100% de cobertura em `src/`.

## Análise de segurança

O Bandit, o pip-audit e o Safety ficam em um ambiente virtual separado, para
que as auditorias de dependências considerem apenas os pacotes do projeto:

```
python -m venv venv-ferramentas
.\venv-ferramentas\Scripts\python -m pip install -r requirements-dev.txt
```

Para rodar tudo de uma vez e gravar os resultados em `docs/evidencias/depois/`:

```
.\venv\Scripts\python scripts\gerar_evidencias.py depois
```

O script executa, nesta ordem: pytest, coverage, Bandit, pip-audit e Safety.
Os comandos usados ficam registrados no início de cada arquivo gerado. Para
rodar uma ferramenta isolada:

```
.\venv-ferramentas\Scripts\bandit -r src
.\venv-ferramentas\Scripts\pip-audit -r docs\evidencias\depois\dependencias_instaladas.txt --no-deps
.\venv-ferramentas\Scripts\safety check -r docs\evidencias\depois\dependencias_instaladas.txt
```

O comando `safety scan` exige login em uma conta do Safety. A tentativa está
registrada em `docs/evidencias/depois/05_safety.txt`.

## Estrutura de pastas

```
python_pytest/
├── README.md
├── requirements.txt           dependências do projeto
├── requirements-dev.txt       ferramentas de segurança
├── pytest.ini
├── src/
│   ├── catalog.py                 catálogo de produtos (acesso ao banco)
│   ├── model_objects.py           produto, oferta, desconto e combo
│   ├── receipt.py                 recibo
│   ├── shopping_cart.py           carrinho
│   ├── teller.py                  caixa: registra ofertas e fecha a compra
│   ├── offer_strategies.py        regras de cálculo de cada oferta
│   ├── offer_strategy_factory.py  escolha da regra pelo tipo de oferta
│   └── discount_calculator.py     cálculo dos descontos de uma compra
├── tests/
│   ├── conftest.py                    fixtures compartilhadas
│   ├── fake_catalog.py                catálogo falso usado nos testes
│   ├── receipt_printer.py             impressão do recibo
│   ├── test_supermarket.py            teste original do repositório
│   ├── test_comportamento_legado.py   testes de caracterização
│   ├── test_estrategias_oferta.py     testes dos padrões de projeto
│   └── test_combos.py                 testes da promoção de combos
├── scripts/
│   └── gerar_evidencias.py
└── docs/
    ├── decisoes_tecnicas.md
    └── evidencias/
        ├── antes/                     resultados sobre o código original
        ├── depois/                    resultados sobre o código final
        └── comparativo_antes_depois.md
```

## Exemplo de uso

```python
from model_objects import Product, ProductUnit, SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller

toothbrush = Product("toothbrush", ProductUnit.EACH)
toothpaste = Product("toothpaste", ProductUnit.EACH)
rice = Product("rice", ProductUnit.EACH)

teller = Teller(catalog)  # catalog: um SupermarketCatalog com os preços
teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)
teller.add_bundle_offer([toothbrush, toothpaste])

cart = ShoppingCart()
cart.add_item(toothbrush)
cart.add_item(toothpaste)
cart.add_item_quantity(rice, 2)

receipt = teller.checks_out_articles_from(cart)
print(receipt.total_price())
```

## Decisões arquiteturais

- **Comportamento preservado.** As classes e os métodos públicos do sistema
  original continuam com as mesmas assinaturas e os mesmos resultados. A única
  mudança intencional é a correção de um defeito na oferta "2 por valor" com
  quantidade ímpar, feita em um commit isolado.
- **Strategy.** Cada tipo de oferta é uma classe que implementa a interface
  `IOfferStrategy`. Uma oferta nova não exige alterar as existentes.
- **Template Method.** As ofertas por quantidade compartilham os passos do
  cálculo em `QuantityOfferStrategy`. Cada subclasse informa só o preço do
  grupo e o texto do recibo.
- **Fábrica.** `OfferStrategyFactory` é o único ponto que relaciona o tipo da
  oferta com a classe que a calcula.
- **Responsabilidade única.** O carrinho guarda os itens. O cálculo de
  descontos fica em `DiscountCalculator`. O método
  `ShoppingCart.handle_offers` foi mantido e repassa a chamada.
- **Combos.** `Teller.add_bundle_offer` cadastra um combo. Produto com oferta
  individual não participa de combos, e cada unidade entra em no máximo um
  combo, o que evita desconto duplicado.

O detalhamento, com diagnóstico, diagramas e rastreabilidade, está em
[docs/decisoes_tecnicas.md](docs/decisoes_tecnicas.md). A comparação dos
resultados está em
[docs/evidencias/comparativo_antes_depois.md](docs/evidencias/comparativo_antes_depois.md).
