# Registro da refatoração

Projeto: Supermarket Receipt, versão python_pytest.
Base: etapas definidas no plano de contingência (`docs/plano_contingencia.md`, seção 2).
Data: 25/11/2026.

## 1. Objetivo

Este documento registra cada etapa da refatoração já feita: o que mudou no código, qual item
do diagnóstico foi resolvido, trechos de antes e depois e como foi conferido que o
comportamento não mudou. As próximas etapas são acrescentadas aqui à medida que forem feitas.

## 2. Como cada etapa é conferida

Antes de cada commit:

- `pytest`: todos os testes precisam passar, sem nenhuma alteração nos testes que já existiam.
  Eram 41 até a E4 (40 de caracterização e o teste original), passaram a 60 com os testes das
  ofertas isoladas da E5, a 68 com os testes da classe base da E6 e a 76 com os testes da
  fábrica da E7;
- `coverage run --source=src -m pytest` e `coverage report -m`: a cobertura de `src/` não pode
  cair.

São os critérios de aceitação da seção 6 do plano de contingência. Os testes de caracterização
registram o comportamento do código original, inclusive o dos itens mantidos (D5, D8, D10,
D12 e D13). Se um deles falhar, a etapa mudou um comportamento.

## 3. Resumo

| Etapa | Commit | O que mudou | Item do diagnóstico | Testes | Cobertura de `src/` |
|---|---|---|---|---|---|
| E3 | `1eb7aad` | ReceiptPrinter passa de `tests/` para `src/` | D14 | 41 passaram | 100% (173 linhas) |
| E4 | `014fc79` | Nomes das variáveis internas | D7 | 41 passaram | 100% (172 linhas) |
| E4 | `b0ea27c` | Constantes no lugar dos números soltos | D8 | 41 passaram | 100% (177 linhas) |
| E4 | `9ae05b4` | Anotações de tipo | D9 | 41 passaram | 100% (184 linhas) |
| E5 | `09b4a70` | Uma classe para cada oferta (Strategy) | D1 (em parte), D2 e D6 | 41 passaram | 100% (212 linhas) |
| E5 | `e5c23a6` | Testes de cada oferta isolada | RNF05 e D11 | 60 passaram | 100% (212 linhas) |
| E6 | `9f0255c` | Conta comum das ofertas por quantidade numa classe base (Template Method) | D3 | 60 passaram | 100% (227 linhas) |
| E6 | `60fb453` | Testes da classe base | RNF04 | 68 passaram | 100% (227 linhas) |
| E7 | `0b1c7aa` | Fábrica simples escolhe a estratégia pelo tipo da oferta, com os testes da fábrica | D1 | 76 passaram | 100% (230 linhas) |

O número de linhas muda porque o ReceiptPrinter entrou na conta na E3, uma variável foi
retirada do caixa, as constantes foram acrescentadas, os `import` dos tipos também contam e a
E5 criou o arquivo das ofertas. A cobertura ficou em 100% em todas as etapas.

## 4. E3: impressão do recibo na pasta `src` (D14)

O ReceiptPrinter monta o texto do recibo, que é uma função do sistema, mas estava na pasta de
testes. O arquivo foi movido com `git mv tests\receipt_printer.py src\receipt_printer.py`. O
conteúdo não mudou: o Git registrou a mudança como renomeação com 100% de semelhança.

A forma de importar continua a mesma, `from receipt_printer import ReceiptPrinter`, porque o
`pytest.ini` coloca as pastas `src` e `tests` no caminho de importação. A partir desta etapa,
o ReceiptPrinter entra na cobertura de `src/`, com as 44 linhas cobertas pelos testes do recibo
impresso.

## 5. E4: nomes, constantes e anotações de tipo (D7, D8 e D9)

A E4 foi feita em três commits, um para cada item do diagnóstico, para cada mudança poder ser
revisada e desfeita sozinha.

### 5.1 Nomes das variáveis internas (D7)

Só mudaram nomes de variáveis que existem dentro dos métodos. Os nomes públicos ficaram iguais:
`handle_offers(receipt, offers, catalog)`, `checks_out_articles_from(the_cart)` e o atributo
`ReceiptItem.price`, entre outros (seção 8 do plano).

