# Requisitos

Projeto: Supermarket Receipt, versão python_pytest.
Base: commit c72d68a do repositório original e o diagnóstico em `docs/diagnostico_tecnico.md`.
Data: 24/11/2026. Revisado em 25/11/2026.

## 1. Escopo

Este documento descreve:

- o comportamento atual do sistema que deve ser preservado: carrinho, recibo e as quatro
  ofertas existentes;
- duas correções de defeitos encontrados no diagnóstico (D12 e D13);
- a nova promoção de combos;
- as decisões sobre dois pontos levantados na revisão (seção 8).

Os preços usados nos critérios de aceitação são exemplos para os testes. Cada critério informa
os preços que usa e mostra a conta. Nos combos foram usados os valores do enunciado: escova a
10,00 e creme dental a 15,00.

## 2. Termos usados

| Termo | Significado |
|---|---|
| Oferta | promoção cadastrada no caixa para um produto. Cada produto tem no máximo uma |
| Desconto | linha do recibo com produto, descrição e valor negativo |
| Combo | conjunto de produtos diferentes cadastrado no caixa. Quem leva uma unidade de cada ganha 10% sobre essas unidades |
| Unidade inteira | parte inteira da quantidade. Produto vendido por peso tem preço por quilo, então cada quilo inteiro é uma unidade. Em 3,5 kg, são 3 unidades inteiras e sobra uma fração de 0,5 kg |

## 3. Requisitos funcionais

### 3.1 Carrinho e recibo

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF01 | O carrinho aceita produtos por unidade ou por peso. O mesmo produto pode ser adicionado mais de uma vez. Cada adição vira uma linha no recibo, e as ofertas são calculadas sobre a quantidade total do produto. Esse comportamento é mantido (decisão P1, seção 8) | Escova a 0,99 com "leve 3, pague 2", adicionada com quantidade 2 e depois com quantidade 1. O recibo mostra 2 linhas: 1,98 (2 × 0,99) e 0,99. A oferta considera as 3 escovas: desconto de -0,99 e total 1,98 |
| RF02 | Cada item do recibo tem produto, quantidade, preço unitário e total da linha (quantidade × preço), na ordem em que entrou no carrinho | Maçã a 1,99 o quilo, 2,5 kg: quantidade 2,5, preço 1,99 e total da linha 4,975 (2,5 × 1,99) |
| RF03 | O total do recibo é a soma dos itens mais a soma dos descontos, que são negativos | Sem ofertas, 1 escova a 0,99 e 2,5 kg de maçã a 1,99 o quilo: 0,99 + 4,975 = 5,965 |
| RF04 | Oferta de um produto que não está no carrinho não gera desconto | 10% cadastrado na escova (0,99) e carrinho só com 2,5 kg de maçã a 1,99 o quilo: nenhum desconto, total 4,975 |
| RF05 | Cada produto tem uma única oferta. Cadastrar outra para o mesmo produto substitui a anterior | Na escova a 0,99, cadastra 10% e depois "leve 3, pague 2". Com 3 escovas vale só o "leve 3, pague 2": desconto de -0,99 e total 1,98 |

