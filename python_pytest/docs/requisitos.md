# Requisitos

Projeto: Supermarket Receipt, versão python_pytest.
Base: commit c72d68a do repositório original e o diagnóstico em `docs/diagnostico_tecnico.md`.
Data: 24/11/2026.

## 1. Escopo

Este documento descreve:

- o comportamento atual do sistema que deve ser preservado: carrinho, recibo e as quatro
  ofertas existentes;
- duas correções de defeitos encontrados no diagnóstico (D12 e D13);
- a nova promoção de combos.

Os preços usados nos critérios de aceitação são exemplos para os testes. Nos combos foram
usados os valores do enunciado: escova a 10,00 e creme dental a 15,00.

## 2. Termos usados

| Termo | Significado |
|---|---|
| Oferta | promoção cadastrada no caixa para um produto. Cada produto tem no máximo uma |
| Desconto | linha do recibo com produto, descrição e valor negativo |
| Combo | conjunto de produtos diferentes cadastrado no caixa. Quem leva uma unidade de cada ganha 10% sobre essas unidades |
| Unidade inteira | parte inteira da quantidade. Em 3,5 kg, são 3 unidades inteiras e uma fração de 0,5 kg |

## 3. Requisitos funcionais

### 3.1 Carrinho e recibo

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF01 | O carrinho aceita produtos por unidade ou por quantidade, inclusive peso. O mesmo produto pode ser adicionado mais de uma vez | Escova adicionada com quantidade 2 e depois mais 1: o recibo mostra 2 linhas e as ofertas são calculadas sobre o total de 3 |
| RF02 | Cada item do recibo tem produto, quantidade, preço unitário e total da linha (quantidade × preço), na ordem em que entrou no carrinho | 2,5 kg de maçã a 1,99: quantidade 2,5, preço 1,99, total 4,975 |
| RF03 | O total do recibo é a soma dos itens mais a soma dos descontos, que são negativos | Escova a 0,99 e 2,5 kg de maçã a 1,99, sem oferta: total 5,965 |
| RF04 | Oferta de um produto que não está no carrinho não gera desconto | 10% cadastrado na escova e carrinho só com maçãs: nenhum desconto |
| RF05 | Cada produto tem uma única oferta. Cadastrar outra para o mesmo produto substitui a anterior | 10% e depois "leve 3, pague 2" na escova: vale só o "leve 3, pague 2" |

### 3.2 Ofertas existentes

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF06 | Leve 3, pague 2: a cada 3 unidades o cliente paga 2. As unidades que sobram pagam preço normal. Texto do desconto: `3 for 2` | Escova a 0,99: com 2 unidades, sem desconto; com 3, desconto de -0,99 e total 1,98; com 7, desconto de -1,98 e total 4,95 |
| RF07 | Desconto percentual: quantidade × preço × percentual / 100, inclusive sobre frações. Texto: o percentual seguido de `% off`, por exemplo `10.0% off`. Apesar do nome TEN_PERCENT_DISCOUNT, aceita qualquer percentual | 2 pacotes de arroz a 2,49 com 10%: desconto de -0,498 |
| RF08 | 2 por um valor: cada par paga o valor cadastrado na oferta. A unidade que sobra paga preço normal. Texto: `2 for` seguido do valor, por exemplo `2 for 0.99` | Tomate a 0,69 com "2 por 0,99": 1 unidade, 0,69; 2 unidades, 0,99; 3 unidades, 1,68; 4 unidades, 1,98. O código original cobrava 2,175 por 3 unidades (D12) |
| RF09 | 5 por um valor: cada grupo de 5 unidades paga o valor cadastrado. As que sobram pagam preço normal. Texto: `5 for` seguido do valor, por exemplo `5 for 7.49` | Creme dental a 1,79 com "5 por 7,49": 4 unidades, sem desconto; 5 unidades, 7,49; 6 unidades, 9,28 |
| RF10 | Nas ofertas por quantidade (RF06, RF08 e RF09), só unidades inteiras formam grupos. A fração de um produto vendido por peso paga preço normal | 3,5 kg de maçã a 1,99 com "leve 3, pague 2": total 4,975 (3 kg pela oferta, pagando 2, e 0,5 kg a preço normal). O código original cobrava 3,98 (D13) |
| RF11 | No recibo, os descontos das ofertas vêm na ordem em que os produtos entraram no carrinho. Os descontos de combo vêm depois | Arroz com 10% adicionado antes da escova com "leve 3, pague 2": o desconto do arroz aparece primeiro |

