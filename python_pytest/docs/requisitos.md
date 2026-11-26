
# Requisitos

Projeto: Supermarket Receipt, versão python_pytest.

## 1. Escopo

Este documento descreve:

- o comportamento atual do sistema que deve ser preservado: carrinho, recibo e as quatro ofertas existentes;
- dois defeitos de cálculo encontrados no diagnóstico (D12 e D13), que são mantidos como no código original;
- a nova promoção de combos;
- as decisões tomadas pela equipe na revisão (seção 8).

Os preços usados nos critérios de aceitação são exemplos para os testes. Cada critério informa os preços utilizados e apresenta o cálculo correspondente. Nos combos foram usados os valores do enunciado: escova a 10,00 e creme dental a 15,00.

## 2. Termos usados

| Termo | Significado |
|---|---|
| Oferta | Promoção cadastrada no caixa para um produto. Cada produto tem no máximo uma. |
| Desconto | Linha do recibo com produto, descrição e valor negativo. |
| Combo | Conjunto de produtos diferentes cadastrado no caixa. Quem leva uma unidade de cada ganha 10% de desconto sobre essas unidades. |
| Unidade inteira | Parte inteira da quantidade. Produto vendido por peso tem preço por quilo, então cada quilo inteiro é uma unidade. Em 3,5 kg, são 3 unidades inteiras e sobra uma fração de 0,5 kg. |

## 3. Requisitos funcionais

### 3.1 Carrinho e recibo

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF01 | O carrinho aceita produtos por unidade ou por peso. O mesmo produto pode ser adicionado mais de uma vez. Cada adição vira uma linha no recibo, e as ofertas são calculadas sobre a quantidade total do produto. Esse comportamento é mantido (decisão P1, seção 8). | Escova a 0,99 com "leve 3, pague 2", adicionada com quantidade 2 e depois com quantidade 1. O recibo mostra 2 linhas: 1,98 (2 × 0,99) e 0,99. A oferta considera as 3 escovas: desconto de -0,99 e total 1,98. |
| RF02 | Cada item do recibo tem produto, quantidade, preço unitário e total da linha (quantidade × preço), na ordem em que entrou no carrinho. | Maçã a 1,99 o quilo, 2,5 kg: quantidade 2,5, preço 1,99 e total da linha 4,975 (2,5 × 1,99). |
| RF03 | O total do recibo é a soma dos itens mais a soma dos descontos, que são negativos. | Sem ofertas, 1 escova a 0,99 e 2,5 kg de maçã a 1,99 o quilo: 0,99 + 4,975 = 5,965. |
| RF04 | Oferta de um produto que não está no carrinho não gera desconto. | 10% cadastrado na escova (0,99) e carrinho só com 2,5 kg de maçã a 1,99 o quilo: nenhum desconto, total 4,975. |
| RF05 | Cada produto tem uma única oferta. Cadastrar outra para o mesmo produto substitui a anterior. | Na escova a 0,99, cadastra 10% e depois "leve 3, pague 2". Com 3 escovas vale só o "leve 3, pague 2": desconto de -0,99 e total 1,98. |

