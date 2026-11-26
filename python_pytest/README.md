# Supermarket Receipt: modernização de sistema legado

Trabalho prático da disciplina Alta Qualidade de Software (AV3). A equipe modernizou a versão
`python_pytest` do kata [Supermarket Receipt](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata)
sem mudar o comportamento existente, aplicou dois padrões de projeto, implementou uma promoção
nova (combos com 10% de desconto) e comparou a segurança antes e depois.

O sistema simula o caixa de um supermercado: o cliente coloca produtos no carrinho, o caixa
busca os preços no catálogo, aplica as ofertas e os combos cadastrados e devolve um recibo com
itens, descontos e total.

- Código original: commit `c72d68a` do repositório-base.
- Entrega: branch `modernizacao`.

## 1. Dependências

| Item | Versão |
|---|---|
| Python | 3.11.5 (qualquer 3.10 ou mais novo funciona, por causa da sintaxe `X \| None` nas anotações de tipo) |
| Bibliotecas do projeto | as do `requirements.txt` original, sem nenhuma acrescentada: `pytest`, `approvaltests`, `pytest-approvaltests` e `coverage` |

A lista exata das 24 bibliotecas instaladas, com as versões usadas nas evidências, está em
`docs/evidencias/depois/dependencias_projeto.txt`.

## 2. Ambiente

Os testes e as evidências foram gerados em Windows 10, no terminal **cmd**, com um ambiente
virtual (venv) na pasta `python_pytest`.

Use o cmd, e não o PowerShell, para gerar arquivos de saída com `>`. O PowerShell grava esses
arquivos em outra codificação (UTF-16), e eles ficam ilegíveis no GitHub.

## 3. Execução

Na pasta `python_pytest`:

**Windows (cmd)**

```
py -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

**Linux ou macOS**

```
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

O sistema não tem programa principal: ele é usado pelos testes, que montam o catálogo, o caixa
e o carrinho. Exemplo de uso, como nos testes. Para rodá-lo fora do pytest, na pasta
`python_pytest`, defina antes o caminho de importação com `set PYTHONPATH=src` (cmd) ou
`export PYTHONPATH=src` (Linux ou macOS):

```python
from model_objects import Product, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog

escova = Product("toothbrush", ProductUnit.EACH)
creme = Product("toothpaste", ProductUnit.EACH)
catalogo = FakeCatalog()
catalogo.add_product(escova, 10.00)
catalogo.add_product(creme, 15.00)

caixa = Teller(catalogo)
caixa.add_bundle_offer([escova, creme])   # combo: 10% nos dois

carrinho = ShoppingCart()
carrinho.add_item_quantity(escova, 1)
carrinho.add_item_quantity(creme, 1)
recibo = caixa.checks_out_articles_from(carrinho)
print(recibo.total_price())   # 22.5
```

## 4. Testes

Com a venv ativa, na pasta `python_pytest`:

```
pytest -v
coverage run --source=src -m pytest
coverage report -m
```

Resultado esperado: 100 testes passando e 100% de cobertura de `src/`.

| Arquivo | Testes | O que verifica |
|---|---|---|
| `tests/test_supermarket.py` | 1 | O teste original do kata, sem alteração |
| `tests/test_comportamento_legado.py` | 40 | Caracterização: o comportamento do código original, escrito e executado antes de qualquer mudança e nunca alterado |
| `tests/test_estrategias_oferta.py` | 27 | Cada oferta isolada (Strategy) e a classe base das ofertas por quantidade (Template Method) |
| `tests/test_fabrica_ofertas.py` | 8 | A fábrica que escolhe a estratégia pelo tipo da oferta |
| `tests/test_calculadora_descontos.py` | 6 | A calculadora de descontos das ofertas |
| `tests/test_combos.py` | 18 | Os combos promocionais |

Antes da modernização, o projeto tinha 1 teste e 71% de cobertura. O resumo completo está em
`docs/evidencias_testes.md`.

## 5. Análises de segurança

Três ferramentas foram executadas antes e depois da modernização: Bandit 1.9.4 (código),
pip-audit 2.10.1 e Safety 3.8.1 (bibliotecas). Nenhuma apontou vulnerabilidade, nem antes nem
depois.

As ferramentas ficam num ambiente virtual **separado**, fora do projeto. Se fossem instaladas na
venv do projeto, o pip-audit e o Safety analisariam também as bibliotecas delas.

```
py -m venv ..\..\venv-ferramentas
..\..\venv-ferramentas\Scripts\activate
python -m pip install bandit==1.9.4 pip-audit==2.10.1 safety==3.8.1
```

Comandos, na pasta `python_pytest` (troque `depois` por `antes` para a linha de base):

```
bandit -r src
pip-audit -r docs\evidencias\depois\dependencias_projeto.txt --no-deps
set PYTHONIOENCODING=utf-8
set NO_COLOR=1
safety check -r docs\evidencias\depois\dependencias_projeto.txt
safety scan --target . < NUL
```

