# Lições aprendidas

Projeto: Supermarket Receipt, versão python_pytest.
Base: todos os documentos de `docs/` e o histórico de commits da branch `modernizacao`.
Data: 25/11/2026.

## 1. Objetivo

Este documento registra a reflexão da equipe sobre o processo de modernização: o que funcionou,
as decisões relevantes e por que foram tomadas, as decisões que mudaram no caminho e as
limitações que continuam. Atende à linha "Lições aprendidas" da seção 6 do enunciado (MPS.BR).

## 2. O que funcionou

### 2.1 Testes de caracterização antes de mexer no código

Os 40 testes de caracterização foram escritos e executados sobre o código original antes de
qualquer mudança em `src/`. Eles registram o que o sistema faz, e não o que deveria fazer,
inclusive nos defeitos. Foram eles que permitiram refatorar com segurança: em cada etapa, se um
deles falhasse, a refatoração tinha mudado um comportamento. Nenhum deles foi alterado do
começo ao fim do trabalho.

Os testes também transformaram os defeitos encontrados no diagnóstico em valores concretos.
Cada item mantido tem um teste com nome e comentário dizendo que é defeito conhecido, para
ninguém "consertá-lo" por engano durante a refatoração.

### 2.2 Commits pequenos, com testes e cobertura conferidos antes de cada um

Cada etapa da refatoração (E3 a E9) foi feita em um ou poucos commits, e nenhum commit entrou sem
todos os testes passando e sem a cobertura de `src/` em 100%. Isso deixou o histórico legível,
com uma mudança por commit, e fez de qualquer commit um ponto de retorno seguro (plano de
contingência, seção 5).

Na E7, os testes da fábrica entraram no mesmo commit do código. Sem eles, a linha que devolve
`None` para tipo de oferta desconhecido ficaria sem teste, e a cobertura cairia para 99%. O
critério de cobertura forçou a equipe a testar um caso que seria esquecido.

### 2.3 Cuidado com arredondamento

O computador guarda números decimais de forma aproximada, e a ordem das contas muda o resultado
(risco R2 do plano). Na E6, as classes do Template Method foram comparadas com as da E5 em 8.448
casos, exigindo o mesmo número até a última casa, e não houve diferença. Manter nas fórmulas
novas a ordem das contas do código original foi o que garantiu isso.

### 2.4 Padrões escolhidos pelo problema, não pela lista

Cada padrão foi aplicado para resolver um item do diagnóstico: Strategy para D1, D2 e D6;
Template Method para D3. O enunciado cita Factory Method como exemplo, mas o que o problema pedia
era só tirar do carrinho a escolha da classe da oferta. Uma fábrica simples, com uma tabela,
resolve isso. Aplicar o Factory Method do catálogo, com uma hierarquia de criadores, acrescentaria
classes sem resolver nenhum problema a mais (risco R7). Por isso a fábrica é documentada como
fábrica simples, e os dois padrões que contam são o Strategy e o Template Method.

### 2.5 A promoção nova sobre a estrutura já organizada

Os combos foram a última etapa (E9). Como as ofertas já estavam separadas em classes, os combos
entraram em classes próprias (`Bundle` e `BundleCalculator`), sem alterar nenhum arquivo das
ofertas. O diff do commit `89f6a53` é a prova do RNF04.

## 3. Decisões relevantes

### 3.1 Manter os defeitos

A equipe decidiu manter os itens D5, D8 (nome TEN_PERCENT_DISCOUNT), D10, D12 e D13 como estão
no código original (plano de contingência, seção 3.1). Os motivos:

- o enunciado manda preservar as regras comerciais existentes, os cálculos e os valores exibidos
  no recibo, e penaliza a quebra injustificada de regra;
- com nenhum resultado mudando, a comparação de antes e depois mostra saídas idênticas, e
  qualquer diferença indica erro da refatoração.

O custo é que o sistema continua cobrando errado em dois casos: 3 tomates com "2 por 0,99" saem
por 2,175, mais do que sem oferta (D12), e a fração de peso sai de graça nas ofertas por
quantidade (D13). A equipe considerou esse custo aceitável porque os defeitos estão registrados
nos testes, documentados com a correção proposta e, depois da refatoração, isolados num lugar
só: o D12 num método da `TwoForAmountStrategy` e o D13 numa linha da classe base.

### 3.2 Regras dos combos

O enunciado não definia a convivência dos combos com as ofertas nem combos com produto em comum.
A equipe escolheu regras que dependem só do cadastro, simples de prever e de testar: produto
com oferta própria não entra em combo (RF16), e cada unidade entra num combo só, na ordem de
cadastro (RF17). As alternativas, liberar para o combo as unidades que a oferta não usou e
escolher o combo de maior desconto, foram descartadas por deixar a regra mais difícil de prever
(requisitos, seção 4).

## 4. Decisões que mudaram no caminho

| Decisão inicial | Decisão final | Por que mudou | Onde ficou registrado |
|---|---|---|---|
| Acrescentar `PERCENT_DISCOUNT` como apelido de `TEN_PERCENT_DISCOUNT` | Manter só o nome original, sem apelido | Dois nomes para a mesma oferta seriam redundantes, e renomear quebraria o teste original (RNF01) | Requisitos, P2; commit `ef527b3` |
| Corrigir o D12 (contar só pares inteiros) e o D13 (cobrar a fração de peso) | Manter os dois defeitos | Preservar os valores do recibo, como pede o enunciado, e permitir a comparação de saídas idênticas | Requisitos, P3; plano, seção 3.1; commit `ef527b3` |

As decisões foram tomadas na revisão de 25/11/2026 e registradas nos documentos antes de qualquer
mudança no código. Assim, o código nunca precisou ser desfeito por causa delas.

## 5. Ferramentas de segurança

- As ferramentas (Bandit, pip-audit e Safety) foram instaladas num ambiente separado, fora da
  venv do projeto. Assim elas não entram na lista de bibliotecas auditadas nem mudam o
  `requirements.txt` (RNF07).
- O comando novo do Safety, `scan`, exige conta no serviço. A equipe registrou a tentativa e usou
  o comando antigo, `check`, que funciona sem conta mas está descontinuado. A lição é que uma
  ferramenta de segurança também é uma dependência, que pode mudar ou deixar de funcionar.
- O PowerShell grava os arquivos de saída em outra codificação. As evidências foram geradas no
  terminal cmd, para que os arquivos ficassem legíveis no GitHub.

## 6. Limitações que continuam

- O `requirements.txt` não fixa versões. Uma instalação nova pode trazer versões diferentes das
  24 bibliotecas analisadas. Fixar versões e hashes foi deixado como recomendação, porque o
  RNF07 pede o `requirements.txt` igual ao original.
- A ausência de alertas não prova que o sistema é seguro. As ferramentas não entendem a regra de
  negócio: os defeitos D12 e D13 foram encontrados na leitura do código, não por ferramenta.
- Os defeitos D5, D12 e D13 continuam fazendo o sistema dar resultado errado. A correção de cada
  um está descrita no plano de contingência, seção 3.1.
- Não dá para cadastrar um combo com duas unidades do mesmo produto, como "2 escovas + 1 creme
  dental". O RF12 recusa produto repetido.
- O código passou de 5 para 10 arquivos em `src/`. A estrutura é maior, embora cada parte seja
  menor e testável sozinha.

## 7. O que a equipe faria diferente

- Decidir antes de escrever os requisitos se os defeitos seriam corrigidos ou mantidos. A troca
  de decisão no caminho obrigou a reescrever o RF07, o RF08, o RF10 e a rastreabilidade.
