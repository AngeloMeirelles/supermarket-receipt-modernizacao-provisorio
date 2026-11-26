# Diagnóstico técnico do código legado

Projeto: Supermarket Receipt, versão python_pytest.

## 1. Como a análise foi feita

O código de `src/` e de `tests/` foi lido arquivo por arquivo, seguindo o caminho de uma
compra do carrinho até o recibo. Depois, os testes foram executados e a cobertura foi
medida. As saídas estão em `docs/evidencias/antes/`.

Os números de linha citados são do código original. Para ver um arquivo como era:
`git show c72d68a:python_pytest/src/shopping_cart.py`.

## 2. Como o sistema funciona

| Arquivo | Classes | Papel |
|---|---|---|
| `model_objects.py` | Product, ProductQuantity, ProductUnit, SpecialOfferType, Offer, Discount | dados do sistema: produto, quantidade, tipo de oferta, oferta e desconto |
| `catalog.py` | SupermarketCatalog | catálogo de preços; a versão real acessaria um banco de dados e só lança erro |
| `shopping_cart.py` | ShoppingCart | guarda os itens do carrinho e calcula os descontos das ofertas |
| `teller.py` | Teller | caixa: cadastra ofertas e fecha a compra |
| `receipt.py` | Receipt, ReceiptItem | recibo: itens, descontos e total |

Caminho de uma compra:

1. `Teller.checks_out_articles_from` cria o recibo e adiciona cada item do carrinho com o
   preço do catálogo.
2. Em seguida chama `ShoppingCart.handle_offers`, passando o recibo, as ofertas cadastradas
   e o catálogo.
3. `handle_offers` percorre os produtos do carrinho, calcula o desconto de cada um que tem
   oferta e o adiciona ao recibo.
4. O total do recibo é a soma dos itens mais a soma dos descontos, que são valores negativos.

Ofertas existentes: leve 3 e pague 2 (THREE_FOR_TWO), desconto percentual
(TEN_PERCENT_DISCOUNT), 2 unidades por um valor (TWO_FOR_AMOUNT) e 5 unidades por um valor
(FIVE_FOR_AMOUNT).

Nos testes, o catálogo real é substituído pelo FakeCatalog (`tests/fake_catalog.py`), que
guarda produtos e preços em memória.

## 3. Problemas encontrados

### 3.1 Excesso de condicionais e método longo

#### D1. Um único método decide o cálculo de todas as ofertas

Onde: `src/shopping_cart.py`, método `handle_offers`, linhas 30 a 68.

O método tem 39 linhas e testa o tipo da oferta nas linhas 39, 42, 49, 53, 58 e 62:

```python
if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
    x = 3

elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
    ...

if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
    x = 5
```

É o mesmo formato do exemplo "antes" do princípio Aberto/Fechado visto em aula (Aula05,
p. 3), em que uma classe `Desconto` decide o cálculo com `if tipo == ... elif ...`.

Efeitos. Evolução: qualquer oferta nova, incluindo os combos pedidos, obriga a editar este
método. Manutenção: ao mexer em uma oferta é fácil afetar outra, porque todas usam as mesmas
variáveis. Testabilidade: não dá para testar uma oferta isoladamente.

#### D2. A mesma oferta está espalhada em pontos diferentes do método

Onde: `src/shopping_cart.py`. Leve 3, pague 2: linhas 39-40 e 53-56. 5 por valor: linhas
49-50 e 62-65. 2 por valor: linhas 42-47, num caminho próprio.

O método primeiro define o tamanho do grupo (`x`), depois conta os grupos (linha 52) e só
então calcula o desconto. Por isso a mesma oferta aparece duas vezes. O "2 por valor" é a
exceção: calcula tudo antes da linha 52. Há ainda `elif` na linha 42 e `if` na linha 49 para
o mesmo tipo de decisão.

Efeitos. Manutenção: para entender ou alterar uma oferta é preciso localizar todos os seus
pedaços.

### 3.2 Duplicação

#### D3. Três fórmulas quase iguais para as ofertas por quantidade

Onde: `src/shopping_cart.py`, linhas 45-46, 54-55 e 63-64.

As três calculam "preço sem oferta menos (grupos completos × preço do grupo + unidades
avulsas × preço unitário)", cada uma com seus próprios números:

```python
# linha 45 (2 por valor)
total = offer.argument * (quantity_as_int / x) + quantity_as_int % 2 * unit_price

# linhas 54-55 (leve 3, pague 2)
discount_amount = quantity * unit_price - (
            (number_of_x * 2 * unit_price) + quantity_as_int % 3 * unit_price)

# linhas 63-64 (5 por valor)
discount_total = unit_price * quantity - (
            offer.argument * number_of_x + quantity_as_int % 5 * unit_price)
```

Efeitos. Manutenção: uma correção feita em uma cópia não vale para as outras. O defeito D12
é justamente uma das três cópias estar diferente das demais.

