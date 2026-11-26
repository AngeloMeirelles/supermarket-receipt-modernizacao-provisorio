# Evidências de testes

Projeto: Supermarket Receipt, versão python_pytest.
Base: arquivos de `docs/evidencias/antes/` e `docs/evidencias/depois/`.
Data: 25/11/2026.

## 1. Objetivo

Este documento reúne as evidências de testes da modernização num lugar só, para quem avalia não
precisar abrir vários arquivos `.txt`. Ele mostra a evolução dos testes e da cobertura, a prova
de que o comportamento do código original foi preservado e os cenários de fronteira cobertos.
Os logs completos continuam nos arquivos de evidência (índice na seção 7). Nada foi executado de
novo para este documento: todos os números vêm desses arquivos.

## 2. Antes e depois

| Momento | Código | Testes | Resultado | Cobertura de `src/` | Evidência |
|---|---|---|---|---|---|
| Código original | commit `c72d68a` | 1 (o teste original do kata) | 1 passou | 71% (129 linhas, 37 sem teste) | `antes/01_pytest.txt`, `antes/02_cobertura.txt` |
| Com a caracterização (E1) | commit `c72d68a`, sem nenhuma mudança em `src/` | 41 (40 de caracterização + o original) | 41 passaram | 100% (129 linhas) | `antes/03_caracterizacao_pytest.txt`, `antes/04_caracterizacao_cobertura.txt` |
| Final | branch `modernizacao`, commits `0b70856` e `b968277` | 100 | 100 passaram | 100% (263 linhas) | `depois/01_pytest.txt`, `depois/02_cobertura.txt` |

A meta da equipe era ficar acima de 90% de cobertura (RNF03). O enunciado não fixa um
percentual.

No final, a cobertura (`depois/02_cobertura.txt`) foi medida no commit `0b70856`, que retirou os
comentários e as docstrings do código, e a execução dos testes (`depois/01_pytest.txt`) no commit
`b968277`, que traduziu para o inglês os nomes dos testes novos. O código de `src/` é o mesmo
nos dois commits.

### 2.1 Cobertura por arquivo

No código original, só com o teste original:

| Arquivo | Linhas | Sem teste | Cobertura |
|---|---|---|---|
| `catalog.py` | 5 | 2 | 60% |
| `model_objects.py` | 27 | 3 | 89% |
| `receipt.py` | 27 | 2 | 93% |
| `shopping_cart.py` | 49 | 29 | 41% |
| `teller.py` | 21 | 1 | 95% |
| **Total** | **129** | **37** | **71%** |

O `shopping_cart.py`, onde ficava todo o cálculo das ofertas, tinha 41% de cobertura: as linhas
34 a 68, que calculam os descontos, não eram executadas por nenhum teste (D11).

No código final:

| Arquivo | Linhas | Sem teste | Cobertura |
|---|---|---|---|
| `bundle_calculator.py` | 20 | 0 | 100% |
| `catalog.py` | 6 | 0 | 100% |
| `discount_calculator.py` | 17 | 0 | 100% |
| `model_objects.py` | 32 | 0 | 100% |
| `offer_strategies.py` | 51 | 0 | 100% |
| `offer_strategy_factory.py` | 11 | 0 | 100% |
| `receipt.py` | 28 | 0 | 100% |
| `receipt_printer.py` | 45 | 0 | 100% |
| `shopping_cart.py` | 24 | 0 | 100% |
| `teller.py` | 29 | 0 | 100% |
| **Total** | **263** | **0** | **100%** |

O `receipt_printer.py` passou a contar na cobertura de `src/` na E3, quando saiu da pasta de
testes (D14). Por isso o total de linhas não é comparável diretamente entre antes e depois.
O total final era de 271 linhas até a retirada dos comentários e das docstrings (commit
`0b70856`). Com essa retirada, os 4 métodos abstratos passaram a ter só `...` no corpo, e a
ferramenta de cobertura deixa de contar esses métodos por padrão, com 2 linhas cada: no
`offer_strategies.py`, o total passou de 59 para 51 linhas.