### 3.2 Ofertas existentes

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF06 | Leve 3, pague 2: a cada 3 unidades o cliente paga 2. As unidades que sobram pagam preço normal. Texto do desconto: `3 for 2`. | Escova a 0,99. 2 unidades: sem desconto, total 1,98. 3 unidades: paga 2, desconto de -0,99, total 1,98. 7 unidades: os 2 grupos de 3 pagam 4 escovas e a 7ª paga preço normal, total 4,95 (5 × 0,99). Sem oferta seriam 6,93, então o desconto é de -1,98. |
| RF07 | Desconto percentual: quantidade × preço × percentual / 100, inclusive sobre frações. O percentual é o valor informado no cadastro da oferta. Texto: o percentual seguido de `% off`, por exemplo `10.0% off`. Apesar do nome TEN_PERCENT_DISCOUNT, aceita qualquer percentual. O nome é mantido (decisão P2, seção 8). | Arroz a 2,49 o pacote com 10%: 2 pacotes custam 4,98, desconto de -0,498 (10% de 4,98), total 4,482. Maçã a 1,99 o quilo com 20%: 1 kg tem desconto de -0,398 e texto `20.0% off`. |
| RF08 | 2 por um valor: a oferta vale a partir de 2 unidades. Com quantidade par, cada par paga o valor cadastrado. Com quantidade ímpar, vale a conta do código original: o valor cadastrado vezes a metade da quantidade, mais uma unidade a preço normal. Assim, a unidade que sobra é cobrada duas vezes. Esse é o defeito D12, mantido (seção 8, P3). Texto: `2 for` seguido do valor, por exemplo `2 for 0.99`. | Tomate a 0,69 a caixa, com "2 por 0,99". 1 caixa: 0,69, sem desconto. 2 caixas: 0,99. 3 caixas: 0,99 × 1,5 + 0,69 = 2,175, mais do que os 2,07 sem oferta. 4 caixas: 2 pares = 1,98. 5 caixas: 0,99 × 2,5 + 0,69 = 3,165. O certo seria 1,68 com 3 caixas e 2,67 com 5. |
| RF09 | 5 por um valor: cada grupo de 5 unidades paga o valor cadastrado. As que sobram pagam preço normal. Texto: `5 for` seguido do valor, por exemplo `5 for 7.49`. | Creme dental a 1,79 com "5 por 7,49". 4 unidades: sem desconto, total 7,16 (4 × 1,79). 5 unidades: total 7,49; sem oferta seriam 8,95, então o desconto é de -1,46. 6 unidades: 7,49 + 1,79 = 9,28. |
| RF10 | Nas ofertas por quantidade (RF06, RF08 e RF09), os grupos são contados só com as unidades inteiras, mas o desconto é calculado sobre a quantidade completa. Assim, quando a oferta se aplica, a fração de um produto vendido por peso sai de graça. Esse é o defeito D13, mantido (seção 8, P3). | Maçã a 1,99 o quilo com "leve 3, pague 2", e o cliente leva 3,5 kg (sem oferta: 6,965). Os 3 kg inteiros formam um grupo e pagam 2 kg: 3,98. O 0,5 kg não é cobrado. Total 3,98, desconto de -2,985. O certo seria cobrar o 0,5 kg a preço normal, com total de 4,975. |
| RF11 | No recibo, os descontos das ofertas vêm na ordem em que os produtos entraram no carrinho. Os descontos de combo vêm depois. | Arroz a 2,49 com 10% e escova a 0,99 com "leve 3, pague 2". Entram no carrinho 1 pacote de arroz e depois 3 escovas. O recibo mostra primeiro o desconto do arroz (-0,249) e depois o da escova (-0,99). |

### 3.3 Combos

Preços usados nesta seção, salvo indicação: escova a 10,00 e creme dental a 15,00.