### 3.2 Ofertas existentes

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF06 | Leve 3, pague 2: a cada 3 unidades o cliente paga 2. As unidades que sobram pagam preço normal. Texto do desconto: `3 for 2` | Escova a 0,99. 2 unidades: sem desconto, total 1,98. 3 unidades: paga 2, desconto de -0,99, total 1,98. 7 unidades: os 2 grupos de 3 pagam 4 escovas e a 7ª paga preço normal, total 4,95 (5 × 0,99). Sem oferta seriam 6,93, então o desconto é de -1,98 |
| RF07 | Desconto percentual: quantidade × preço × percentual / 100, inclusive sobre frações. O percentual é o valor informado no cadastro da oferta. Texto: o percentual seguido de `% off`, por exemplo `10.0% off`. Apesar do nome TEN_PERCENT_DISCOUNT, aceita qualquer percentual. O tipo também pode ser informado pelo nome PERCENT_DISCOUNT, que é um apelido de TEN_PERCENT_DISCOUNT (decisão P2, seção 8) | Arroz a 2,49 o pacote com 10%: 2 pacotes custam 4,98, desconto de -0,498 (10% de 4,98), total 4,482. Maçã a 1,99 o quilo com 20%: 1 kg tem desconto de -0,398 e texto `20.0% off`. Cadastrar a oferta com PERCENT_DISCOUNT dá o mesmo desconto e o mesmo texto que com TEN_PERCENT_DISCOUNT |
| RF08 | 2 por um valor: cada par paga o valor cadastrado na oferta. A unidade que sobra paga preço normal. Texto: `2 for` seguido do valor, por exemplo `2 for 0.99`. Corrige o defeito D12 | Tomate a 0,69 a caixa, com "2 por 0,99". 1 caixa: 0,69. 2 caixas: 0,99. 3 caixas: 1 par (0,99) + 1 caixa a preço normal (0,69) = 1,68. 4 caixas: 2 pares = 1,98. O código original cobrava 2,175 por 3 caixas, mais do que os 2,07 sem oferta, porque contava 1,5 par e ainda cobrava a caixa que sobrou (D12) |
| RF09 | 5 por um valor: cada grupo de 5 unidades paga o valor cadastrado. As que sobram pagam preço normal. Texto: `5 for` seguido do valor, por exemplo `5 for 7.49` | Creme dental a 1,79 com "5 por 7,49". 4 unidades: sem desconto, total 7,16 (4 × 1,79). 5 unidades: total 7,49; sem oferta seriam 8,95, então o desconto é de -1,46. 6 unidades: 7,49 + 1,79 = 9,28 |
| RF10 | Nas ofertas por quantidade (RF06, RF08 e RF09), só unidades inteiras formam grupos. A fração de um produto vendido por peso paga preço normal. Corrige o defeito D13 | Maçã a 1,99 o quilo com "leve 3, pague 2", e o cliente leva 3,5 kg (sem oferta: 6,965). Os 3 kg inteiros formam um grupo e pagam 2 kg: 3,98. O 0,5 kg que sobra paga preço normal: 0,995. Total 4,975, desconto de -1,99. O código original cobrava 3,98: o 0,5 kg saía de graça (D13) |
| RF11 | No recibo, os descontos das ofertas vêm na ordem em que os produtos entraram no carrinho. Os descontos de combo vêm depois | Arroz a 2,49 com 10% e escova a 0,99 com "leve 3, pague 2". Entram no carrinho 1 pacote de arroz e depois 3 escovas. O recibo mostra primeiro o desconto do arroz (-0,249) e depois o da escova (-0,99) |

### 3.3 Combos

Preços usados nesta seção, salvo indicação: escova a 10,00 e creme dental a 15,00.

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF12 | O caixa cadastra um combo informando os produtos que o compõem. O combo precisa de 2 ou mais produtos diferentes. Se não tiver, o cadastro é recusado com erro | [escova, creme dental] é aceito. [escova] (um produto só) e [escova, escova] (produto repetido) são recusados com erro |
| RF13 | Combo completo: 10% de desconto sobre uma unidade de cada produto do combo, com uma linha de desconto por produto e o texto `bundle 10% off` | 1 escova (10,00) e 1 creme dental (15,00) = 25,00. Descontos de -1,00 na escova e -1,50 no creme dental, -2,50 no total. Total 22,50 |
| RF14 | Combos repetidos, excedentes e incompletos: o número de combos é a menor quantidade entre os produtos do combo. O que sobra paga preço normal | 2 escovas e 1 creme dental = 35,00: forma 1 combo (-2,50) e a 2ª escova paga preço normal, total 32,50. 2 escovas e 2 cremes dentais = 50,00: forma 2 combos (-5,00), total 45,00. Só 1 escova: falta o creme dental, sem combo, total 10,00 |
| RF15 | Produto vendido por peso em combo: o preço do catálogo é por quilo, então cada quilo inteiro conta como uma unidade do combo. A fração paga preço normal | Combo [maçã, escova], com maçã a 2,00 o quilo. 1,5 kg de maçã (3,00) e 1 escova (10,00) = 13,00. Entram no combo 1 kg de maçã (2,00) e a escova (10,00): 10% de 12,00 = -1,20 (-0,20 na maçã e -1,00 na escova). O 0,5 kg restante paga preço normal. Total 11,80. Com 0,5 kg de maçã (1,00) e 1 escova (10,00) não há 1 kg inteiro: sem combo, total 11,00 |
| RF16 | Convivência com outras ofertas: produto com oferta própria cadastrada não entra em combo, mesmo quando a quantidade não é suficiente para a oferta dar desconto | Escova com "leve 3, pague 2" e combo [escova, creme dental]. 1 escova e 1 creme dental = 25,00: o "leve 3, pague 2" não se aplica (precisa de 3 escovas) e a escova não entra no combo. Nenhum desconto, total 25,00. 3 escovas e 1 creme dental = 45,00: o "leve 3, pague 2" dá uma escova de graça (-10,00) e não há combo. Total 35,00 |
| RF17 | Combos que usam o mesmo produto: cada unidade entra em um único combo, seguindo a ordem em que os combos foram cadastrados | Fio dental a 5,00. Cadastrados nesta ordem: combo A [escova, creme dental] e combo B [escova, fio dental]. 1 escova, 1 creme dental e 1 fio dental = 30,00: a única escova vai para o combo A, cadastrado primeiro (10% de 25,00 = -2,50). O combo B fica sem escova e o fio dental paga preço normal. Total 27,50. 2 escovas, 1 creme dental e 1 fio dental = 40,00: a 1ª escova fecha o combo A (-2,50) e a 2ª fecha o combo B (10% de 15,00 = -1,50). Total 36,00 |

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
  de prever e de testar. Consequência aceita: se a oferta própria não for atingida, como em
  1 escova com "leve 3, pague 2", o produto fica sem desconto nenhum. A alternativa
  considerada foi liberar para o combo as unidades que a oferta própria não usou. Ela foi
  descartada porque cada oferta teria de informar quantas unidades usou, o que torna a regra
  mais difícil de prever e de testar.