| Antes | Depois | Arquivo | O que a variável guarda |
|---|---|---|---|
| `p` | `product` | carrinho e caixa | o produto |
| `x` | `group_size` | carrinho | o tamanho do grupo da oferta |
| `number_of_x` | `number_of_groups` | carrinho | quantos grupos completos o cliente levou |
| `total` | `total_with_offer` | carrinho | quanto o cliente paga com a oferta "2 por valor" |
| `discount_n` e `discount_total` | `discount_amount` | carrinho | o valor do desconto, agora com o mesmo nome nas três ofertas por quantidade |
| `pq` | `item` | caixa | um item do carrinho |
| `product_quantities` | retirada | caixa | o laço passa a percorrer `the_cart.items` direto. O nome antigo se confundia com a propriedade `product_quantities` do carrinho, que guarda a soma das quantidades por produto |
| `price` | `total_price` | caixa | o total da linha. Antes, `price` era o preço unitário no recibo e o total da linha no caixa |

Caixa, antes:

```python
product_quantities = the_cart.items
for pq in product_quantities:
    p = pq.product
    quantity = pq.quantity
    unit_price = self.catalog.unit_price(p)
    price = quantity * unit_price
    receipt.add_product(p, quantity, unit_price, price)
```

Caixa, depois:

```python
for item in the_cart.items:
    product = item.product
    quantity = item.quantity
    unit_price = self.catalog.unit_price(product)
    total_price = quantity * unit_price
    receipt.add_product(product, quantity, unit_price, total_price)
```

### 5.2 Constantes no lugar dos números soltos (D8)

Os números usados nas contas das ofertas viraram constantes com nome, no início de
`src/shopping_cart.py`:

| Constante | Valor | O que representa |
|---|---|---|
| `THREE_FOR_TWO_GROUP_SIZE` | 3 | tamanho do grupo do "leve 3, pague 2" |
| `THREE_FOR_TWO_PAID_UNITS` | 2 | unidades pagas em cada grupo do "leve 3, pague 2" |
| `TWO_FOR_AMOUNT_GROUP_SIZE` | 2 | tamanho do grupo do "2 por valor" |
| `FIVE_FOR_AMOUNT_GROUP_SIZE` | 5 | tamanho do grupo do "5 por valor" |
| `PERCENT_BASE` | 100.0 | base do percentual: 10% é 10 dividido por 100 |

"Leve 3, pague 2", antes:

```python
if offer.offer_type == SpecialOfferType.THREE_FOR_TWO and quantity_as_int > 2:
    discount_amount = quantity * unit_price - (
                (number_of_groups * 2 * unit_price) + quantity_as_int % 3 * unit_price)
```

Depois:

```python
if offer.offer_type == SpecialOfferType.THREE_FOR_TWO and quantity_as_int >= THREE_FOR_TWO_GROUP_SIZE:
    discount_amount = quantity * unit_price - (
                (number_of_groups * THREE_FOR_TWO_PAID_UNITS * unit_price) + quantity_as_int % THREE_FOR_TWO_GROUP_SIZE * unit_price)
```

A condição `quantity_as_int > 2` virou `quantity_as_int >= THREE_FOR_TWO_GROUP_SIZE`. Para
números inteiros, "maior que 2" e "maior ou igual a 3" são a mesma coisa, e `quantity_as_int` é
sempre inteiro. A forma nova se lê como a regra de negócio: a oferta vale a partir de um grupo
completo.

Cada constante tem exatamente o valor do número que substituiu, e as contas continuam na mesma
ordem, para evitar diferenças de arredondamento (risco R2 do plano).

Ficaram como estavam, de propósito:

- os textos dos descontos (`"3 for 2"`, `"2 for "` e `"% off"`), que fazem parte do que o
  recibo mostra (RNF02);
- `group_size = 1`, valor padrão que só evita divisão por zero nas ofertas sem grupo. Ele deixa
  de existir quando cada oferta ganhar a própria classe (E5);
