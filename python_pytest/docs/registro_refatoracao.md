# Registro da refatoração

Projeto: Supermarket Receipt, versão python_pytest.

## 1. Objetivo

Este documento registra as etapas de código concluídas: a refatoração (E3 a E8) e a implementação dos combos (E9). Para cada etapa, são apresentadas as mudanças realizadas, os itens do diagnóstico ou requisitos relacionados, trechos de código de antes e depois e os resultados das verificações de comportamento.

As próximas etapas serão acrescentadas a este registro conforme forem concluídas.

## 2. Como cada etapa é conferida

Antes de cada commit, são realizadas as seguintes verificações:

- `pytest`: todos os testes precisam passar, sem alterações nos testes que já existiam. Eram 41 até a E4 (40 de caracterização e o teste original); passaram a 60 com os testes das ofertas isoladas da E5, a 68 com os testes da classe base da E6, a 76 com os testes da fábrica da E7, a 82 com os testes da calculadora da E8 e a 100 com os testes dos combos da E9;
- `coverage run --source=src -m pytest` e `coverage report -m`: a cobertura de `src/` não pode cair.

Esses critérios correspondem aos critérios de aceitação da seção 6 do plano de contingência. Os testes de caracterização registram o comportamento do código original, inclusive o dos itens mantidos (D5, D8, D10, D12 e D13). Se algum deles falhar, significa que a etapa alterou um comportamento registrado.

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
| E8 | `a123262` | Cálculo dos descontos sai do carrinho para uma classe própria | D4 | 76 passaram | 100% (239 linhas) |
| E8 | `e40c587` | Testes da calculadora de descontos | RNF05 | 82 passaram | 100% (239 linhas) |
| E9 | `89f6a53` | Combos promocionais, com os testes dos combos | RF11 a RF17 | 100 passaram | 100% (271 linhas) |
| Ajuste | `0b70856` | Retirada dos comentários e docstrings do código (seção 12) | nenhum | 100 passaram | 100% (263 linhas) |

O número de linhas muda porque o ReceiptPrinter entrou na cobertura de `src/` na E3, uma variável foi retirada do caixa, as constantes foram acrescentadas, os `import` dos tipos também passaram a contar e a E5 criou o arquivo das ofertas. No ajuste final, a ferramenta deixou de contar os métodos abstratos com corpo `...`. A cobertura permaneceu em 100% em todas as etapas.

## 4. E3: impressão do recibo na pasta `src` (D14)

O ReceiptPrinter monta o texto do recibo e faz parte das funcionalidades do sistema, mas estava na pasta de testes. O arquivo foi movido com `git mv tests\receipt_printer.py src\receipt_printer.py`.

O conteúdo não mudou: o Git registrou a operação como uma renomeação com 100% de semelhança.

A forma de importar continua a mesma, `from receipt_printer import ReceiptPrinter`, porque o `pytest.ini` coloca as pastas `src` e `tests` no caminho de importação. A partir desta etapa, o ReceiptPrinter entra na cobertura de `src/`, com as 44 linhas cobertas pelos testes do recibo impresso.

## 5. E4: nomes, constantes e anotações de tipo (D7, D8 e D9)

A E4 foi dividida em três commits, um para cada item do diagnóstico. Assim, cada mudança pode ser revisada e desfeita separadamente.

### 5.1 Nomes das variáveis internas (D7)

Só mudaram os nomes de variáveis utilizadas dentro dos métodos. Os nomes públicos permaneceram iguais: `handle_offers(receipt, offers, catalog)`, `checks_out_articles_from(the_cart)` e o atributo `ReceiptItem.price`, entre outros (seção 8 do plano).