| # | Requisito | Critério de aceitação |
|---|---|---|
| RF12 | O caixa cadastra um combo informando os produtos que o compõem. O combo precisa de 2 ou mais produtos diferentes. Se não tiver, o cadastro é recusado com erro. | [escova, creme dental] é aceito. [escova] (um produto só) e [escova, escova] (produto repetido) são recusados com erro. |
| RF13 | Combo completo: 10% de desconto sobre uma unidade de cada produto do combo, com uma linha de desconto por produto e o texto `bundle 10% off`. | 1 escova (10,00) e 1 creme dental (15,00) = 25,00. Descontos de -1,00 na escova e -1,50 no creme dental, -2,50 no total. Total 22,50. |
| RF14 | Combos repetidos, excedentes e incompletos: o número de combos é a menor quantidade entre os produtos do combo. O que sobra paga preço normal. | 2 escovas e 1 creme dental = 35,00: forma 1 combo (-2,50) e a 2ª escova paga preço normal, total 32,50. 2 escovas e 2 cremes dentais = 50,00: forma 2 combos (-5,00), total 45,00. Só 1 escova: falta o creme dental, sem combo, total 10,00. |
| RF15 | Produto vendido por peso em combo: o preço do catálogo é por quilo, então cada quilo inteiro conta como uma unidade do combo. A fração paga preço normal. | Combo [maçã, escova], com maçã a 2,00 o quilo. 1,5 kg de maçã (3,00) e 1 escova (10,00) = 13,00. Entram no combo 1 kg de maçã (2,00) e a escova (10,00): 10% de 12,00 = -1,20 (-0,20 na maçã e -1,00 na escova). O 0,5 kg restante paga preço normal. Total 11,80. Com 0,5 kg de maçã (1,00) e 1 escova (10,00) não há 1 kg inteiro: sem combo, total 11,00. |
| RF16 | Convivência com outras ofertas: produto com oferta própria cadastrada não entra em combo, mesmo quando a quantidade não é suficiente para a oferta dar desconto. | Escova com "leve 3, pague 2" e combo [escova, creme dental]. 1 escova e 1 creme dental = 25,00: o "leve 3, pague 2" não se aplica (precisa de 3 escovas) e a escova não entra no combo. Nenhum desconto, total 25,00. 3 escovas e 1 creme dental = 45,00: o "leve 3, pague 2" dá uma escova de graça (-10,00) e não há combo. Total 35,00. |
| RF17 | Combos que usam o mesmo produto: cada unidade entra em um único combo, seguindo a ordem em que os combos foram cadastrados. | Fio dental a 5,00. Cadastrados nesta ordem: combo A [escova, creme dental] e combo B [escova, fio dental]. 1 escova, 1 creme dental e 1 fio dental = 30,00: a única escova vai para o combo A, cadastrado primeiro (10% de 25,00 = -2,50). O combo B fica sem escova e o fio dental paga preço normal. Total 27,50. 2 escovas, 1 creme dental e 1 fio dental = 40,00: a 1ª escova fecha o combo A (-2,50) e a 2ª fecha o combo B (10% de 15,00 = -1,50). Total 36,00. |

## 4. Decisões sobre os combos

Esta seção registra as decisões adotadas para o tratamento de múltiplos combos e sua convivência com as ofertas existentes.

- **Composição (RF12 e RF13):** um combo é formado por uma unidade de cada produto, com pelo menos dois produtos diferentes.
- **Múltiplos combos do mesmo tipo (RF14):** valem tantos combos quanto a quantidade do produto mais escasso. O excedente paga preço normal.
- **Convivência com outras ofertas (RF16):** produto com oferta própria não participa de combos. Assim, nenhum recibo que já tinha oferta muda de valor, e não existe a possibilidade de dois descontos sobre o mesmo item. A regra considera apenas o cadastro da oferta, evitando que um mesmo produto receba dois descontos. Consequência aceita: se a oferta própria não for atingida, como em 1 escova com "leve 3, pague 2", o produto fica sem desconto nenhum. A alternativa considerada foi liberar para o combo as unidades que a oferta própria não utilizou. Ela foi descartada porque cada oferta teria de informar quantas unidades utilizou, o que torna a regra mais difícil de prever e testar.
- **Combos diferentes com produto em comum (RF17):** cada unidade entra em um combo só, na ordem de cadastro, para evitar descontos duplicados. A alternativa de escolher o combo de maior desconto foi descartada: exige comparar combinações de combos e o resultado fica mais difícil de prever.
- **Produtos por peso (RF15):** o preço de um produto vendido por peso é por quilo, então o quilo é a unidade do produto. Só quilos inteiros entram no combo, e a fração paga preço normal. As ofertas por quantidade também contam só unidades inteiras (RF10), mas nelas a fração sai de graça por causa do defeito D13, que é mantido. O combo é uma regra nova, então cobra a fração do jeito certo.
- **Recibo (RF11 e RF13):** uma linha de desconto por produto do combo. A classe Discount liga cada desconto a um produto, então não é preciso mudar a estrutura do recibo. Os descontos de combo vêm depois dos demais, e um recibo sem combo fica igual ao do código original.

Consequência do RF17: se dois combos usam a escova e o cliente leva 2 escovas, aparecem duas linhas de desconto da escova, uma por combo. Cada unidade recebe um único desconto.

## 5. Requisitos não funcionais