- **Combos diferentes com produto em comum (RF17):** cada unidade entra em um combo só, na
  ordem de cadastro, para não haver desconto duplicado. A alternativa de escolher o combo de
  maior desconto foi descartada: exige comparar combinações de combos e o resultado fica mais
  difícil de prever.
- **Produtos por peso (RF15):** o preço de um produto vendido por peso é por quilo, então o
  quilo é a unidade do produto. Só quilos inteiros entram no combo, a mesma regra adotada para
  as ofertas por quantidade no RF10.
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
| RNF03 | Testes automatizados com pytest, executados com o comando `pytest` na pasta `python_pytest` | Todos os testes passam, o que `pytest -v` mostra. A tabela da seção 7.2 indica, para cada RF, o teste que o verifica. A cobertura de linhas de `src/`, medida com `coverage`, fica acima de 90% depois da modernização. Antes era de 71% (`docs/evidencias/antes/02_cobertura.txt`) |
| RNF04 | Uma promoção nova pode ser incluída sem alterar o código das ofertas existentes | A implementação dos combos não modifica as regras das ofertas existentes, o que pode ser conferido no diff do commit |
| RNF05 | Cada regra de desconto pode ser testada sozinha, sem montar caixa, carrinho e recibo | Para cada uma das quatro ofertas e para o combo existe ao menos um teste que chama a regra de cálculo diretamente, sem criar Teller, ShoppingCart nem Receipt. Esses testes aparecem na tabela da seção 7.2 |
| RNF06 | Bandit, pip-audit e Safety são executados antes e depois da modernização, com triagem dos alertas | Relatórios em `docs/evidencias/antes/` e `docs/evidencias/depois/`, com todos os alertas analisados |
| RNF07 | Nenhuma dependência nova é adicionada ao projeto | `requirements.txt` igual ao original |

O enunciado não fixa um percentual de cobertura. Ele pede cobertura "quando disponível" e
testes antes e depois. A meta de 90% do RNF03 é da equipe. O `coverage` já faz parte do
`requirements.txt` original, então medir a cobertura não exige dependência nova.

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
| SpecialOfferType | valores `THREE_FOR_TWO`, `TEN_PERCENT_DISCOUNT`, `TWO_FOR_AMOUNT` e `FIVE_FOR_AMOUNT`. O apelido `PERCENT_DISCOUNT` é acrescentado sem remover nada (decisão P2) |
| Offer | `Offer(offer_type, product, argument)` e os atributos de mesmo nome |
| Discount | `Discount(product, description, discount_amount)` e os atributos de mesmo nome |
| SupermarketCatalog | `add_product(product, price)` e `unit_price(product)` |

## 6. Critérios de aceitação pedidos para os combos

Preços: escova a 10,00, creme dental a 15,00 e fio dental a 5,00. Combo [escova, creme
dental], com 10% de desconto.

| Caso | Requisito | Carrinho e conta | Total esperado |
|---|---|---|---|
| Combo completo | RF13 | 1 escova + 1 creme dental = 25,00. Forma 1 combo: 10% de 25,00 = -2,50 | 22,50 |
| Combo incompleto | RF14 | Só 1 escova = 10,00. Falta o creme dental, então não há combo nem desconto | 10,00 |
| Combo repetido | RF14 | 2 escovas + 2 cremes dentais = 50,00. Formam 2 combos: 2 × -2,50 = -5,00 | 45,00 |
| Excedentes | RF14 | 2 escovas + 1 creme dental = 35,00. Forma 1 combo (-2,50). A 2ª escova não tem creme dental para formar outro combo e paga preço normal | 32,50 |
| Múltiplos combos com produto em comum | RF17 | Combo A [escova, creme dental] cadastrado antes do combo B [escova, fio dental]. 2 escovas + 1 creme dental + 1 fio dental = 40,00. Combo A: -2,50. Combo B: 10% de 15,00 = -1,50 | 36,00 |
| Regressão das ofertas anteriores | RF16 e RNF02 | Escova com "leve 3, pague 2" e combo [escova, creme dental]. 3 escovas + 1 creme dental = 45,00. Vale só o "leve 3, pague 2", uma escova de graça (-10,00). A escova não entra no combo, então não há desconto duplicado | 35,00 |
| Regressão sem combo cadastrado | RNF02 | Os carrinhos dos critérios do RF06 ao RF10 dão os mesmos totais, descontos e textos com e sem a implementação dos combos | iguais aos do RF06 ao RF10 |