| Antes | Depois | Arquivo | O que a variável guarda |
|---|---|---|---|
| `p` | `product` | carrinho e caixa | o produto |
| `x` | `group_size` | carrinho | o tamanho do grupo da oferta |
| `number_of_x` | `number_of_groups` | carrinho | quantos grupos completos o cliente levou |
| `total` | `total_with_offer` | carrinho | quanto o cliente paga com a oferta "2 por valor" |
| `discount_n` e `discount_total` | `discount_amount` | carrinho | o valor do desconto, agora com o mesmo nome nas três ofertas por quantidade |
| `pq` | `item` | caixa | um item do carrinho |
| `product_quantities` | retirada | caixa | o laço passa a percorrer `the_cart.items` diretamente. O nome antigo se confundia com a propriedade `product_quantities` do carrinho, que guarda a soma das quantidades por produto |
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

Os números usados nas contas das ofertas viraram constantes com nome, no início de `src/shopping_cart.py`:

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

A condição `quantity_as_int > 2` virou `quantity_as_int >= THREE_FOR_TWO_GROUP_SIZE`. Para números inteiros, "maior que 2" e "maior ou igual a 3" são equivalentes, e `quantity_as_int` é sempre inteiro. A nova forma representa diretamente a regra da oferta: ela vale a partir de um grupo completo.

Cada constante tem exatamente o valor do número que substituiu, e as contas continuam na mesma ordem para evitar diferenças de arredondamento (risco R2 do plano).

Ficaram como estavam, de propósito:

- os textos dos descontos (`"3 for 2"`, `"2 for "` e `"% off"`), que fazem parte do que o recibo mostra (RNF02);
- `group_size = 1`, valor padrão que só evita divisão por zero nas ofertas sem grupo. Ele deixa de existir quando cada oferta ganhar a própria classe (E5);
- o `1.0` de `add_item`, que significa uma unidade e não estava entre os números do D8;
- o nome `TEN_PERCENT_DISCOUNT`, que faz parte do D8, mas foi mantido conforme definido no plano, seção 3.1.

### 5.3 Anotações de tipo (D9)

Todos os parâmetros e retornos de `src/` passaram a declarar o tipo. Exemplo em `src/shopping_cart.py`, antes:

```python
def handle_offers(self, receipt, offers, catalog):
```

Depois:

```python
def handle_offers(self, receipt: Receipt, offers: dict[Product, Offer], catalog: SupermarketCatalog) -> None:
```

A assinatura passa a indicar que `offers` é um dicionário de produto para oferta, informação que antes só era possível identificar lendo o `teller.py`. Outros pontos:

- `-> Product | None` em `product_with_name` indica que o método devolve um produto ou `None`;
- `list[ReceiptItem]` e `dict[Product, float]` indicam o que vai dentro das listas e dos dicionários;
- em `Product`, o tipo `"ProductUnit"` fica entre aspas porque essa classe é definida mais abaixo no mesmo arquivo;
- foram acrescentados os `import` necessários para citar os tipos. Nenhum deles cria dependência circular entre os arquivos.

Além dos testes, a estrutura dos seis arquivos foi comparada antes e depois, desconsiderando as anotações e os `import`, e permaneceu igual: nenhuma conta, mensagem ou nome mudou.

Com os tipos, o D5 fica mais fácil de identificar: o caixa declara que recebe um `SupermarketCatalog`, mas usa `catalog.products`, atributo que essa classe não tem. O D5 é um item mantido e continua como estava.

### 5.4 Itens mantidos

Nenhuma etapa alterou os itens mantidos, conforme definido no plano, seção 3.1. O `catalog.py` recebeu apenas anotações de tipo: a exceção genérica e a mensagem do D10 continuam iguais. Os resultados do D5, do D12 e do D13 continuam os mesmos, conforme os testes de caracterização.

## 6. E5: uma classe para cada oferta (Strategy)

### 6.1 Problema

O método `handle_offers` do carrinho decidia o cálculo de todas as ofertas com uma sequência de `if` e `elif` (D1). Uma mesma oferta aparecia em partes separadas do método (D2), e o valor `argument` da oferta mudava de significado conforme o tipo: percentual, preço do par ou preço do grupo de cinco (D6). Também não era possível testar uma oferta isoladamente.

### 6.2 Padrão aplicado

