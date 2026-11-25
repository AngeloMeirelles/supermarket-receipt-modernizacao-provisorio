# Plano de contingência e refatoração

Projeto: Supermarket Receipt, versão python_pytest.
Base: commit c72d68a do repositório original, o diagnóstico em `docs/diagnostico_tecnico.md` e
os requisitos em `docs/requisitos.md`.
Data: 25/11/2026.

## 1. Objetivo

Este plano define como o código legado será alterado sem mudar o comportamento de forma
indevida. Ele indica a ordem das mudanças, os riscos de cada uma, como evitá-los, quais testes
detectam um problema e como voltar atrás se houver regressão. Também registra o tratamento de
cada item do diagnóstico (D1 a D14), os comportamentos que não podem mudar e as interfaces que
precisam continuar compatíveis.

Regra geral: nenhum resultado do sistema atual é alterado. Antes de mexer no código, testes
registram o comportamento atual, e esses testes precisam continuar passando, sem alteração,
até o fim do trabalho.

## 2. Sequência das mudanças

Cada etapa só começa quando a anterior cumpre seus critérios de aceitação (seção 6). Uma etapa
pode ter mais de um commit, desde que todos os testes passem em cada um.

| Etapa | Passo do enunciado | O que muda | Itens | Testes associados | Commit |
|---|---|---|---|---|---|
| E1 | 6 | Testes de caracterização sobre o código original, sem mexer em `src/`. Registram o comportamento atual, inclusive o dos itens que são mantidos (seção 3.1) | D11 | `tests/test_comportamento_legado.py` | `test:` |
| E2 | 7 | Linha de base de segurança: Bandit, pip-audit e Safety sobre o código original | RNF06 | não se aplica | `docs:` |
| E3 | 8 | ReceiptPrinter passa de `tests/` para `src/`, sem mudar o conteúdo | D14 | caracterização do recibo impresso | `refactor:` |
| E4 | 8 | Nomes das variáveis internas, constantes no lugar dos números soltos e anotações de tipo | D7, D8, D9 | caracterização e teste original | `refactor:` |
| E5 | 8 | Strategy: uma interface de oferta e uma classe para cada tipo de oferta | D1, D2, D6 | caracterização e testes de cada oferta isolada (RNF05) | `refactor:` |
| E6 | 8 | Template Method: os passos comuns das ofertas por quantidade vão para uma classe base. O resultado do D12 continua igual, isolado em um método da classe do "2 por valor" | D3 | os mesmos de E5, inclusive os testes do D12 e do D13 | `refactor:` |
| E7 | 8 | Fábrica que escolhe a classe da oferta pelo tipo, no lugar do if/elif | D1 | os mesmos de E5 e teste da fábrica | `refactor:` |
| E8 | 8 | O cálculo dos descontos sai do ShoppingCart para uma classe própria. `handle_offers` continua existindo e repassa a chamada | D4 | caracterização e teste original | `refactor:` |
| E9 | 9 | Combos, conforme RF12 a RF17 | combos | `tests/test_combos.py` e a caracterização inteira como regressão | `feat:` |
| E10 | 10 | Testes de regressão, cobertura e evidências finais | RNF03 | todos | `docs:` |
| E11 | 11 | Reavaliação de segurança e comparação com a linha de base | RNF06 | não se aplica | `docs:` |
| E12 | 12 | README, documentos finais e apresentação, que mostra os itens mantidos e como seriam corrigidos | | | `docs:` |

Por que nessa ordem:

- Caracterização primeiro (E1). O enunciado pede testes antes de qualquer alteração que possa
  mudar regra de negócio. Eles são a referência para saber se algo mudou.
- Segurança antes de mexer (E2). A linha de base precisa ser do código original, para a
  comparação da E11 fazer sentido.
- Nenhuma etapa muda resultado (E3 a E8). Os testes da E1 não são alterados em nenhum momento.
  Se algum falhar, a refatoração errou. Assim a comparação de antes e depois mostra saídas
  idênticas.
- ReceiptPrinter antes das anotações de tipo (E3 antes da E4). Depois de ir para `src/`, ele
  também recebe as anotações de tipo da E4.