### 3.3 Combos

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF12 | O caixa cadastra um combo informando os produtos que o compõem. O combo precisa de 2 ou mais produtos diferentes. Se não tiver, o cadastro é recusado com erro | [escova, creme dental] é aceito. [escova] e [escova, escova] são recusados |
| RF13 | Combo completo: 10% de desconto sobre uma unidade de cada produto do combo, com uma linha de desconto por produto e o texto `bundle 10% off` | 1 escova e 1 creme dental: descontos de -1,00 e -1,50, total 22,50 |
| RF14 | Combos repetidos, excedentes e incompletos: o número de combos é a menor quantidade entre os produtos do combo. O que sobra paga preço normal | 2 escovas e 1 creme dental: 1 combo, total 32,50. 2 escovas e 2 cremes dentais: 2 combos, total 45,00. Só 1 escova: sem desconto, total 10,00 |
| RF15 | Produto vendido por peso em combo: só unidades inteiras entram no combo. A fração paga preço normal | Combo [maçã a 2,00 o quilo, escova]: 1,5 kg de maçã e 1 escova formam 1 combo com desconto sobre 1 kg, total 11,80. 0,5 kg de maçã e 1 escova não formam combo |
| RF16 | Convivência com outras ofertas: produto com oferta própria cadastrada não entra em combo, mesmo quando a quantidade não é suficiente para a oferta dar desconto | Escova com "leve 3, pague 2" e combo [escova, creme dental]. 1 escova e 1 creme dental: nenhum desconto, total 25,00. 3 escovas e 1 creme dental: só o desconto `3 for 2`, total 35,00 |
| RF17 | Combos que usam o mesmo produto: cada unidade entra em um único combo, seguindo a ordem em que os combos foram cadastrados | Combos [escova, creme dental] e [escova, fio dental a 5,00], nessa ordem. 1 escova, 1 creme dental e 1 fio dental: só o primeiro combo, total 27,50. 2 escovas, 1 creme dental e 1 fio dental: os dois combos, total 36,00 |

## 4. Decisões sobre os combos

O enunciado pede que a documentação explique o tratamento de múltiplos combos e a convivência
com outras ofertas. As decisões foram estas:

- **Composição (RF12 e RF13):** um combo é formado por uma unidade de cada produto, com pelo
  menos dois produtos diferentes. É o que a tabela do enunciado mostra.
- **Múltiplos combos do mesmo tipo (RF14):** valem tantos combos quanto a quantidade do
  produto mais escasso. O excedente paga preço normal.
- **Convivência com outras ofertas (RF16):** produto com oferta própria não participa de
  combos. Assim nenhum recibo que já tinha oferta muda de valor, e não existe a possibilidade
  de dois descontos sobre o mesmo item. A regra depende só do cadastro, o que a torna simples
  de prever e de testar.
- **Combos diferentes com produto em comum (RF17):** cada unidade entra em um combo só, na
  ordem de cadastro, para não haver desconto duplicado.
- **Produtos por peso (RF15):** só unidades inteiras, a mesma regra adotada para as ofertas
  por quantidade no RF10.
- **Recibo (RF11 e RF13):** uma linha de desconto por produto do combo. A classe Discount liga
  cada desconto a um produto, então não é preciso mudar a estrutura do recibo. Os descontos de
  combo vêm depois dos demais, e um recibo sem combo fica igual ao do código original.

Consequência do RF17: se dois combos usam a escova e o cliente leva 2 escovas, aparecem duas
linhas de desconto da escova, uma por combo. Cada unidade recebe um único desconto.

## 5. Requisitos não funcionais

