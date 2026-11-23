# Comparativo antes e depois

Todos os números abaixo saem dos arquivos das pastas `antes/` e `depois/`,
gerados pelo mesmo script (`scripts/gerar_evidencias.py`), no mesmo ambiente
(Windows 10, Python 3.11.5). As versões das ferramentas estão em `00_ambiente.txt`.

- **Antes:** código original do repositório-base (commit `c72d68a`).
- **Depois:** código refatorado, com a correção do "2 por valor" e os combos.

## Testes

| Item | Antes | Depois | Arquivo |
|---|---|---|---|
| Testes automatizados | 1 | 94 | `01_pytest.txt` |
| Testes que passam | 1 | 94 | `01_pytest.txt` |
| Cobertura de `src/` | 71% | 100% | `02_cobertura.txt` |
| Cobertura de `shopping_cart.py` | 41% | 100% | `02_cobertura.txt` |

Os 94 testes se dividem assim: 45 de comportamento legado, 27 de combos,
21 das estratégias, da fábrica e da calculadora, e 1 teste original do repositório.

### Preservação do comportamento

O arquivo `antes/06_caracterizacao_no_legado.txt` mostra os testes de
caracterização rodando **sobre o código original**: 46 testes, todos passando,
com 100% de cobertura. Os mesmos testes continuam passando no código
refatorado. A única diferença são 3 casos da oferta "2 por valor" com
quantidade ímpar, alterados de propósito no commit da correção (ver
`docs/decisoes_tecnicas.md`, seção 7).

## Segurança

| Ferramenta | Antes | Depois | Arquivo |
|---|---|---|---|
| Bandit (`src/`) | 0 alertas em 133 linhas | 0 alertas em 306 linhas | `03_bandit.txt` |
| pip-audit | 0 vulnerabilidades em 24 pacotes | 0 vulnerabilidades em 24 pacotes | `04_pip_audit.txt` |
| Safety (`check`) | 0 vulnerabilidades em 24 pacotes | 0 vulnerabilidades em 24 pacotes | `05_safety.txt` |
| Safety (`scan`) | exige login, não executado | exige login, não executado | `05_safety.txt` |

As dependências do projeto não mudaram entre o antes e o depois: nenhuma
biblioteca foi adicionada ao `requirements.txt`. A lista exata auditada está em
`dependencias_instaladas.txt`, em cada pasta.

Ausência de alertas não prova que o sistema é seguro. O Bandit procura padrões
de código perigosos (por exemplo `eval`, senhas fixas, comandos de sistema), e
este projeto é só cálculo em memória, sem rede, arquivos ou banco de dados. O
pip-audit e o Safety conferem apenas vulnerabilidades já publicadas para as
versões instaladas.