- o `1.0` de `add_item`, que significa uma unidade e não estava entre os números do D8;
- o nome `TEN_PERCENT_DISCOUNT`, que faz parte do D8 mas é um item mantido (plano, seção 3.1).

### 5.3 Anotações de tipo (D9)

Todos os parâmetros e retornos de `src/` passaram a declarar o tipo. Exemplo, em
`src/shopping_cart.py`, antes:

```python
def handle_offers(self, receipt, offers, catalog):
```

Depois:

```python
def handle_offers(self, receipt: Receipt, offers: dict[Product, Offer], catalog: SupermarketCatalog) -> None:
```

A assinatura passa a dizer que `offers` é um dicionário de produto para oferta, informação que
antes só se descobria lendo o `teller.py`. Outros pontos:

- `-> Product | None` em `product_with_name` indica que o método devolve um produto ou `None`;
- `list[ReceiptItem]` e `dict[Product, float]` indicam o que vai dentro das listas e dos
  dicionários;
- em `Product`, o tipo `"ProductUnit"` fica entre aspas porque essa classe é definida mais
  abaixo no mesmo arquivo;
- foram acrescentados os `import` necessários para citar os tipos. Nenhum deles cria
  dependência circular entre os arquivos.

Além dos testes, a estrutura dos seis arquivos foi comparada antes e depois, desconsiderando as
anotações e os `import`, e é a mesma: nenhuma conta, mensagem ou nome mudou.

Com os tipos, o D5 fica mais fácil de ver: o caixa declara que recebe um `SupermarketCatalog`,
mas usa `catalog.products`, que essa classe não tem. O D5 é um item mantido e continua como
estava.

### 5.4 Itens mantidos

Nenhuma etapa alterou os itens mantidos (plano, seção 3.1). O `catalog.py` recebeu apenas
anotações de tipo: a exceção genérica e a mensagem do D10 continuam iguais. Os resultados do
D5, do D12 e do D13 continuam os mesmos, conferidos pelos testes de caracterização.

## 6. E5: uma classe para cada oferta (Strategy)

### 6.1 Problema

O método `handle_offers` do carrinho decidia o cálculo de todas as ofertas com uma sequência de
`if` e `elif` (D1). Uma mesma oferta aparecia em pedaços separados do método (D2), e o valor
`argument` da oferta mudava de sentido conforme o tipo: percentual, preço do par ou preço do
grupo de cinco (D6). Também não dava para testar uma oferta sozinha.

### 6.2 Padrão aplicado

Strategy: cada forma de calcular o desconto fica numa classe própria, e todas seguem o mesmo
contrato, a interface `IOfferStrategy`. Quem usa as ofertas não precisa saber como cada uma
calcula; só chama o método do contrato. É a mesma ideia do exemplo das aulas com a interface
`IDesconto`.

O arquivo novo `src/offer_strategies.py` tem a interface e uma classe para cada oferta:

| Classe | Oferta | Valor que recebe |
|---|---|---|
| `IOfferStrategy` | interface com o método `calculate_discount(product, quantity, unit_price)`, que devolve o desconto ou `None` quando a oferta não dá desconto | não se aplica |
| `ThreeForTwoStrategy` | leve 3, pague 2 (RF06) | nenhum |
| `PercentDiscountStrategy` | desconto percentual (RF07) | `percent` |
| `TwoForAmountStrategy` | 2 por um valor (RF08) | `pair_price`, o preço do par |
| `FiveForAmountStrategy` | 5 por um valor (RF09) | `group_price`, o preço do grupo de cinco |

A interface segue o estilo das aulas: `class IOfferStrategy(abc.ABC)` com o método marcado com
`@abc.abstractmethod`. As constantes criadas na E4 passaram para esse arquivo, porque pertencem
às ofertas. Cada classe recebeu a conta da sua oferta exatamente como estava, na mesma ordem
das operações.

### 6.3 Antes e depois

`handle_offers`, antes (trecho):