### 3.3 Responsabilidades misturadas e baixa coesão

#### D4. O carrinho guarda os itens e também calcula as promoções

Onde: `src/shopping_cart.py`. Guardar itens: linhas 8 a 28. Calcular descontos: linhas 30
a 68.

Pelo princípio da Responsabilidade Única, uma classe deve ter "uma única razão para mudar"
(Aula04, p. 4). O ShoppingCart tem duas: mudar a forma de guardar os itens ou mudar qualquer
regra de promoção. Os métodos que guardam itens e o cálculo de descontos não têm relação
entre si.

Efeitos. Evolução: as regras de promoção crescem dentro de uma classe que deveria só
representar o carrinho. Testabilidade: para testar um desconto é preciso passar pelo
carrinho, pelo caixa e pelo recibo.

### 3.4 Acoplamento

#### D5. O caixa depende de um atributo que só existe no catálogo de teste

Onde: `src/teller.py`, linhas 28-29.

```python
def product_with_name(self, name):
    return self.catalog.products.get(name, None)
```

O atributo `products` só é criado no FakeCatalog (`tests/fake_catalog.py`, linhas 6 e 10). O
SupermarketCatalog, que é o contrato do catálogo, não o tem. Com o catálogo real, o método
falha com `AttributeError: 'SupermarketCatalog' object has no attribute 'products'`. Além
disso, nenhum código ou teste chama este método. Por fazer parte da interface pública do
Teller, ele não pode simplesmente ser removido.

O princípio da Inversão de Dependência diz que o código deve depender da abstração, do
contrato, e não de uma implementação específica (Aula06, p. 13-14).

Efeitos. Evolução: trocar o FakeCatalog pelo catálogo real quebra o método. Manutenção: o
método parece funcionar porque só é usado com o catálogo falso.

#### D6. O valor `argument` da oferta muda de significado conforme o tipo

Onde: `src/shopping_cart.py`, linhas 45, 47, 59-60, 64 e 65.

No desconto percentual, `argument` é o percentual (10.0). No "2 por valor", é o preço do par.
No "5 por valor", é o preço das cinco unidades. No "leve 3, pague 2", não é usado.

Efeitos. Manutenção: nada no código indica o que deve ser informado em cada caso, e um valor
errado no cadastro passa sem aviso.

### 3.5 Code smells de legibilidade

#### D7. Nomes que não explicam o conteúdo

Onde:

- `src/shopping_cart.py`: `p` (linha 31), `x` (38), `discount_n` (46), `number_of_x` (52).
- `src/teller.py`: `product_quantities` recebe `the_cart.items` (16), embora o carrinho tenha
  outro dado com esse mesmo nome; `pq` (17); `p` (18); `price` guarda o total da linha (21),
  enquanto em `ReceiptItem` (`src/receipt.py`, linhas 3 a 6) `price` é o preço unitário.

Efeitos. Manutenção: a leitura fica lenta e é fácil confundir um valor com outro.

#### D8. Números mágicos

Onde: `src/shopping_cart.py`: 3 (linhas 40 e 55), 2 (43, 44, 45, 53 e 55), 5 (50, 62 e 64)
e 100.0 (60).

Além disso, `SpecialOfferType.TEN_PERCENT_DISCOUNT` (`src/model_objects.py`, linha 23) aceita
qualquer percentual, não só 10%. O nome faz parte da interface pública.

Efeitos. Manutenção: as regras de negócio ficam escondidas em números soltos, sem um nome que
diga o que representam.

#### D9. Nenhuma anotação de tipo

Onde: todos os arquivos de `src/`.

Nenhum parâmetro ou retorno indica o tipo esperado. Em `handle_offers(self, receipt, offers,
catalog)` (`src/shopping_cart.py`, linha 30), por exemplo, só lendo o `teller.py` se descobre
que `offers` é um dicionário de produto para oferta. Nas aulas, a falta de tipagem estática
aparece como um dos problemas de qualidade (Aula03, análise estática, p. 7), e os type hints
como forma de ajudar "na leitura do código" e "na detecção de erros antes de executar"
(p. 19).

Efeitos. Manutenção: erros de tipo só aparecem durante a execução.

#### D10. Exceção genérica com mensagem repetida

Onde: `src/catalog.py`, linhas 5 e 8.

Os dois métodos lançam `Exception` com o mesmo texto. Quem chama não tem como diferenciar esse
erro de outros. É um ponto de menor impacto.

### 3.6 Baixa testabilidade

#### D11. Quase nenhum teste, e o existente não verifica desconto

Onde: `tests/test_supermarket.py`. Evidências: `docs/evidencias/antes/01_pytest.txt` e
`02_cobertura.txt`.

O projeto tem um único teste, `test_ten_percent_discount`. Ele cadastra 10% de desconto para
a escova, mas coloca só maçãs no carrinho, então nenhum desconto é calculado. A comparação do
total usa `pytest.approx(..., 0.01)`, que aceita 1% de diferença: um total de 5,02 também
passaria no lugar de 4,975.