| # | Requisito | Critério de aceitação |
|---|---|---|
| RNF01 | As interfaces públicas são preservadas: classes e métodos públicos mantêm nome, parâmetros e retorno (lista na seção 5.1). Mudanças internas são permitidas quando justificadas. | O teste original `tests/test_supermarket.py` passa sem nenhuma alteração. |
| RNF02 | Os valores e textos do recibo são preservados sem exceção, inclusive nos defeitos D12 e D13. | Os testes de caracterização escritos sobre o código original continuam passando sem nenhuma alteração, inclusive o texto impresso pelo ReceiptPrinter. Um recibo sem combo fica idêntico ao do código original. |
| RNF03 | Testes automatizados com pytest, executados com o comando `pytest` na pasta `python_pytest`. | Todos os testes passam, conforme mostrado por `pytest -v`. A tabela da seção 7.2 indica, para cada RF, o teste que o verifica. A cobertura de linhas de `src/`, medida com `coverage`, fica acima de 90% depois da modernização. Antes era de 71% (`docs/evidencias/antes/02_cobertura.txt`). |
| RNF04 | Uma promoção nova pode ser incluída sem alterar o código das ofertas existentes. | A implementação dos combos não modifica as regras das ofertas existentes, o que pode ser conferido no diff do commit. |
| RNF05 | Cada regra de desconto pode ser testada sozinha, sem montar caixa, carrinho e recibo. | Para cada uma das quatro ofertas e para o combo existe ao menos um teste que chama a regra de cálculo diretamente, sem criar Teller, ShoppingCart nem Receipt. Esses testes aparecem na tabela da seção 7.2. |
| RNF06 | Bandit, pip-audit e Safety são executados antes e depois da modernização, com triagem dos alertas. | Relatórios em `docs/evidencias/antes/` e `docs/evidencias/depois/`, com todos os alertas analisados. |
| RNF07 | Nenhuma dependência nova é adicionada ao projeto. | `requirements.txt` igual ao original. |

O enunciado não estabelece um percentual mínimo de cobertura. Ele pede cobertura "quando disponível" e testes antes e depois. A meta de 90% do RNF03 foi definida pela equipe. O `coverage` já faz parte do `requirements.txt` original, então medir a cobertura não exige dependência nova.

### 5.1 Interfaces públicas que devem ser mantidas (RNF01)

| Classe | O que é mantido |
|---|---|
| Teller | `Teller(catalog)`, `add_special_offer(offer_type, product, argument)`, `checks_out_articles_from(the_cart)` devolvendo um Receipt, `product_with_name(name)`, atributos `catalog` e `offers`. |
| ShoppingCart | `ShoppingCart()`, propriedades `items` e `product_quantities`, `add_item(product)`, `add_item_quantity(product, quantity)`, `handle_offers(receipt, offers, catalog)`. |
| Receipt | `Receipt()`, `total_price()`, `add_product(product, quantity, price, total_price)`, `add_discount(discount)`, propriedades `items` e `discounts`. |
| ReceiptItem | `ReceiptItem(product, quantity, price, total_price)` e os atributos de mesmo nome. |
| Product | `Product(name, unit)`, atributos `name` e `unit`. |
| ProductQuantity | `ProductQuantity(product, quantity)`, atributos `product` e `quantity`. |
| ProductUnit | valores `EACH` e `KILO`. |
| SpecialOfferType | valores `THREE_FOR_TWO`, `TEN_PERCENT_DISCOUNT`, `TWO_FOR_AMOUNT` e `FIVE_FOR_AMOUNT`. |
| Offer | `Offer(offer_type, product, argument)` e os atributos de mesmo nome. |
| Discount | `Discount(product, description, discount_amount)` e os atributos de mesmo nome. |
| SupermarketCatalog | `add_product(product, price)` e `unit_price(product)`. |

## 6. Critérios de aceitação pedidos para os combos

Preços: escova a 10,00, creme dental a 15,00 e fio dental a 5,00. Combo [escova, creme dental], com 10% de desconto.