Strategy: cada forma de calcular o desconto fica numa classe própria, e todas seguem o mesmo contrato, a interface `IOfferStrategy`. Quem utiliza as ofertas não precisa conhecer os detalhes de cada cálculo; basta chamar o método definido pela interface.

O arquivo novo `src/offer_strategies.py` tem a interface e uma classe para cada oferta:

| Classe | Oferta | Valor que recebe |
|---|---|---|
| `IOfferStrategy` | interface com o método `calculate_discount(product, quantity, unit_price)`, que devolve o desconto ou `None` quando a oferta não dá desconto | não se aplica |
| `ThreeForTwoStrategy` | leve 3, pague 2 (RF06) | nenhum |
| `PercentDiscountStrategy` | desconto percentual (RF07) | `percent` |
| `TwoForAmountStrategy` | 2 por um valor (RF08) | `pair_price`, o preço do par |
| `FiveForAmountStrategy` | 5 por um valor (RF09) | `group_price`, o preço do grupo de cinco |

A interface é definida como `class IOfferStrategy(abc.ABC)`, com o método marcado por `@abc.abstractmethod`. As constantes criadas na E4 passaram para esse arquivo, pois pertencem às regras das ofertas. Cada classe recebeu a conta da sua oferta exatamente como estava, mantendo a mesma ordem das operações.

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

O carrinho agora só escolhe a classe da oferta e solicita o desconto a ela. Uma oferta de tipo desconhecido continua sem desconto, como no código original.

### 6.4 O que foi resolvido e o que fica para as próximas etapas

- D2: resolvido. Cada oferta está inteira na sua classe.
- D6: resolvido. Cada classe dá um nome claro ao valor que recebe, e `Offer.argument` continua igual, pois faz parte da interface pública.
- D1: resolvido em parte. As contas saíram do método, mas a escolha da classe ainda usa `if` e `elif`. Essa escolha passa para uma fábrica na E7.
- D3: continua. As três ofertas por quantidade ainda repetem a mesma conta, agora em classes separadas. Isso é tratado com o Template Method na E6.

### 6.5 Itens mantidos

As classes preservam o comportamento dos itens mantidos, conforme definido no plano, seção 3.1:

- `TwoForAmountStrategy` conta os pares com divisão comum, como no original. Um comentário na conta explicava o D12, retirado depois com os demais comentários (seção 12);
- as três ofertas por quantidade contam os grupos com a parte inteira da quantidade e calculam o desconto sobre a quantidade completa, então a fração de peso continua sem cobrança (D13). A documentação de cada classe registra esse comportamento;
- `PercentDiscountStrategy` aplica o percentual cadastrado, qualquer que seja, e o tipo continua se chamando `TEN_PERCENT_DISCOUNT` (D8).

### 6.6 Testes de cada oferta isolada

O arquivo `tests/test_estrategias_oferta.py` tem 19 testes que chamam cada classe diretamente, sem criar Teller, ShoppingCart nem Receipt, conforme o RNF05. Exemplo:

```python
desconto = ThreeForTwoStrategy().calculate_discount(ESCOVA, 3, 0.99)
```

Eles cobrem:

- a interface: as quatro classes seguem `IOfferStrategy`, e a interface sozinha não pode ser criada;
- cada oferta abaixo do mínimo, no limite e acima dele;
- os itens mantidos D8, D12 e D13, com os mesmos valores do código original.

Antes da refatoração, esses testes não eram possíveis porque as contas estavam dentro do método do carrinho (D4 e D11).

### 6.7 Conferência

Os 41 testes que já existiam passaram sem nenhuma alteração depois do commit `09b4a70`, e os 60 passaram depois do commit `e5c23a6`. A cobertura de `src/` ficou em 100%, com 212 linhas, e o arquivo novo das ofertas está totalmente coberto.

## 7. E6: conta comum das ofertas por quantidade (Template Method)

### 7.1 Problema

Depois da E5, cada oferta tinha a sua classe, mas as três ofertas por quantidade ("leve 3, pague 2", "2 por valor" e "5 por valor") ainda repetiam a mesma conta, cada uma com os seus números (D3). Uma correção feita em uma das implementações não seria aplicada automaticamente às outras, e o D12 surgiu justamente de uma diferença entre essas contas.