```python
if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
    group_size = THREE_FOR_TWO_GROUP_SIZE

elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
    group_size = TWO_FOR_AMOUNT_GROUP_SIZE
    if quantity_as_int >= TWO_FOR_AMOUNT_GROUP_SIZE:
        total_with_offer = offer.argument * (quantity_as_int / group_size) + ...
        ...

if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
    group_size = FIVE_FOR_AMOUNT_GROUP_SIZE

number_of_groups = math.floor(quantity_as_int / group_size)
if offer.offer_type == SpecialOfferType.THREE_FOR_TWO and quantity_as_int >= THREE_FOR_TWO_GROUP_SIZE:
    ...
if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
    ...
if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT and quantity_as_int >= FIVE_FOR_AMOUNT_GROUP_SIZE:
    ...
```

Depois:

```python
strategy: IOfferStrategy | None = None
if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
    strategy = ThreeForTwoStrategy()
elif offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
    strategy = PercentDiscountStrategy(offer.argument)
elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
    strategy = TwoForAmountStrategy(offer.argument)
elif offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
    strategy = FiveForAmountStrategy(offer.argument)

if strategy:
    discount = strategy.calculate_discount(product, quantity, unit_price)
    if discount:
        receipt.add_discount(discount)
```

O carrinho agora só escolhe a classe da oferta e pede o desconto a ela. Uma oferta de tipo
desconhecido continua sem desconto, como no código original.

### 6.4 O que foi resolvido e o que fica para as próximas etapas

- D2: resolvido. Cada oferta está inteira na sua classe.
- D6: resolvido. Cada classe dá um nome claro ao valor que recebe, e `Offer.argument`
  continua igual, porque é interface pública.
- D1: resolvido em parte. As contas saíram do método, mas a escolha da classe ainda usa `if` e
  `elif`. Essa escolha passa para uma fábrica na E7.
- D3: continua. As três ofertas por quantidade ainda repetem a mesma conta, agora em classes
  separadas. Isso é tratado com o Template Method na E6.

### 6.5 Itens mantidos

As classes guardam o comportamento dos itens mantidos (plano, seção 3.1):

- `TwoForAmountStrategy` conta os pares com divisão comum, como no original. Um comentário na
  conta explica o D12;
- as três ofertas por quantidade contam os grupos com a parte inteira da quantidade e calculam
  o desconto sobre a quantidade completa, então a fração de peso continua sem cobrança (D13). A
  documentação de cada classe registra isso;
- `PercentDiscountStrategy` aplica o percentual cadastrado, qualquer que seja, e o tipo continua
  se chamando `TEN_PERCENT_DISCOUNT` (D8).

### 6.6 Testes de cada oferta isolada

O arquivo `tests/test_estrategias_oferta.py` tem 19 testes que chamam cada classe direto, sem
criar Teller, ShoppingCart nem Receipt, como pede o RNF05. Exemplo:

```python
desconto = ThreeForTwoStrategy().calculate_discount(ESCOVA, 3, 0.99)
```

Eles cobrem:

- a interface: as quatro classes seguem `IOfferStrategy`, e a interface sozinha não pode ser
  criada;
- cada oferta abaixo do mínimo, no limite e acima dele;
- os itens mantidos D8, D12 e D13, com os mesmos valores do código original.

Antes da refatoração, esses testes não eram possíveis, porque as contas estavam presas dentro do
método do carrinho (D4 e D11).

### 6.7 Conferência

Os 41 testes que já existiam passaram sem nenhuma alteração depois do commit `09b4a70`, e os 60
passaram depois do commit `e5c23a6`. A cobertura de `src/` ficou em 100%, com 212 linhas, e o
arquivo novo das ofertas está todo coberto.

## 7. E6: conta comum das ofertas por quantidade (Template Method)

### 7.1 Problema