| Caso | Requisito | Carrinho e conta | Total esperado |
|---|---|---|---|
| Combo completo | RF13 | 1 escova + 1 creme dental = 25,00. Forma 1 combo: 10% de 25,00 = -2,50. | 22,50 |
| Combo incompleto | RF14 | Só 1 escova = 10,00. Falta o creme dental, então não há combo nem desconto. | 10,00 |
| Combo repetido | RF14 | 2 escovas + 2 cremes dentais = 50,00. Formam 2 combos: 2 × -2,50 = -5,00. | 45,00 |
| Excedentes | RF14 | 2 escovas + 1 creme dental = 35,00. Forma 1 combo (-2,50). A 2ª escova não tem creme dental para formar outro combo e paga preço normal. | 32,50 |
| Múltiplos combos com produto em comum | RF17 | Combo A [escova, creme dental] cadastrado antes do combo B [escova, fio dental]. 2 escovas + 1 creme dental + 1 fio dental = 40,00. Combo A: -2,50. Combo B: 10% de 15,00 = -1,50. | 36,00 |
| Regressão das ofertas anteriores | RF16 e RNF02 | Escova com "leve 3, pague 2" e combo [escova, creme dental]. 3 escovas + 1 creme dental = 45,00. Vale só o "leve 3, pague 2", uma escova de graça (-10,00). A escova não entra no combo, então não há desconto duplicado. | 35,00 |
| Regressão sem combo cadastrado | RNF02 | Os carrinhos dos critérios do RF06 ao RF10 dão os mesmos totais, descontos e textos com e sem a implementação dos combos. | iguais aos do RF06 ao RF10 |

## 7. Rastreabilidade

### 7.1 Relação com o diagnóstico

| Requisito | Itens do diagnóstico |
|---|---|
| RF08 | D12 ("2 por valor" cobra a mais com quantidade ímpar; defeito mantido, P3). |
| RF10 | D13 (fração de peso não é cobrada; defeito mantido, P3). |
| RF07 | D8 (nome TEN_PERCENT_DISCOUNT aceita qualquer percentual; nome mantido, decisão P2). |
| RNF01 | D5 (`product_with_name` faz parte da interface e é mantido como está, com o defeito; P3). |
| RNF03 | D11 (falta de testes). |
| RNF04 | D1, D2 e D3 (condicionais por tipo e fórmulas duplicadas). |
| RNF05 | D4 e D11 (cálculo preso ao carrinho e impossível de testar isoladamente). |

Os itens de legibilidade e organização (D6, D7, D9, D10 e D14) não geram requisito próprio. O tratamento deles fica no plano de contingência e na refatoração.

### 7.2 Requisito, implementação e teste

A rastreabilidade relaciona cada requisito à sua implementação, aos testes correspondentes e às evidências de execução. Para cada requisito, as tabelas abaixo informam onde ele está implementado, quais testes o verificam e onde está registrada a evidência. As tabelas também permitem verificar o atendimento ao RNF03 (cada RF tem teste) e ao RNF05 (cada regra tem teste isolado). Foram preenchidas na etapa E10 do plano de contingência, depois da implementação dos combos.

Arquivos de teste, todos na pasta `tests/`, e o nome curto usado nas tabelas:

| Nome curto | Arquivo | O que testa |
|---|---|---|
| original | `test_supermarket.py` | teste original do kata, sem nenhuma alteração. |
| legado | `test_comportamento_legado.py` | caracterização: o comportamento do código original, sem alteração desde que foi escrito. |
| estratégias | `test_estrategias_oferta.py` | cada oferta isolada e a classe base das ofertas por quantidade. |
| fábrica | `test_fabrica_ofertas.py` | a fábrica que escolhe a regra de cada oferta. |
| calculadora | `test_calculadora_descontos.py` | a calculadora dos descontos das ofertas. |
| combos | `test_combos.py` | os combos. |

As evidências ficam em `docs/evidencias/`. Nas tabelas, `antes/03` é `docs/evidencias/antes/03_caracterizacao_pytest.txt`, a execução da caracterização no código original, e `depois/01` é `docs/evidencias/depois/01_pytest.txt`, a execução de todos os testes no código final. Os demais seguem o mesmo padrão.