As três calculam o desconto do mesmo jeito:

> desconto = quantidade × preço − (preço do grupo × número de grupos + unidades que sobram × preço)

Só mudam o tamanho do grupo, o preço do grupo, o texto do desconto e, no "2 por valor", a forma de contar os grupos.

### 7.2 Padrão aplicado

Template Method: a conta fica escrita uma vez, numa classe base, com lacunas que cada oferta preenche. A classe base é `QuantityOfferStrategy`, em `src/offer_strategies.py`. O método `calculate_discount` dela define o roteiro fixo:

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

As lacunas são os métodos implementados por cada oferta:

| Lacuna | Leve 3, pague 2 | 2 por valor | 5 por valor |
|---|---|---|---|
| `_group_size()`: tamanho do grupo | 3 | 2 | 5 |
| `_price_per_group()`: preço de um grupo completo | 2 × preço da unidade | `pair_price` | `group_price` |
| `_description()`: texto no recibo | `3 for 2` | `2 for` e o valor | `5 for` e o valor |
| `_number_of_groups()`: quantos grupos | padrão da classe base | trocado (D12) | padrão da classe base |

As três primeiras lacunas são obrigatórias (`@abc.abstractmethod`). A quarta tem uma implementação padrão na classe base, que conta os grupos inteiros, e só o "2 por valor" substitui essa implementação. O `_` no início dos nomes indica que são métodos internos do roteiro: quem usa as ofertas continua chamando apenas `calculate_discount`. A oferta de percentual não é por quantidade e continua ligada diretamente à interface `IOfferStrategy`.

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

O "2 por valor" e o "5 por valor" ficaram no mesmo formato. Nenhuma das três classes tem uma conta própria: o cálculo existe apenas na classe base, e o D3 está resolvido.

### 7.4 Itens mantidos

Com a conta centralizada, os comportamentos dos itens mantidos ficaram concentrados nos seguintes pontos:

- D12: está no método `_number_of_groups` da classe `TwoForAmountStrategy`, que conta os pares com divisão comum. A correção seria remover esse método, permitindo que a contagem de grupos inteiros da classe base fosse utilizada. Um comentário no código registra esse comportamento;
- D13: está numa linha da classe base, porque os grupos e a sobra usam as unidades inteiras, enquanto o preço sem oferta considera a quantidade completa. A documentação da classe registra esse comportamento.

### 7.5 Testes da classe base

Foram acrescentados 8 testes em `tests/test_estrategias_oferta.py`:

- as três ofertas por quantidade usam a mesma classe base, e a classe base sozinha não pode ser criada;
- uma quarta implementação, chamada `QuatroPorSeis`, representa uma oferta de "4 por 6,00". Ela foi criada implementando apenas as três lacunas, sem escrever uma nova conta. Com 4 unidades a 1,79, o desconto é de 1,16; abaixo de 4 unidades, não há desconto. O teste demonstra que uma nova promoção desse tipo pode utilizar o cálculo existente sem alterar as outras ofertas (RNF04).

### 7.6 Conferência

- Os 60 testes que já existiam passaram sem nenhuma alteração depois do commit `9f0255c`, e os 68 passaram depois do commit `60fb453`.
- As classes novas foram comparadas com as da E5 em 8.448 casos, de 0 a 30 unidades, com frações e onze preços diferentes, exigindo o mesmo resultado até a última casa decimal. Não houve nenhuma diferença. Essa comparação foi feita com um script à parte, fora do repositório, como verificação adicional de arredondamento (risco R2 do plano).
- A cobertura de `src/` ficou em 100%, com 227 linhas.

## 8. E7: fábrica simples para escolher a oferta

### 8.1 Problema

Depois da E5, as contas tinham saído do carrinho, mas a escolha da classe de cada oferta ainda era uma sequência de `if` e `elif` dentro do `handle_offers`. Era o que restava do D1: para criar uma oferta nova, ainda seria necessário alterar o carrinho.