Depois da E5, cada oferta tinha a sua classe, mas as três ofertas por quantidade ("leve 3,
pague 2", "2 por valor" e "5 por valor") ainda repetiam a mesma conta, cada uma com os seus
números (D3). Uma correção feita numa cópia não valeria para as outras, e o D12 nasceu
justamente de uma das cópias ser diferente.

As três calculam o desconto do mesmo jeito:

> desconto = quantidade × preço − (preço do grupo × número de grupos + unidades que sobram × preço)

Só mudam o tamanho do grupo, o preço do grupo, o texto do desconto e, no "2 por valor", a forma
de contar os grupos.

### 7.2 Padrão aplicado

Template Method: a conta fica escrita uma vez, numa classe base, com lacunas que cada oferta
preenche. A classe base é `QuantityOfferStrategy`, em `src/offer_strategies.py`. O método
`calculate_discount` dela é o roteiro fixo:

```python
def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
    whole_units = int(quantity)
    if whole_units < self._group_size():
        return None
    price_with_offer = (self._price_per_group(unit_price) * self._number_of_groups(whole_units)
                        + whole_units % self._group_size() * unit_price)
    discount_amount = quantity * unit_price - price_with_offer
    return Discount(product, self._description(), -discount_amount)
```

As lacunas são os métodos que cada oferta escreve:

| Lacuna | Leve 3, pague 2 | 2 por valor | 5 por valor |
|---|---|---|---|
| `_group_size()`: tamanho do grupo | 3 | 2 | 5 |
| `_price_per_group()`: preço de um grupo completo | 2 × preço da unidade | `pair_price` | `group_price` |
| `_description()`: texto no recibo | `3 for 2` | `2 for` e o valor | `5 for` e o valor |
| `_number_of_groups()`: quantos grupos | padrão da classe base | trocado (D12) | padrão da classe base |

As três primeiras lacunas são obrigatórias (`@abc.abstractmethod`). A quarta tem um padrão na
classe base, a contagem de grupos inteiros, e só o "2 por valor" troca. O `_` no início dos
nomes indica que são passos internos do roteiro: quem usa as ofertas continua chamando apenas
`calculate_discount`. A oferta de percentual não é por quantidade e continua ligada direto à
interface `IOfferStrategy`.

### 7.3 Antes e depois

"Leve 3, pague 2", antes:

```python
class ThreeForTwoStrategy(IOfferStrategy):

    def calculate_discount(self, product: Product, quantity: float, unit_price: float) -> Discount | None:
        quantity_as_int = int(quantity)
        if quantity_as_int < THREE_FOR_TWO_GROUP_SIZE:
            return None
        number_of_groups = math.floor(quantity_as_int / THREE_FOR_TWO_GROUP_SIZE)
        discount_amount = quantity * unit_price - (
                    (number_of_groups * THREE_FOR_TWO_PAID_UNITS * unit_price) + quantity_as_int % THREE_FOR_TWO_GROUP_SIZE * unit_price)
        return Discount(product, "3 for 2", -discount_amount)
```

Depois:

```python
class ThreeForTwoStrategy(QuantityOfferStrategy):

    def _group_size(self) -> int:
        return THREE_FOR_TWO_GROUP_SIZE

    def _price_per_group(self, unit_price: float) -> float:
        return THREE_FOR_TWO_PAID_UNITS * unit_price

    def _description(self) -> str:
        return "3 for 2"
```

O "2 por valor" e o "5 por valor" ficaram no mesmo formato. Nenhuma das três tem conta própria:
a conta existe só na classe base, e o D3 está resolvido.

### 7.4 Itens mantidos

Com a conta num lugar só, os defeitos mantidos ficaram fáceis de apontar:

- D12: está inteiro no método `_number_of_groups` da classe `TwoForAmountStrategy`, que conta
  os pares com divisão comum. A correção seria apagar esse método, porque passaria a valer a
  contagem de grupos inteiros da classe base. Um comentário no código registra isso;
- D13: está numa linha da classe base, porque os grupos e a sobra usam as unidades inteiras, e
  o preço sem oferta usa a quantidade completa. A documentação da classe registra isso.

### 7.5 Testes da classe base

Foram acrescentados 8 testes em `tests/test_estrategias_oferta.py`, que mostram o benefício do
padrão:

- as três ofertas por quantidade usam a mesma classe base, e a classe base sozinha não pode ser
  criada;
- uma oferta inventada só para o teste, "4 por 6,00" (`QuatroPorSeis`), foi criada apenas
  preenchendo as três lacunas, sem escrever nenhuma conta. Com 4 unidades a 1,79, o desconto é
  de 1,16, e abaixo de 4 unidades não há desconto. É a prova de que uma promoção nova do mesmo
  tipo não precisa de conta nova nem altera as ofertas existentes (RNF04).

### 7.6 Conferência

- Os 60 testes que já existiam passaram sem nenhuma alteração depois do commit `9f0255c`, e os
  68 passaram depois do commit `60fb453`.
- As classes novas foram comparadas com as da E5 em 8.448 casos, de 0 a 30 unidades, com
  frações e onze preços diferentes, exigindo o mesmo número até a última casa. Não houve
  nenhuma diferença. Essa comparação foi feita com um script à parte, fora do repositório, como
  cuidado extra com o arredondamento (risco R2 do plano).
- A cobertura de `src/` ficou em 100%, com 227 linhas.

## 8. E7: fábrica simples para escolher a oferta

### 8.1 Problema

Depois da E5, as contas tinham saído do carrinho, mas a escolha da classe de cada oferta ainda
era uma sequência de `if` e `elif` dentro do `handle_offers`. Era o que restava do D1: para
criar uma oferta nova, ainda seria preciso mexer no carrinho.

### 8.2 Solução

A escolha passou para a classe `OfferStrategyFactory`, no arquivo novo
`src/offer_strategy_factory.py`. No lugar do `if` e `elif`, ela tem uma tabela, um dicionário
que diz, para cada tipo de oferta, como criar a estratégia a partir do valor cadastrado:

```python
_STRATEGY_BUILDERS = {
    SpecialOfferType.THREE_FOR_TWO: lambda argument: ThreeForTwoStrategy(),
    SpecialOfferType.TEN_PERCENT_DISCOUNT: lambda argument: PercentDiscountStrategy(argument),
    SpecialOfferType.TWO_FOR_AMOUNT: lambda argument: TwoForAmountStrategy(argument),
    SpecialOfferType.FIVE_FOR_AMOUNT: lambda argument: FiveForAmountStrategy(argument),
}
```

Cada `lambda argument: ...` é uma função curta que recebe o valor da oferta e cria a estratégia.
No "leve 3, pague 2", ela ignora o valor, porque essa oferta não usa nenhum. O método
`create(offer)` procura o tipo da oferta na tabela e cria a estratégia. Se o tipo não estiver na
tabela, devolve `None`, e a oferta não dá desconto, como no código original.

Uma oferta nova passa a ser uma linha nova na tabela, sem mexer no carrinho (RNF04).

Esta classe é uma fábrica simples, e é documentada com esse nome. O Factory Method do catálogo
de padrões é outra coisa: uma classe base declara o método de criação e as subclasses decidem
qual objeto criar. Os dois padrões de projeto do trabalho são o Strategy (E5) e o Template
Method (E6). A fábrica completa o Strategy, tirando do carrinho a escolha da estratégia (risco
R11 do plano).

### 8.3 Antes e depois

`handle_offers`, antes:

```python
strategy: IOfferStrategy | None = None
if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
    strategy = ThreeForTwoStrategy()
elif offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
    strategy = PercentDiscountStrategy(offer.argument)
elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
    strategy = TwoForAmountStrategy(offer.argument)
elif offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
    strategy = FiveForAmountStrategy(offer.argument)
```

Depois:

```python
strategy = OfferStrategyFactory.create(offer)
```

Com isso, o D1 está resolvido: o `handle_offers` não tem mais nenhuma decisão por tipo de oferta.

### 8.4 Testes da fábrica

O arquivo `tests/test_fabrica_ofertas.py` tem 8 testes:

- cada tipo de oferta gera a classe certa;
- o valor cadastrado chega à estratégia: uma oferta de 15% gera o texto `15.0% off`, e as de
  "2 por valor" e "5 por valor" geram os textos com o valor cadastrado;
- um tipo de oferta desconhecido devolve `None`.

### 8.5 Conferência

Código e testes foram no mesmo commit (`0b1c7aa`). Sem os testes da fábrica, a linha que
devolve `None` para tipo desconhecido ficaria sem teste, e a cobertura cairia para 99%, o que o
critério das etapas de refatoração não permite. Os 68 testes que já existiam passaram sem
alteração, os 76 passaram no total, e a cobertura de `src/` ficou em 100%, com 230 linhas.