Requisitos funcionais:

| Requisito | Implementação (`src/`) | Testes | Evidência |
|---|---|---|---|
| RF01 | `ShoppingCart.add_item_quantity`, `add_item` e `product_quantities` (`shopping_cart.py`); `Teller.checks_out_articles_from` (`teller.py`). | legado: `test_mesmo_produto_adicionado_duas_vezes_gera_duas_linhas`, `test_oferta_considera_a_soma_das_linhas_do_mesmo_produto`, `test_add_item_adiciona_uma_unidade`, `test_product_quantities_soma_as_quantidades_do_mesmo_produto`. | antes/03 e depois/01 |
| RF02 | `Teller.checks_out_articles_from` (`teller.py`); `Receipt.add_product` e `ReceiptItem` (`receipt.py`). | legado: `test_recibo_tem_uma_linha_por_item_na_ordem_do_carrinho`, `test_recibo_montado_diretamente`. | antes/03 e depois/01 |
| RF03 | `Receipt.total_price` (`receipt.py`). | legado: `test_carrinho_vazio_gera_recibo_vazio`, `test_total_sem_oferta_e_a_soma_dos_itens`; original: `test_ten_percent_discount`. | antes/03 e depois/01 |
| RF04 | `DiscountCalculator.offer_discounts` (`discount_calculator.py`). | legado: `test_oferta_de_produto_fora_do_carrinho_nao_gera_desconto`; calculadora: `test_oferta_de_produto_fora_da_compra_nao_gera_desconto`. | antes/03 e depois/01 |
| RF05 | `Teller.add_special_offer` (`teller.py`). | legado: `test_nova_oferta_substitui_a_anterior_do_mesmo_produto`. | antes/03 e depois/01 |
| RF06 | `ThreeForTwoStrategy` e `QuantityOfferStrategy` (`offer_strategies.py`). | legado: `test_leve_3_pague_2_abaixo_do_minimo_nao_gera_desconto`, `test_leve_3_pague_2`; estratégias: `test_leve_3_pague_2_abaixo_do_minimo_nao_da_desconto`, `test_leve_3_pague_2`. | antes/03 e depois/01 |
| RF07 | `PercentDiscountStrategy` (`offer_strategies.py`). | legado: `test_desconto_percentual`, `test_desconto_percentual_vale_sobre_fracao_de_peso`, `test_ten_percent_discount_aplica_o_percentual_cadastrado_item_mantido_d8`; estratégias: `test_desconto_percentual`, `test_desconto_percentual_aplica_o_percentual_cadastrado_item_mantido_d8`. | antes/03 e depois/01 |
| RF08 | `TwoForAmountStrategy` (`offer_strategies.py`), com o D12 mantido no método `_number_of_groups`. | legado: `test_dois_por_valor_com_1_unidade_nao_gera_desconto`, `test_dois_por_valor_com_quantidade_par`, `test_dois_por_valor_com_3_unidades_cobra_a_mais_item_mantido_d12`, `test_dois_por_valor_com_5_unidades_cobra_a_mais_item_mantido_d12`; estratégias: `test_dois_por_valor_com_1_unidade_nao_da_desconto`, `test_dois_por_valor_com_quantidade_par`, `test_dois_por_valor_com_quantidade_impar_cobra_a_mais_item_mantido_d12`. | antes/03 e depois/01 |
| RF09 | `FiveForAmountStrategy` (`offer_strategies.py`). | legado: `test_cinco_por_valor_abaixo_do_minimo_nao_gera_desconto`, `test_cinco_por_valor`; estratégias: `test_cinco_por_valor_abaixo_do_minimo_nao_da_desconto`, `test_cinco_por_valor`. | antes/03 e depois/01 |
| RF10 | `QuantityOfferStrategy.calculate_discount` (`offer_strategies.py`), com o D13 mantido. | legado: `test_fracao_de_peso_nao_completa_grupo_da_oferta`, `test_fracao_de_peso_sai_de_graca_item_mantido_d13`; estratégias: `test_leve_3_pague_2_nao_cobra_fracao_de_peso_item_mantido_d13`. | antes/03 e depois/01 |
| RF11 | `DiscountCalculator.offer_discounts` (ordem do carrinho) e `Teller.checks_out_articles_from` (combos depois das ofertas). | legado: `test_descontos_seguem_a_ordem_do_carrinho`, `test_todas_as_ofertas_no_mesmo_carrinho`; calculadora: `test_descontos_seguem_a_ordem_dos_produtos`; combos: `test_descontos_de_combo_vem_depois_dos_descontos_das_ofertas`. | antes/03 e depois/01 |
| RF12 | `Teller.add_bundle_offer` (`teller.py`) e `Bundle` (`model_objects.py`). | combos: `test_cadastro_de_combo_com_produtos_diferentes`, `test_cadastro_de_combo_recusa_menos_de_dois_produtos_diferentes`. | depois/01 |
| RF13 | `BundleCalculator.bundle_discounts` (`bundle_calculator.py`). | combos: `test_combo_completo`, `test_recibo_impresso_com_combo`, `test_calculadora_de_combos_isolada`. | depois/01 |
| RF14 | `BundleCalculator.bundle_discounts` (`bundle_calculator.py`). | combos: `test_combo_incompleto_nao_da_desconto`, `test_combo_repetido`, `test_produto_excedente_paga_preco_normal`. | depois/01 |
| RF15 | `BundleCalculator.bundle_discounts` (`bundle_calculator.py`). | combos: `test_produto_por_peso_entra_no_combo_so_com_quilos_inteiros`, `test_produto_por_peso_sem_quilo_inteiro_nao_forma_combo`. | depois/01 |
| RF16 | `BundleCalculator.bundle_discounts` (`bundle_calculator.py`). | combos: `test_produto_com_oferta_propria_fica_fora_do_combo`, `test_produto_com_oferta_propria_fica_fora_mesmo_sem_desconto_da_oferta`. | depois/01 |
| RF17 | `BundleCalculator.bundle_discounts` (`bundle_calculator.py`). | combos: `test_combo_cadastrado_primeiro_fica_com_a_unidade_em_comum`, `test_multiplos_combos_com_produto_em_comum`. | depois/01 |