### 2.2 Testes por arquivo no final

| Arquivo | Testes | O que verifica |
|---|---|---|
| `tests/test_supermarket.py` | 1 | O teste original do kata, sem alteração |
| `tests/test_comportamento_legado.py` | 40 | Caracterização do código original, sem alteração desde que foi escrita |
| `tests/test_offer_strategies.py` | 27 | Cada oferta isolada e a classe base das ofertas por quantidade |
| `tests/test_offer_strategy_factory.py` | 8 | A fábrica de estratégias |
| `tests/test_discount_calculator.py` | 6 | A calculadora de descontos |
| `tests/test_combos.py` | 18 | Os combos promocionais |
| **Total** | **100** | |

A evolução etapa por etapa (41, 60, 68, 76, 82 e 100 testes, sempre com 100% de cobertura) está
na seção 3 do registro da refatoração.

## 3. Mesmo ambiente antes e depois

| Item | Antes | Depois |
|---|---|---|
| Sistema | Windows 10 | Windows 10 |
| Python | 3.11.5 | 3.11.5 |
| pytest | 9.2.0 | 9.2.0 |
| Bibliotecas na venv | 24 | as mesmas 24, nas mesmas versões |
| `requirements.txt` | original do kata | igual ao original (RNF07) |

Evidências: `antes/00_ambiente.txt`, `depois/00_ambiente.txt` e os dois arquivos
`dependencias_projeto.txt`, que são idênticos. A mesma venv foi usada nas duas medições, sem
nenhuma instalação nova.

## 4. Preservação do comportamento

A prova de que a modernização não mudou nenhum resultado está em três pontos:

1. Os 40 testes de caracterização foram escritos e executados sobre o código original, antes de
   qualquer mudança em `src/` (`antes/03_caracterizacao_pytest.txt`, 41 testes passando). O
   valor esperado de cada teste é o que o código original devolve, inclusive nos itens mantidos
   D5, D8, D10, D12 e D13.
2. Esses mesmos 40 testes passaram no código final (`depois/01_pytest.txt`) sem nenhuma
   alteração. O arquivo `tests/test_comportamento_legado.py` é idêntico ao do commit `60f645f`,
   em que foi criado. Isso pode ser conferido com:

   ```
   git diff 60f645f HEAD -- python_pytest/tests/test_comportamento_legado.py
   ```

3. O teste original `tests/test_supermarket.py` também não foi alterado em relação ao commit
   `c72d68a` (RNF01).

Os testes de caracterização também passaram em cada commit intermediário, que é o critério de
aceitação da seção 6.1 do plano de contingência. Como nenhum resultado podia mudar, qualquer
falha indicaria erro da refatoração.

Os testes de caracterização comparam valores com `pytest.approx` na tolerância padrão, e o
recibo impresso é comparado caractere por caractere. Isso cobre o risco R2 do plano
(arredondamento de números decimais).

## 5. Cenários de fronteira cobertos