O arquivo `dependencias_projeto.txt` é gerado com `python -m pip freeze` na venv do projeto. O
`safety scan` exige conta no serviço Safety; a tentativa sem conta está registrada, e o resultado
vem do `safety check`. As saídas estão em `docs/evidencias/antes/` e `docs/evidencias/depois/`
(arquivos 05 a 07), e a análise completa em `docs/seguranca_antes_depois.md`.

## 6. Estrutura de pastas

```
python_pytest/
├── README.md
├── requirements.txt          igual ao original
├── pytest.ini                coloca src e tests no caminho de importação
├── src/                      código do sistema
│   ├── model_objects.py      produto, oferta, desconto e combo (Bundle)
│   ├── catalog.py            contrato do catálogo de preços
│   ├── shopping_cart.py      carrinho: guarda os itens
│   ├── teller.py             caixa: cadastra ofertas e combos e fecha a compra
│   ├── receipt.py            recibo: itens, descontos e total
│   ├── receipt_printer.py    texto do recibo impresso
│   ├── offer_strategies.py   regras de cada oferta (Strategy e Template Method)
│   ├── offer_strategy_factory.py   escolhe a regra pelo tipo da oferta (fábrica simples)
│   ├── discount_calculator.py      descontos das ofertas
│   └── bundle_calculator.py        descontos dos combos
├── tests/                    testes e o catálogo de teste (fake_catalog.py)
├── docs/                     documentos do trabalho (.md e .pdf)
│   ├── diagramas/            diagramas de classes antes e depois (fonte Mermaid e imagens)
│   └── evidencias/
│       ├── antes/            saídas do código original
│       └── depois/           saídas do código modernizado
└── apresentacao/
    └── slides.pdf
```

A pasta `docs` fica dentro de `python_pytest`, e não na raiz do repositório como na estrutura
sugerida no enunciado, porque o repositório-base tem versões do kata em várias linguagens. O
enunciado diz que a estrutura é ilustrativa e pede para preservar os arquivos do
repositório-base, então as outras pastas não foram tocadas.

## 7. Decisões arquiteturais

| Decisão | Motivo |
|---|---|
| **Strategy**: uma classe por oferta, com a interface `IOfferStrategy` | Tirar do carrinho o `if`/`elif` que calculava todas as ofertas (D1, D2 e D6) e permitir testar cada oferta sozinha |
| **Template Method**: a conta das ofertas por quantidade na classe base `QuantityOfferStrategy` | A mesma conta estava copiada em três ofertas (D3) |
| **Fábrica simples** `OfferStrategyFactory` | Tirar do carrinho a escolha da estratégia. Não é o Factory Method do catálogo de padrões: é uma tabela que escolhe a classe pelo tipo da oferta |
| Calculadoras separadas do carrinho (`DiscountCalculator`, `BundleCalculator`) | O carrinho guardava os itens e calculava as promoções (D4). Agora só guarda os itens |
| Combos em classes próprias (`Bundle`, `BundleCalculator`) | A promoção nova entrou sem alterar o código das ofertas existentes (RNF04) |
| Interfaces públicas mantidas | `handle_offers`, `checks_out_articles_from` e as demais classes e métodos públicos mantêm nome, parâmetros e retorno (RNF01). O teste original passa sem alteração |
| Itens mantidos: D5, D8 (nome `TEN_PERCENT_DISCOUNT`), D10, D12 e D13 | Preservar as regras e os valores do recibo, como pede o enunciado, e comparar saídas idênticas antes e depois. A correção proposta de cada um está no plano de contingência, seção 3.1 |

Os detalhes, com diagramas e trechos de código antes e depois, estão em
`docs/padroes_projeto.md`.

## 8. Documentos

Cada documento está em Markdown (`.md`, a fonte) e em PDF (`.pdf`) na pasta `docs/`.

| Documento | Conteúdo |
|---|---|
| `diagnostico_tecnico` | Como o sistema funciona e os 14 problemas encontrados no código original (D1 a D14) |
| `requisitos` | Requisitos funcionais (RF01 a RF17) e não funcionais (RNF01 a RNF07), decisões sobre os combos e rastreabilidade |
| `plano_contingencia` | Ordem das mudanças, riscos, estratégia de retorno, critérios de aceitação e invariantes |
| `registro_refatoracao` | Cada etapa de código (E3 a E9), com antes e depois e a conferência |
| `padroes_projeto` | Strategy, Template Method e fábrica simples, com diagramas, trechos, testes e SOLID |
| `evidencias_testes` | Testes e cobertura antes e depois, preservação do comportamento e cenários de fronteira |
| `seguranca_antes_depois` | Bandit, pip-audit e Safety antes e depois, triagem e riscos remanescentes |
| `licoes_aprendidas` | Reflexão sobre o processo, decisões e limitações |

A apresentação está em `apresentacao/slides.pdf`.