- Combos por último (E9). Entram sobre a estrutura já organizada, sem alterar o código das
  ofertas existentes (RNF04).

## 3. Tratamento dos itens do diagnóstico

| Item | Problema | Tratamento | Etapa |
|---|---|---|---|
| D1 | Um método decide todas as ofertas com condicionais | Cada oferta vira uma classe (Strategy), e uma fábrica escolhe a classe pelo tipo da oferta | E5 e E7 |
| D2 | Mesma oferta espalhada no método | Cada oferta fica inteira na sua classe | E5 |
| D3 | Três fórmulas quase iguais | A fórmula fica na classe base (Template Method). Cada oferta informa só o que muda: tamanho do grupo e preço do grupo | E6 |
| D4 | Carrinho guarda itens e calcula promoções | O cálculo vai para uma classe própria, e o carrinho só guarda os itens | E8 |
| D5 | Teller usa um atributo que só o FakeCatalog tem | Mantido. A caracterização registra o comportamento atual, e a apresentação mostra o defeito e a correção proposta (seção 3.1) | E1 e E12 |
| D6 | `argument` muda de sentido conforme o tipo | Cada classe de oferta dá um nome ao valor que recebe, como percentual ou preço do grupo. `Offer.argument` continua igual | E5 |
| D7 | Nomes que não explicam o conteúdo | Variáveis internas renomeadas (`p`, `x`, `number_of_x`, `discount_n`, `pq`, `price` no Teller). Atributos públicos, como `ReceiptItem.price`, não mudam | E4 |
| D8 | Números mágicos e nome TEN_PERCENT_DISCOUNT | Os números soltos viram constantes com nome. O nome TEN_PERCENT_DISCOUNT é mantido (decisão P2 dos requisitos) e vai para a apresentação (seção 3.1) | E4 e E12 |
| D9 | Nenhuma anotação de tipo | Anotações de tipo nos parâmetros e retornos de `src/` | E4 |
| D10 | Exceção genérica com mensagem repetida | Mantido. A caracterização registra o erro atual, e a apresentação mostra o problema e a correção proposta (seção 3.1) | E1 e E12 |
| D11 | Quase nenhum teste | Caracterização, testes de cada oferta isolada e testes dos combos | E1, E5 e E9 |
| D12 | "2 por valor" cobra a mais com quantidade ímpar | Mantido. A caracterização registra o valor atual, e a apresentação mostra o defeito e a correção proposta (seção 3.1) | E1, E6 e E12 |
| D13 | Fração de peso sai de graça | Mantido. A caracterização registra o valor atual, e a apresentação mostra o defeito e a correção proposta (seção 3.1) | E1, E6 e E12 |
| D14 | ReceiptPrinter na pasta de testes | Movido para `src/` (seção 3.2) | E3 |

### 3.1 Itens mantidos: D5, D8 (nome TEN_PERCENT_DISCOUNT), D10, D12 e D13

Os itens abaixo não são alterados no código. O enunciado manda preservar as regras comerciais
existentes, os cálculos, os valores exibidos no recibo e o contrato observável das interfaces
públicas. Três deles (D5, D12 e D13) fazem o sistema dar um resultado errado. O D10 não muda
resultado, mas a correção mudaria o tipo de erro que o catálogo lança, que faz parte do
comportamento observável. O nome TEN_PERCENT_DISCOUNT, parte do D8, é interface pública:
renomear quebraria o teste original, e um segundo nome para a mesma oferta seria redundante.
A equipe decidiu manter todos como estão. Eles ficam registrados nos testes de caracterização
com o comportamento atual, e a apresentação mostra cada um e como seria corrigido.

A decisão também deixa a comparação de antes e depois mais clara: como nenhum resultado muda,
qualquer diferença nas saídas indica erro da refatoração.

