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

- `pytest`: os 41 testes (40 de caracterização e o teste original) precisam passar, sem
  nenhuma alteração nos testes;
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

O número de linhas muda porque o ReceiptPrinter entrou na conta na E3, uma variável foi
retirada do caixa, as constantes foram acrescentadas e os `import` dos tipos também contam. A
cobertura ficou em 100% em todas as etapas.

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