### 8.2 Solução

A escolha passou para a classe `OfferStrategyFactory`, no arquivo novo `src/offer_strategy_factory.py`. No lugar dos `if` e `elif`, ela tem uma tabela, representada por um dicionário que indica como criar a estratégia para cada tipo de oferta:

```python
_STRATEGY_BUILDERS: dict[SpecialOfferType, Callable[[float], IOfferStrategy]] = {
    SpecialOfferType.THREE_FOR_TWO: lambda argument: ThreeForTwoStrategy(),
    SpecialOfferType.TEN_PERCENT_DISCOUNT: lambda argument: PercentDiscountStrategy(argument),
    SpecialOfferType.TWO_FOR_AMOUNT: lambda argument: TwoForAmountStrategy(argument),
    SpecialOfferType.FIVE_FOR_AMOUNT: lambda argument: FiveForAmountStrategy(argument),
}
```

Cada `lambda argument: ...` é uma função curta que recebe o valor da oferta e cria a estratégia. No "leve 3, pague 2", ela ignora o valor, porque essa oferta não utiliza nenhum. O método `create(offer)` procura o tipo da oferta na tabela e cria a estratégia correspondente. Se o tipo não estiver na tabela, devolve `None`, e a oferta não dá desconto, como no código original.

Uma oferta nova passa a exigir apenas uma nova entrada na tabela, sem alteração no carrinho (RNF04).

Esta classe é uma fábrica simples. O Factory Method do catálogo de padrões é diferente: uma classe base declara o método de criação e as subclasses decidem qual objeto criar. Os dois padrões de projeto utilizados no trabalho são Strategy (E5) e Template Method (E6). A fábrica complementa o Strategy, retirando do carrinho a escolha da estratégia (risco R11 do plano).

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

Com isso, o D1 está resolvido: o `handle_offers` não tem mais decisões por tipo de oferta.

### 8.4 Testes da fábrica

O arquivo `tests/test_fabrica_ofertas.py` tem 8 testes:

- cada tipo de oferta gera a classe correta;
- o valor cadastrado chega à estratégia: uma oferta de 15% gera o texto `15.0% off`, e as de "2 por valor" e "5 por valor" geram os textos com o valor cadastrado;
- um tipo de oferta desconhecido devolve `None`.

### 8.5 Conferência

Código e testes foram incluídos no mesmo commit (`0b1c7aa`). Sem os testes da fábrica, a linha que devolve `None` para tipo desconhecido ficaria sem teste, e a cobertura cairia para 99%, abaixo do critério definido para as etapas de refatoração. Os 68 testes que já existiam passaram sem alteração, os 76 passaram no total, e a cobertura de `src/` ficou em 100%, com 230 linhas.

## 9. E8: cálculo dos descontos fora do carrinho

### 9.1 Problema

O ShoppingCart guardava os itens da compra e também calculava os descontos das ofertas (D4). Pelo princípio da Responsabilidade Única, uma classe deve ter um único motivo para mudar. O carrinho tinha dois: mudar a forma de guardar os itens ou mudar o cálculo das promoções.

### 9.2 Solução

O cálculo passou para a classe `DiscountCalculator`, no arquivo novo `src/discount_calculator.py`:

- ela recebe o catálogo pelo construtor, `DiscountCalculator(catalog)`. Isso é injeção de dependência: a calculadora depende do contrato `SupermarketCatalog`, e não de um catálogo específico. Nos testes, recebe o catálogo de teste;
- o método `offer_discounts(product_quantities, offers)` percorre os produtos na ordem em que entraram no carrinho, solicita a estratégia à fábrica, calcula o desconto e devolve a lista de descontos.

O método `handle_offers` do carrinho continua existindo, com o mesmo nome e os mesmos parâmetros, porque faz parte da interface pública (RNF01). Ele apenas repassa o trabalho para a calculadora. O caixa não mudou: continua chamando `the_cart.handle_offers(...)`, como no código original.

### 9.3 Antes e depois

`handle_offers`, antes:

```python
def handle_offers(self, receipt: Receipt, offers: dict[Product, Offer], catalog: SupermarketCatalog) -> None:
    for product in self._product_quantities.keys():
        quantity = self._product_quantities[product]
        if product in offers.keys():
            offer = offers[product]
            unit_price = catalog.unit_price(product)
            strategy = OfferStrategyFactory.create(offer)
            if strategy:
                discount = strategy.calculate_discount(product, quantity, unit_price)
                if discount:
                    receipt.add_discount(discount)
```

Depois:

```python
def handle_offers(self, receipt: Receipt, offers: dict[Product, Offer], catalog: SupermarketCatalog) -> None:
    for discount in DiscountCalculator(catalog).offer_discounts(self._product_quantities, offers):
        receipt.add_discount(discount)
```

O carrinho agora fica responsável por guardar os itens, enquanto a calculadora realiza os cálculos. O D4 está resolvido.

### 9.4 Testes da calculadora

O arquivo `tests/test_calculadora_descontos.py` tem 6 testes, que usam apenas o catálogo de teste e dicionários, sem criar Teller, ShoppingCart nem Receipt:

- os descontos saem na ordem dos produtos;
- não geram desconto: compra sem ofertas, oferta que não atinge o mínimo, oferta de produto que não está na compra e oferta de tipo desconhecido;
- a calculadora utiliza o preço do catálogo.

### 9.5 Conferência

Os 76 testes que já existiam passaram sem nenhuma alteração depois do commit `a123262`, e os 82 passaram depois do commit `e40c587`. A cobertura de `src/` ficou em 100%, com 239 linhas.

## 10. Situação ao fim da refatoração

### 10.1 Itens do diagnóstico

| Item | Situação | Etapa |
|---|---|---|
| D1. Um método decide todas as ofertas com condicionais | Resolvido: Strategy e fábrica simples | E5 e E7 |
| D2. Mesma oferta espalhada no método | Resolvido: uma classe por oferta | E5 |
| D3. Fórmulas duplicadas | Resolvido: Template Method | E6 |
| D4. Carrinho guarda itens e calcula promoções | Resolvido: `DiscountCalculator` | E8 |
| D5. Caixa depende de atributo do catálogo de teste | Mantido (plano, seção 3.1) | |
| D6. `argument` com vários significados | Resolvido: cada estratégia dá nome ao valor | E5 |
| D7. Nomes que não explicam | Resolvido | E4 |
| D8. Números mágicos e nome TEN_PERCENT_DISCOUNT | Números resolvidos; nome mantido (plano, seção 3.1) | E4 |
| D9. Sem anotações de tipo | Resolvido | E4 |
| D10. Exceção genérica | Mantido (plano, seção 3.1) | |
| D11. Quase nenhum teste | Resolvido: de 1 para 82 testes, cobertura de 71% para 100% | E1, E5 a E8 |
| D12. "2 por valor" cobra a mais | Mantido, isolado num método (plano, seção 3.1) | |
| D13. Fração de peso não cobrada | Mantido, isolado numa linha da classe base (plano, seção 3.1) | |
| D14. Impressão do recibo na pasta de testes | Resolvido | E3 |

### 10.2 Responsabilidade de cada arquivo de `src/`

| Arquivo | Responsabilidade |
|---|---|
| `model_objects.py` | dados do sistema: produto, quantidade, unidade, tipo de oferta, oferta e desconto |
| `catalog.py` | contrato do catálogo de preços |
| `shopping_cart.py` | guardar os itens da compra; `handle_offers` repassa o cálculo para a calculadora |
| `teller.py` | caixa: cadastrar ofertas e fechar a compra |
| `receipt.py` | recibo: itens, descontos e total |
| `receipt_printer.py` | texto do recibo impresso |
| `offer_strategies.py` | regras de desconto de cada oferta (Strategy e Template Method) |
| `offer_strategy_factory.py` | escolher a regra de desconto pelo tipo da oferta (fábrica simples) |
| `discount_calculator.py` | calcular os descontos das ofertas de uma compra |