| Item | Comportamento atual, que é mantido | Como seria corrigido |
|---|---|---|
| D5 | `Teller.product_with_name` lê `catalog.products`, que só o FakeCatalog tem. Com o catálogo real, dá `AttributeError` | Acrescentar `product_with_name(name)` ao SupermarketCatalog e ao FakeCatalog, e o Teller chamar esse método |
| D8 | O tipo de oferta TEN_PERCENT_DISCOUNT aceita qualquer percentual, mas o nome diz 10% | Renomear para PERCENT_DISCOUNT. Para não quebrar quem usa o nome antigo, ele ficaria como apelido durante uma transição e depois seria removido |
| D10 | Os dois métodos do SupermarketCatalog lançam `Exception` com a mesma mensagem, e quem chama não consegue diferenciar esse erro de outros | Criar uma exceção própria do catálogo, que herda de `Exception`, com a mensagem em uma constante |
| D12 | Tomate a 0,69 com "2 por 0,99": 3 unidades custam 2,175, mais do que os 2,07 sem oferta, e 5 unidades custam 3,165. Com quantidade ímpar, a unidade que sobra é cobrada duas vezes | Contar só pares inteiros, com divisão inteira (`//`) no lugar da divisão comum (`/`). 3 unidades custariam 1,68 e 5 custariam 2,67 |
| D13 | Maçã a 1,99 o quilo com "leve 3, pague 2": 3,5 kg custam 3,98, o mesmo que 2 kg sem oferta | Cobrar a fração a preço normal. 3,5 kg custariam 4,975 |

Cuidados na refatoração:

- Os testes que registram esses resultados têm nome e comentário indicando que se trata de
  defeito conhecido e mantido. Assim ninguém os "conserta" por engano.
- O D13 acontece igual nas três ofertas por quantidade: os grupos são contados com a parte
  inteira da quantidade, mas o preço sem oferta usa a quantidade completa. A classe base do
  Template Method (E6) repete essa conta, então o resultado não muda.
- O D12 só existe no "2 por valor", que conta os pares com divisão comum. Na E6, essa conta
  fica em um único método da classe do "2 por valor".
- Com isso, a correção de cada defeito, se um dia for feita, fica em um lugar só: a do D12 no
  método da classe do "2 por valor" e a do D13 na classe base.
- Na E4, o `catalog.py` recebe só anotações de tipo. O tipo do erro e a mensagem não mudam
  (D10).

### 3.2 Impressão do recibo: D14

O ReceiptPrinter monta o texto do recibo, que é uma função do sistema, não um teste. Decisão:
mover o arquivo para `src/`. O `pytest.ini` coloca `src` e `tests` no caminho de importação,
então `from receipt_printer import ReceiptPrinter` funciona igual antes e depois. O commit da
E3 só move o arquivo, sem alterar o conteúdo. A partir da E3, o ReceiptPrinter passa a contar
na cobertura de `src/`. A comparação de cobertura entre antes e depois deve levar isso em
conta, porque `src/` passa a ter um arquivo a mais.

Os pontos P1 e P2 estão justificados na seção 8 dos requisitos.

## 4. Riscos e medidas preventivas

Riscos das alterações feitas no sistema durante a modernização, o que é feito para evitar cada
um e como ele é verificado. Se algum acontecer, o retorno segue a seção 5.