Requisitos não funcionais:

| Requisito | Como é atendido | Testes | Evidência |
|---|---|---|---|
| RNF01 | As interfaces da seção 5.1 foram mantidas; `handle_offers` continua existindo e repassa o cálculo; o ReceiptPrinter é importado do mesmo jeito. | original, sem nenhuma alteração; legado, grupo das interfaces: `test_add_item_adiciona_uma_unidade`, `test_handle_offers_chamado_diretamente_adiciona_so_os_descontos`, `test_recibo_montado_diretamente`, `test_items_e_discounts_do_recibo_devolvem_copias`, `test_caixa_guarda_o_catalogo_e_comeca_sem_ofertas`. | depois/01 |
| RNF02 | Nenhuma etapa mudou um valor ou um texto do recibo, inclusive nos defeitos mantidos. | Todo o legado, sem alteração desde o commit `60f645f`, incluindo os testes do recibo impresso; combos: `test_recibo_sem_combo_cadastrado_nao_tem_desconto_de_combo`. | antes/03 e depois/01 |
| RNF03 | Testes automatizados com pytest. | Os 100 testes; esta tabela mostra pelo menos um teste para cada RF. | depois/01 (100 testes) e depois/02 (cobertura de 100%, meta acima de 90%). |
| RNF04 | Strategy, Template Method e fábrica simples; combos em classe própria. | estratégias: `test_nova_oferta_por_quantidade_so_preenche_as_lacunas`, `test_nova_oferta_por_quantidade_abaixo_do_minimo_nao_da_desconto`. | O commit `89f6a53` dos combos não altera os arquivos das ofertas (`docs/registro_refatoracao.md`, seção 11.3). |
| RNF05 | Cada regra de desconto numa classe própria. | estratégias (as quatro ofertas); calculadora; combos: `test_calculadora_de_combos_isolada`. | depois/01 |
| RNF06 | Bandit, pip-audit e Safety antes e depois, com as mesmas versões e o mesmo ambiente separado. | não se aplica. | antes/05, antes/06 e antes/07 (linha de base) e depois/05, depois/06 e depois/07: nenhum alerta do Bandit e nenhuma vulnerabilidade nas dependências, antes e depois. |
| RNF07 | Nenhuma biblioteca foi acrescentada. | não se aplica. | depois/00: as mesmas 24 bibliotecas de antes; `requirements.txt` igual ao original. |