| Cenário | Exemplo verificado | Arquivo de teste |
|---|---|---|
| Carrinho vazio | recibo sem itens e total 0; recibo impresso vazio | `test_comportamento_legado.py` |
| Leve 3, pague 2 abaixo, no limite e acima do mínimo | 2 escovas sem desconto; 3 escovas com -0,99; 7 escovas | `test_comportamento_legado.py`, `test_offer_strategies.py` |
| 2 por valor com quantidade 1, par e ímpar | 1 caixa sem desconto; 2 e 4 caixas; 3 e 5 caixas com o defeito D12 (2,175 e 3,165) | `test_comportamento_legado.py`, `test_offer_strategies.py` |
| 5 por valor abaixo, no limite e acima do mínimo | 4, 5 e 6 unidades | `test_comportamento_legado.py`, `test_offer_strategies.py` |
| Desconto percentual com qualquer percentual | 10% e 20%, inclusive sobre fração de peso (D8) | `test_comportamento_legado.py`, `test_offer_strategy_factory.py` |
| Frações de peso | fração que não completa grupo; 3,5 kg de maçã com o defeito D13 | `test_comportamento_legado.py`, `test_offer_strategies.py` |
| Mesmo produto em mais de uma linha | duas linhas no recibo e oferta sobre a quantidade somada (P1) | `test_comportamento_legado.py` |
| Oferta de produto fora do carrinho e troca de oferta | nenhum desconto; a última oferta cadastrada vale | `test_comportamento_legado.py`, `test_discount_calculator.py` |
| Ordem dos descontos | na ordem dos produtos no carrinho; combos por último | `test_comportamento_legado.py`, `test_combos.py` |
| Tipo de oferta desconhecido | a fábrica devolve `None` e não há desconto | `test_offer_strategy_factory.py`, `test_discount_calculator.py` |
| Combo completo, incompleto, repetido e excedente | 22,50; 10,00; 45,00; 32,50 | `test_combos.py` |
| Cadastro de combo inválido | lista vazia, um produto só e produto repetido são recusados | `test_combos.py` |
| Combo com produto por peso | 1,5 kg forma combo sobre 1 kg (11,80); 0,5 kg não forma (11,00) | `test_combos.py` |
| Combos com produto em comum | com 1 escova, só o primeiro combo (27,50); com 2, os dois (36,00) | `test_combos.py` |
| Convivência de combo com oferta | 3 escovas com "leve 3, pague 2" e 1 creme dental: só a oferta (35,00); 1 escova: nenhum desconto (25,00) | `test_combos.py` |
| Interfaces públicas | `handle_offers` chamado direto, recibo montado direto, cópias das listas do recibo | `test_comportamento_legado.py` |
| Itens mantidos | `product_with_name` com o catálogo real (D5); `Exception` genérica do catálogo (D10) | `test_comportamento_legado.py` |

A ligação de cada requisito ao teste que o verifica está na seção 7.2 dos requisitos.

## 6. Como reproduzir

Na pasta `python_pytest`, com a venv do projeto ativa (passo a passo no README):

```
pytest -v
coverage run --source=src -m pytest
coverage report -m
```

Para rodar a caracterização sobre o código original:

```
git checkout 60f645f
pytest -v
git checkout modernizacao
```

## 7. Índice dos arquivos de evidência

Todos em `docs/evidencias/`. Cada arquivo começa com um cabeçalho que diz o código usado, os
comandos executados e, nos de depois, a comparação com o arquivo de antes.

| Arquivo | Conteúdo |
|---|---|
| `antes/00_ambiente.txt` | Sistema, versão do Python e bibliotecas da venv no código original |
| `antes/01_pytest.txt` | `pytest -v` no código original, só com o teste original: 1 teste |
| `antes/02_cobertura.txt` | Cobertura do código original só com o teste original: 71% |
| `antes/03_caracterizacao_pytest.txt` | `pytest -v` no código original com a caracterização: 41 testes |
| `antes/04_caracterizacao_cobertura.txt` | Cobertura do código original com a caracterização: 100% |
| `antes/05_bandit.txt` | Bandit no código original |
| `antes/06_pip_audit.txt` | pip-audit nas dependências do código original |
| `antes/07_safety.txt` | Safety nas dependências do código original |
| `antes/dependencias_projeto.txt` | `pip freeze` da venv do projeto |
| `depois/00_ambiente.txt` | Sistema, Python e bibliotecas no código final: os mesmos de antes |
| `depois/01_pytest.txt` | `pytest -v` no código final: 100 testes |
| `depois/02_cobertura.txt` | Cobertura do código final: 100% |
| `depois/05_bandit.txt` | Bandit no código final |
| `depois/06_pip_audit.txt` | pip-audit nas dependências do código final |
| `depois/07_safety.txt` | Safety nas dependências do código final |
| `depois/dependencias_projeto.txt` | `pip freeze` da venv do projeto, igual ao de antes |

Os arquivos 05 a 07 são analisados no relatório de segurança (`docs/seguranca_antes_depois.md`).