| # | Requisito | Critério de aceitação |
|---|---|---|
| RNF01 | As interfaces públicas são preservadas: classes e métodos públicos mantêm nome, parâmetros e retorno (lista na seção 5.1). Mudanças internas são permitidas quando justificadas | O teste original `tests/test_supermarket.py` passa sem nenhuma alteração |
| RNF02 | Os valores e textos do recibo são preservados, exceto as correções do RF08 e do RF10, que são justificadas e feitas em commit separado | Os testes de caracterização escritos sobre o código original continuam passando, inclusive o texto impresso pelo ReceiptPrinter. Um recibo sem combo fica idêntico ao do código original |
| RNF03 | Testes automatizados com pytest, executados com o comando `pytest` na pasta `python_pytest` | Todos os testes passam. Cada RF tem pelo menos um teste. A cobertura é medida antes e depois |
| RNF04 | Uma promoção nova pode ser incluída sem alterar o código das ofertas existentes | A implementação dos combos não modifica as regras das ofertas existentes, o que pode ser conferido no diff do commit |
| RNF05 | Cada regra de desconto pode ser testada sozinha, sem montar caixa, carrinho e recibo | Existe pelo menos um teste de cada oferta isolada |
| RNF06 | Bandit, pip-audit e Safety são executados antes e depois da modernização, com triagem dos alertas | Relatórios em `docs/evidencias/antes/` e `docs/evidencias/depois/`, com todos os alertas analisados |
| RNF07 | Nenhuma dependência nova é adicionada ao projeto | `requirements.txt` igual ao original |

### 5.1 Interfaces públicas que devem ser mantidas (RNF01)

| Classe | O que é mantido |
|---|---|
| Teller | `Teller(catalog)`, `add_special_offer(offer_type, product, argument)`, `checks_out_articles_from(the_cart)` devolvendo um Receipt, `product_with_name(name)`, atributos `catalog` e `offers` |
| ShoppingCart | `ShoppingCart()`, propriedades `items` e `product_quantities`, `add_item(product)`, `add_item_quantity(product, quantity)`, `handle_offers(receipt, offers, catalog)` |
| Receipt | `Receipt()`, `total_price()`, `add_product(product, quantity, price, total_price)`, `add_discount(discount)`, propriedades `items` e `discounts` |
| ReceiptItem | `ReceiptItem(product, quantity, price, total_price)` e os atributos de mesmo nome |
| Product | `Product(name, unit)`, atributos `name` e `unit` |
| ProductQuantity | `ProductQuantity(product, quantity)`, atributos `product` e `quantity` |
| ProductUnit | valores `EACH` e `KILO` |
| SpecialOfferType | valores `THREE_FOR_TWO`, `TEN_PERCENT_DISCOUNT`, `TWO_FOR_AMOUNT` e `FIVE_FOR_AMOUNT` |
| Offer | `Offer(offer_type, product, argument)` e os atributos de mesmo nome |
| Discount | `Discount(product, description, discount_amount)` e os atributos de mesmo nome |
| SupermarketCatalog | `add_product(product, price)` e `unit_price(product)` |

## 6. Critérios de aceitação pedidos para os combos

| Caso | Requisito | Critério |
|---|---|---|
| Combo completo | RF13 | 1 escova e 1 creme dental: total 22,50 |
| Combo incompleto | RF14 | Só 1 escova: sem desconto |
| Combo repetido | RF14 | 2 escovas e 2 cremes dentais: 2 combos, total 45,00 |
| Excedentes | RF14 | 2 escovas e 1 creme dental: 1 combo, a escova a mais paga preço normal, total 32,50 |
| Regressão das ofertas anteriores | RF16 e RNF02 | Produto com oferta própria fica fora do combo, e recibos sem combo não mudam |

## 7. Relação com o diagnóstico

| Requisito | Itens do diagnóstico |
|---|---|
| RF08 | D12 (correção do "2 por valor" com quantidade ímpar) |
| RF10 | D13 (correção da fração de peso) |
| RF07 | D8 (nome TEN_PERCENT_DISCOUNT mantido, embora aceite qualquer percentual) |
| RNF01 | D5 (`product_with_name` faz parte da interface e é mantido) |
| RNF03 | D11 (falta de testes) |
| RNF04 | D1, D2 e D3 (condicionais por tipo e fórmulas duplicadas) |
| RNF05 | D4 e D11 (cálculo preso ao carrinho e impossível de testar isoladamente) |

Os itens de legibilidade e organização (D6, D7, D9, D10 e D14) não geram requisito próprio.
O tratamento deles fica no plano de contingência e na refatoração.

A ligação de cada requisito com o código e os testes que o atendem será registrada à medida
que a implementação avançar.