| # | Risco | Impacto | Prevenção | Como é verificado |
|---|---|---|---|---|
| R1 | Regressão nas regras existentes: a refatoração muda o valor de um desconto, o total, o texto ou a ordem dos descontos. Exemplo: 3 escovas com "leve 3, pague 2" passarem a custar 2,97 em vez de 1,98 | Alto | Testes de caracterização escritos antes de qualquer mudança (E1). Refatoração em passos pequenos, com todos os testes rodando antes de cada commit | Testes de caracterização, que não são alterados em nenhum momento |
| R2 | Diferença de arredondamento. O computador guarda números decimais de forma aproximada, e a ordem da conta muda o resultado: 0,1 + 0,2 + 0,3 dá 0.6000000000000001, e 0,3 + 0,2 + 0,1 dá 0.6. O recibo impresso arredonda para duas casas, então uma diferença invisível pode virar um centavo: hoje 4,975 aparece como `4.97` e, com outra ordem de conta, poderia aparecer como `4.98` | Médio | Manter nas fórmulas refatoradas a ordem das contas do código original. Comparar valores com `pytest.approx` na tolerância padrão, e não com a tolerância de 1% do teste original (D11) | Testes de caracterização do recibo impresso, que comparam o texto caractere por caractere |
| R3 | Quebra de interface pública: uma classe ou um método usado por outro código muda de nome, de parâmetro ou de retorno, ou um módulo deixa de existir. Exemplo: renomear `checks_out_articles_from` | Alto | Lista de interfaces da seção 8. Classes novas em arquivos novos, sem remover nada dos atuais. `handle_offers` continua existindo e repassa a chamada | Teste original `tests/test_supermarket.py`, sem alteração, e testes de interface na caracterização |
| R4 | Desconto duplicado com combos: um produto com oferta própria ganha também o desconto do combo, ou a mesma unidade entra em dois combos. Exemplo: escova com "leve 3, pague 2" e combo escova + creme dental | Alto | Produto com oferta própria fica fora do combo (RF16). Cada unidade entra em um combo só (RF17) | `tests/test_combos.py`, casos de convivência e de produto em comum |
| R5 | Os combos afetarem o que já existia: a implementação muda o código das ofertas atuais ou o recibo de quem não comprou combo | Alto | Combos em classe própria, sem mexer nas classes das ofertas (RNF04). Desconto de combo calculado só quando há combo cadastrado e depois dos demais descontos | Testes de caracterização passando depois da E9 e diff do commit dos combos |
| R6 | Dependência nova no projeto: uma biblioteca acrescentada para implementar ou testar muda o resultado das auditorias de segurança e contraria a orientação do enunciado | Médio | Usar só o que está no `requirements.txt` original (RNF07). Instalar Bandit, pip-audit e Safety em um ambiente separado, fora do projeto | `requirements.txt` igual ao original e lista de pacotes (`pip freeze`) igual antes e depois |
| R7 | A estrutura nova ficar mais complicada que a antiga: os padrões acrescentam classes, e um padrão sem necessidade deixa o código mais difícil de entender | Médio | Cada classe nova resolve um problema do diagnóstico: Strategy para D1 e D2, Template Method para D3 e a classe de cálculo para D4. A fábrica é documentada como fábrica simples | Testes de cada oferta isolada (RNF05), que só são possíveis com a estrutura nova, e diagrama de classes antes e depois |

## 5. Estratégia de retorno

- Pontos de retorno. Todo commit tem todos os testes passando, então qualquer commit serve de
  ponto de retorno. O commit da E1 marca o código original já coberto pela caracterização.
- Regressão antes do commit. Se um teste falha durante uma mudança, a mudança não é
  registrada. Ela é corrigida ou descartada com `git restore <arquivo>`, que devolve o arquivo
  à versão do último commit.
- Regressão depois do commit. Como os commits são pequenos e os testes rodam antes de cada um,
  o commit que causou o problema costuma ser o último. Se não for, os testes são rodados nos
  commits anteriores até achar o último em que tudo passava. O commit com problema é desfeito
  com `git revert <commit>`, que cria um commit novo com o efeito contrário. O histórico não é
  apagado e nada precisa ser reescrito no GitHub. Não usar `git reset --hard` em commits que já
  foram enviados.
- Combos (E9). O `git revert` do commit dos combos remove a funcionalidade sem mexer nas
  ofertas existentes.
- Depois de qualquer retorno, `pytest -v` é executado de novo para confirmar que tudo voltou a
  passar.

## 6. Critérios de aceitação

### 6.1 Em todo commit

- `pytest -v` passa sem nenhuma falha.
- `tests/test_supermarket.py` não foi alterado (RNF01).
- Os testes de caracterização não foram alterados (RNF02).
- O `requirements.txt` continua igual ao original (RNF07).

### 6.2 Por etapa