### 10.3 Princípios SOLID aplicados

| Princípio | Onde aparece |
|---|---|
| Responsabilidade Única | o carrinho só guarda itens, a calculadora calcula, e cada estratégia cuida de uma oferta |
| Aberto/Fechado | uma oferta nova pode ser implementada sem alterar o carrinho nem as estratégias existentes, exigindo apenas uma nova entrada na tabela da fábrica. Os testes da E6 demonstram a reutilização do cálculo com a implementação `QuatroPorSeis` |
| Inversão de Dependência | a calculadora recebe o catálogo pelo construtor e depende do contrato `SupermarketCatalog`. Nos testes, recebe o catálogo de teste |

## 11. E9: combos promocionais

### 11.1 Regras implementadas

O requisito 3.2 do enunciado define um desconto de 10% sobre os produtos de cada combo completo. As regras correspondentes estão registradas nos requisitos:

| Requisito | Regra |
|---|---|
| RF11 | os descontos de combo vêm depois dos descontos das ofertas |
| RF12 | o combo precisa de dois ou mais produtos diferentes; caso contrário, o cadastro é recusado com erro |
| RF13 | 10% sobre uma unidade de cada produto do combo, com uma linha `bundle 10% off` por produto |
| RF14 | o número de combos é a menor quantidade entre os produtos do combo; o que sobra paga preço normal |
| RF15 | produto vendido por peso: só os quilos inteiros entram no combo |
| RF16 | produto com oferta própria cadastrada não entra em combo |
| RF17 | combos com produto em comum: cada unidade entra em apenas um combo, na ordem de cadastro dos combos |

### 11.2 Implementação

- `Bundle`, em `src/model_objects.py`: representa o combo. Guarda os produtos e recusa o cadastro com menos de dois produtos ou com produto repetido (`ValueError`), conforme o RF12.
- `Teller`, em `src/teller.py`: o método novo `add_bundle_offer(products)` cadastra um combo, e a lista `bundles` guarda os combos na ordem de cadastro. Ao fechar a compra, depois dos descontos das ofertas, o caixa solicita os descontos de combo à calculadora de combos e os acrescenta ao recibo. Por isso, eles aparecem por último (RF11).
- `BundleCalculator`, no arquivo novo `src/bundle_calculator.py`: calcula os descontos dos combos. Ela recebe o catálogo pelo construtor, assim como a calculadora das ofertas.

O cálculo segue estes passos:

1. separa as unidades que podem entrar em combo: só as unidades inteiras (RF15) e só de produtos sem oferta própria (RF16);
2. percorre os combos na ordem de cadastro. Para cada combo, o número de combos formados é a menor quantidade disponível entre os seus produtos (RF14);
3. consome essas unidades, para que não sejam utilizadas em outro combo (RF17);
4. cria uma linha `bundle 10% off` por produto do combo, com 10% do preço das unidades que entraram (RF13).

Exemplo do RF17, com o combo A (escova e creme dental) cadastrado antes do combo B (escova e fio dental), e 2 escovas, 1 creme dental e 1 fio dental no carrinho:

| Combo | Disponível antes | Combos formados | Disponível depois |
|---|---|---|---|
| A | escova 2, creme dental 1 | 1 | escova 1, creme dental 0 |
| B | escova 1, fio dental 1 | 1 | escova 0, fio dental 0 |

O recibo recebe quatro linhas de desconto: escova -1,00 e creme dental -1,50 do combo A, escova -1,00 e fio dental -0,50 do combo B. O total é 36,00, conforme o requisito.

### 11.3 Nenhuma alteração nas ofertas existentes

O commit `89f6a53` alterou apenas `src/model_objects.py` (classe nova `Bundle`) e `src/teller.py` (cadastro do combo e soma dos descontos de combo), além de criar `src/bundle_calculator.py` e `tests/test_combos.py`. Os arquivos das ofertas (`offer_strategies.py`, `offer_strategy_factory.py`, `discount_calculator.py` e `shopping_cart.py`) não foram modificados.

Isso atende ao RNF04: a nova promoção foi implementada sem alterar o código das ofertas existentes.