## 7. Rastreabilidade

### 7.1 Relação com o diagnóstico

| Requisito | Itens do diagnóstico |
|---|---|
| RF08 | D12 (correção do "2 por valor" com quantidade ímpar) |
| RF10 | D13 (correção da fração de peso) |
| RF07 | D8 (nome TEN_PERCENT_DISCOUNT aceita qualquer percentual; resolvido com o apelido PERCENT_DISCOUNT, decisão P2) |
| RNF01 | D5 (`product_with_name` faz parte da interface e é mantido) |
| RNF03 | D11 (falta de testes) |
| RNF04 | D1, D2 e D3 (condicionais por tipo e fórmulas duplicadas) |
| RNF05 | D4 e D11 (cálculo preso ao carrinho e impossível de testar isoladamente) |

Os itens de legibilidade e organização (D6, D7, D9, D10 e D14) não geram requisito próprio.
O tratamento deles fica no plano de contingência e na refatoração.

### 7.2 Requisito, implementação e teste

O enunciado pede a rastreabilidade requisito → implementação → caso de teste → evidência.
Esta tabela é preenchida à medida que a implementação avança. Para cada requisito, ela informa
a classe ou o método que o implementa, o arquivo e o nome do teste que o verifica, e a
evidência da execução. É por ela que se confere o RNF03 (cada RF tem teste) e o RNF05 (cada
regra tem teste isolado).

## 8. Pontos decididos na revisão

Os dois pontos abaixo foram levantados na revisão de 25/11/2026 e decididos pela equipe.

### P1. Mesmo produto em mais de uma linha do recibo (RF01)

Hoje, cada vez que um produto é adicionado ao carrinho, o recibo ganha uma linha. Escova
adicionada com quantidade 2 e depois com quantidade 1 gera duas linhas da escova. O total e
as ofertas já estão certos, porque as ofertas usam a soma das quantidades.

Proposta analisada: mostrar uma linha por produto, com a quantidade somada.

- A favor: o recibo fica mais limpo e mais fácil de conferir.
- Contra: muda a lista de itens (`receipt.items`) do recibo devolvido por
  `checks_out_articles_from` e o texto do recibo impresso. O enunciado manda preservar os
  valores exibidos no recibo e o contrato observável das interfaces públicas, e penaliza a
  quebra injustificada de regra ou interface. Diferente do RF08 e do RF10, aqui não há valor
  cobrado errado, então a justificativa é mais fraca.

Decisão: manter o comportamento do código original. Cada adição continua sendo uma linha do
recibo, como descreve o RF01. Os testes de caracterização registram esse comportamento.

### P2. Nome TEN_PERCENT_DISCOUNT com qualquer percentual (RF07)

O nome diz 10%, mas a oferta aplica o percentual informado no cadastro. O README do kata cita
"20% discount on apples" como exemplo desse tipo de oferta, e o código original gera
`20.0% off` sem erro. Ou seja, o comportamento de aceitar qualquer percentual é intencional, e
o nome é que não o descreve.

Opções:

| Opção | Efeito | Risco |
|---|---|---|
| Manter como está | Nada muda | O nome continua enganoso (D8) |
| Fixar em 10% | Só 10% passa a ser aceito | Remove uma regra existente: 20% na maçã deixa de ser possível |
| Renomear para PERCENT_DISCOUNT | Nome correto | Quebra a interface pública: `tests/test_supermarket.py` usa TEN_PERCENT_DISCOUNT e deixa de passar (RNF01) |
| Manter o nome e acrescentar PERCENT_DISCOUNT como apelido | Os dois nomes apontam para o mesmo tipo de oferta. O código existente continua funcionando e o código novo usa o nome correto | Acrescenta um nome ao enum, sem remover nada |

Decisão: manter o nome TEN_PERCENT_DISCOUNT e acrescentar PERCENT_DISCOUNT como apelido.

Em Python, quando dois nomes de um enum recebem o mesmo valor, o segundo vira apelido do
primeiro: os dois são o mesmo membro. Com isso:

- `SpecialOfferType.PERCENT_DISCOUNT is SpecialOfferType.TEN_PERCENT_DISCOUNT` é verdadeiro;
- a lista de tipos de oferta continua com quatro tipos;
- o texto do desconto não muda, porque vem do percentual cadastrado e não do nome;
- o teste original continua passando sem alteração (RNF01).

O código novo passa a usar PERCENT_DISCOUNT. O nome antigo continua valendo para quem já o
usa. A mudança entra na refatoração, e o plano de contingência indica em qual etapa.