| Etapa | Critério | Evidência |
|---|---|---|
| E1 | A caracterização passa sobre o código original, sem mudar `src/`. Cobre carrinho sem oferta; cada oferta abaixo, no limite e acima da quantidade mínima; frações de peso; ordem dos descontos; troca de oferta; recibo impresso; interfaces da seção 8; e o comportamento atual dos itens mantidos (seção 3.1) | Saída do `pytest -v` e cobertura em `docs/evidencias/antes/` |
| E2 | Bandit, pip-audit e Safety executados, com versões, comandos, saídas e limitações registrados | Arquivos em `docs/evidencias/antes/` |
| E3 a E8 | Nenhum teste existente alterado. A cobertura de `src/` não cai em relação à etapa anterior | Saída do `pytest -v` e do `coverage report` |
| E5 a E7 | Cada uma das quatro ofertas tem pelo menos um teste que chama a regra direto, sem criar Teller, ShoppingCart nem Receipt (RNF05) | Testes listados na tabela 7.2 dos requisitos |
| E9 | Os casos da seção 6 dos requisitos e os critérios do RF12 ao RF17 passam. A caracterização passa sem alteração. O diff não altera as classes das ofertas existentes (RNF04) | `tests/test_combos.py` e diff do commit |
| E10 | Todos os testes passam. Cobertura de `src/` acima de 90% (RNF03). Tabela 7.2 dos requisitos preenchida | `docs/evidencias/depois/` |
| E11 | As três ferramentas executadas de novo, cada alerta comparado com a linha de base e analisado | `docs/evidencias/depois/` |
| E12 | README com os itens pedidos no enunciado (item 5.9). Apresentação com os itens mantidos (seção 3.1) e a correção proposta para cada um | README, `docs/` e apresentação |

## 7. Invariantes de negócio

Comportamentos que não podem mudar. Entre parênteses, o requisito correspondente.

1. O total do recibo é a soma dos itens mais a soma dos descontos, que são negativos (RF03).
2. Cada adição ao carrinho vira uma linha do recibo, na ordem em que entrou, com quantidade,
   preço unitário e total da linha (RF01, RF02 e decisão P1).
3. As ofertas são calculadas sobre a quantidade total de cada produto (RF01).
4. Só há desconto para produto que está no carrinho e tem oferta (RF04). Quando a quantidade
   não atinge o mínimo da oferta, nenhuma linha de desconto é criada.
5. Cada produto tem uma oferta só, e cadastrar outra substitui a anterior (RF05).
6. Os textos dos descontos não mudam: `3 for 2`; o percentual cadastrado seguido de `% off`;
   `2 for` e `5 for` seguidos do valor cadastrado (RF06 a RF09).
7. Os valores dos descontos ficam iguais aos da caracterização, inclusive nos defeitos D12 e
   D13 (RNF02).
8. Os descontos aparecem na ordem em que os produtos entraram no carrinho, e os de combo vêm
   depois (RF11).
9. O texto do recibo impresso pelo ReceiptPrinter fica igual, caractere por caractere (RNF02).
10. `Teller.product_with_name` mantém o comportamento atual: devolve o produto quando o
    catálogo é o FakeCatalog e dá erro com o catálogo real (D5).
11. Os métodos do SupermarketCatalog continuam lançando `Exception` com a mesma mensagem
    (D10).

## 8. Interfaces que devem permanecer compatíveis

A lista completa de classes e métodos públicos está na seção 5.1 dos requisitos (RNF01). Além
dela:

- Os módulos `model_objects`, `shopping_cart`, `teller`, `receipt` e `catalog` continuam
  existindo e oferecendo as mesmas classes, porque os testes importam as classes pelo nome do
  módulo.
- O FakeCatalog continua em `tests/fake_catalog.py`, porque o teste original o importa com
  `from tests.fake_catalog import FakeCatalog`.
- `ShoppingCart.handle_offers(receipt, offers, catalog)` continua funcionando quando chamado
  diretamente, mesmo depois que o cálculo sair do carrinho (E8).
- O ReceiptPrinter continua importável com `from receipt_printer import ReceiptPrinter` depois
  de ir para `src/` (E3).

Acréscimos previstos. Nenhum deles remove ou altera o que já existe:

| Onde | Acréscimo | Etapa |
|---|---|---|
| `src/` | classes novas das ofertas, da fábrica e do cálculo dos descontos | E5 a E8 |
| Teller | método para cadastrar combo | E9 |