## 8. Pontos decididos na revisão

Os pontos abaixo foram decididos pela equipe na revisão de 25/11/2026.

### P1. Mesmo produto em mais de uma linha do recibo (RF01)

Hoje, cada vez que um produto é adicionado ao carrinho, o recibo ganha uma linha. Escova adicionada com quantidade 2 e depois com quantidade 1 gera duas linhas da escova. O total e as ofertas já estão certos, porque as ofertas usam a soma das quantidades.

Proposta analisada: mostrar uma linha por produto, com a quantidade somada.

- A favor: o recibo fica mais limpo e mais fácil de conferir.
- Contra: muda a lista de itens (`receipt.items`) do recibo devolvido por `checks_out_articles_from` e o texto do recibo impresso. O enunciado manda preservar os valores exibidos no recibo e o contrato observável das interfaces públicas, além de penalizar a quebra injustificada de regras ou interfaces. Nesse caso, não há valor cobrado errado, portanto não existe justificativa para a mudança.

Decisão: manter o comportamento do código original. Cada adição continua sendo uma linha do recibo, como descreve o RF01. Os testes de caracterização registram esse comportamento.

### P2. Nome TEN_PERCENT_DISCOUNT com qualquer percentual (RF07)

O nome diz 10%, mas a oferta aplica o percentual informado no cadastro. O README do kata cita "20% discount on apples" como exemplo desse tipo de oferta, e o código original gera `20.0% off` sem erro. Ou seja, o comportamento de aceitar qualquer percentual é intencional, e o nome é que não o descreve.

Opções:

| Opção | Efeito | Risco |
|---|---|---|
| Manter como está | Nada muda. | O nome continua enganoso (D8). |
| Fixar em 10% | Só 10% passa a ser aceito. | Remove uma regra existente: 20% na maçã deixa de ser possível. |
| Renomear para PERCENT_DISCOUNT | Nome correto. | Quebra a interface pública: `tests/test_supermarket.py` usa TEN_PERCENT_DISCOUNT e deixa de passar (RNF01). |
| Manter o nome e acrescentar PERCENT_DISCOUNT como apelido | Os dois nomes apontam para o mesmo tipo de oferta. O código existente continua funcionando e o código novo usa o nome correto. | Dois nomes para a mesma oferta, o que é redundante. |

Decisão: manter o nome TEN_PERCENT_DISCOUNT como está, sem acrescentar outro nome.

Renomear quebraria o teste original e a interface pública (RNF01). O apelido resolveria o problema do nome, mas deixaria dois nomes para a mesma oferta, o que é redundante. Por isso, o nome fica como está, e o problema é apresentado junto com os itens mantidos (P3), incluindo a correção que seria feita.

### P3. Defeitos de comportamento D5, D12 e D13

O diagnóstico encontrou três defeitos que fazem o sistema apresentar resultados incorretos:

- D5: `Teller.product_with_name` só funciona com o FakeCatalog. Com o catálogo real, dá erro.
- D12: no "2 por valor", com quantidade ímpar, a unidade que sobra é cobrada duas vezes (RF08).
- D13: nas ofertas por quantidade, quando a oferta se aplica, a fração de um produto vendido por peso sai de graça (RF10).

Decisão: manter os três como estão no código original.

O enunciado manda preservar as regras comerciais existentes, os cálculos e os valores exibidos no recibo. Mantendo os defeitos, a comparação entre antes e depois da refatoração mostra saídas idênticas, e qualquer diferença indica erro na refatoração. Os defeitos ficam registrados nos testes de caracterização, com o resultado atual, e a apresentação mostra cada um e como seria corrigido. A correção proposta para cada defeito está no plano de contingência (seção 3.1).