A cobertura total é de 71%. No `shopping_cart.py` é de 41%: as linhas 34 a 68, com todos os
cálculos de oferta, não são executadas por nenhum teste.

Também não é possível testar uma fórmula de oferta sozinha, porque ela está dentro do
`handle_offers` (D1, D4). É preciso montar catálogo, caixa, carrinho e recibo. Nas aulas, o
teste unitário é o que testa "as menores unidades de software desenvolvidas" (Aula03, testes,
p. 8).

Efeitos. Testabilidade e manutenção: hoje nada avisa se uma mudança alterar um valor do
recibo. Os testes são o "cinto de segurança" do código (Aula03, testes, p. 6), e aqui ele
praticamente não existe.

### 3.7 Defeitos de comportamento

Os dois itens abaixo foram encontrados na leitura do código e ficam aqui só registrados. O
tratamento de cada um, manter ou corrigir com justificativa, é definido no plano de
contingência.

#### D12. Na oferta "2 por valor", quantidade ímpar é cobrada a mais

Onde: `src/shopping_cart.py`, linha 45.

```python
total = offer.argument * (quantity_as_int / x) + quantity_as_int % 2 * unit_price
```

A divisão `quantity_as_int / x` tem casas decimais: com 3 unidades, dá 1,5 par. A unidade que
sobra é cobrada duas vezes: meio par no preço da oferta e mais uma unidade no preço normal.

Exemplo com tomate-cereja a 0,69 e a oferta "2 por 0,99":

| Quantidade | Sem oferta | O código cobra | Cobrança certa |
|---|---|---|---|
| 2 | 1,38 | 0,99 | 0,99 |
| 3 | 2,07 | 2,175 | 1,68 |
| 4 | 2,76 | 1,98 | 1,98 |
| 5 | 3,45 | 3,165 | 2,67 |

A cobrança certa é cada par pelo valor da oferta e a unidade que sobra pelo preço normal. Com
quantidade ímpar, o código cobra 0,495 a mais do que o certo, que é metade do valor de um par.
Com 3 unidades, o total passa até do preço sem oferta: o "desconto" fica positivo e aumenta o
total.

#### D13. Fração de produto vendido por peso não é cobrada nas ofertas por quantidade

Onde: `src/shopping_cart.py`, linhas 36, 45-46, 54-55 e 63-64.

As ofertas contam os grupos usando só a parte inteira da quantidade (`int(quantity)`, linha
36), mas o "preço sem oferta" usa a quantidade completa. A fração entra no desconto e sai de
graça.

Exemplo: maçã a 1,99 o quilo com a oferta "leve 3, pague 2". 3,5 kg custam 3,98, o mesmo que
2 kg sem oferta.

### 3.8 Organização

#### D14. A impressão do recibo está junto dos testes

Onde: `tests/receipt_printer.py`.

A classe ReceiptPrinter monta o texto do recibo impresso, que é uma função do sistema, mas
está na pasta de testes e não é usada por nenhum teste. Fica registrada como observação.

## 4. Resumo

| # | Problema | Onde | Categoria |
|---|---|---|---|
| D1 | Um método decide todas as ofertas com condicionais | `shopping_cart.py`, 30-68 | condicionais, método longo |
| D2 | Mesma oferta espalhada no método | `shopping_cart.py`, 39-65 | condicionais |
| D3 | Fórmulas duplicadas | `shopping_cart.py`, 45-46, 54-55, 63-64 | duplicação |
| D4 | Carrinho guarda itens e calcula promoções | `shopping_cart.py`, 8-68 | responsabilidades misturadas |
| D5 | Caixa depende de atributo do catálogo de teste | `teller.py`, 28-29 | acoplamento |
| D6 | `argument` com vários significados | `shopping_cart.py`, 45-65 | acoplamento |
| D7 | Nomes que não explicam | `shopping_cart.py`, `teller.py`, `receipt.py` | code smell |
| D8 | Números mágicos | `shopping_cart.py`, 40-64; `model_objects.py`, 23 | code smell |
| D9 | Sem anotações de tipo | `src/` | code smell |
| D10 | Exceção genérica | `catalog.py`, 5 e 8 | code smell |
| D11 | Um teste, 71% de cobertura, ofertas sem teste | `tests/test_supermarket.py` | testabilidade |
| D12 | "2 por valor" cobra a mais com quantidade ímpar | `shopping_cart.py`, 45 | defeito |
| D13 | Fração de peso não cobrada | `shopping_cart.py`, 36, 45-46, 54-55, 63-64 | defeito |
| D14 | Impressão do recibo na pasta de testes | `tests/receipt_printer.py` | organização |

Os itens D1 a D4 estão concentrados no `handle_offers` e são o principal alvo da refatoração.
O tratamento de cada item é definido no plano de contingência.