Sem combo cadastrado, o caixa não gera nenhum desconto de combo, e o recibo fica idêntico ao de antes (RNF02). Os 82 testes que já existiam, incluindo os de caracterização, passaram sem nenhuma alteração.

### 11.4 Testes dos combos

O arquivo `tests/test_combos.py` tem 18 testes. Os preços da escova e do creme dental são 10,00 e 15,00, respectivamente. O fio dental a 5,00 e a maçã a 2,00 o quilo completam os casos de produto em comum e de produto por peso.

| Grupo | Casos |
|---|---|
| Seção 6 dos requisitos | combo completo (22,50), combo incompleto (10,00), combo repetido (45,00) e produto excedente (32,50) |
| Cadastro (RF12) | aceita dois produtos diferentes; recusa lista vazia, um produto só e produto repetido |
| Peso (RF15) | 1,5 kg de maçã e 1 escova formam um combo sobre 1 kg (11,80); 0,5 kg não forma combo (11,00) |
| Convivência com ofertas (RF16) | 3 escovas com "leve 3, pague 2" e 1 creme dental: só a oferta vale (35,00); 1 escova com "leve 3, pague 2" e 1 creme dental: nenhum desconto (25,00) |
| Produto em comum (RF17) | com uma escova, só o combo cadastrado primeiro se forma (27,50); com duas escovas, os dois combos se formam (36,00) |
| Ordem e recibo (RF11 e RNF02) | desconto de combo depois do desconto de oferta; sem combo cadastrado, nenhum desconto de combo; recibo impresso com as linhas do combo |
| Regra isolada (RNF05) | a calculadora de combos chamada diretamente, sem caixa, carrinho nem recibo |

### 11.5 Conferência

Código e testes foram incluídos no mesmo commit (`89f6a53`). Os 82 testes que já existiam passaram sem alteração, os 100 passaram no total, e a cobertura de `src/` ficou em 100%, com 271 linhas.

## 12. Retirada dos comentários e docstrings

Commit: `0b70856`.

Os comentários e as docstrings acrescentados durante a modernização foram retirados do código. O código original não tinha comentários nem docstrings, e os nomes das classes, dos métodos e das constantes indicam o papel de cada parte. As explicações sobre requisitos, defeitos mantidos e padrões continuam nos documentos da pasta `docs/`.

O que mudou:

- em `src/`, as docstrings das classes e dos métodos e os comentários de `bundle_calculator.py` e `offer_strategies.py`;
- nos testes novos (`test_estrategias_oferta.py`, `test_fabrica_ofertas.py`, `test_calculadora_descontos.py` e `test_combos.py`), as docstrings e os comentários que separavam os grupos de testes;
- os quatro métodos abstratos, que tinham só a docstring como corpo, passaram a ter `...` na mesma linha da assinatura.

O arquivo `tests/test_comportamento_legado.py` não foi alterado. Ele é o mesmo arquivo que rodou sobre o código original (`docs/evidencias/antes/03_caracterizacao_pytest.txt`), e o RNF02 exige que os testes de caracterização continuem passando sem nenhuma alteração.

Conferência:

- a árvore sintática de cada arquivo, desconsiderando as docstrings e os corpos `...`, ficou idêntica à anterior, o que mostra que nenhuma instrução mudou;
- os 100 testes passaram e a cobertura de `src/` continuou em 100%;
- o total de instruções contadas pela cobertura passou de 271 para 263, porque a ferramenta deixa de contar, por padrão, os métodos cujo corpo é só `...` (os 4 métodos abstratos, com o decorador e a assinatura);
- o Bandit passou a analisar 292 linhas em vez de 319, porque as linhas das docstrings contavam como código, e continuou sem alertas;
- as evidências `depois/01_pytest.txt`, `depois/02_cobertura.txt` e `depois/05_bandit.txt` foram geradas novamente sobre este commit. O pip-audit e o Safety analisam as bibliotecas, que não mudaram, e por isso as evidências 06 e 07 foram mantidas.
