# Análise de segurança antes e depois

Projeto: Supermarket Receipt, versão python_pytest.
Evidências: `docs/evidencias/antes/` (linha de base, etapa E2 do plano de contingência) e
`docs/evidencias/depois/` (reavaliação, etapa E11).
Data: 25/11/2026.

## 1. Objetivo

Este relatório registra a análise de segurança feita com Bandit, pip-audit e Safety antes e
depois da modernização: versões, escopo e comandos, resultados, triagem de cada mensagem das
ferramentas, ações tomadas, o que não foi corrigido e por quê, comparação entre antes e depois e
as limitações encontradas (item 5.8 do enunciado).

## 2. Ferramentas, versões e ambiente

| Ferramenta | Versão | O que analisa | Escopo neste trabalho |
|---|---|---|---|
| Bandit | 1.9.4 | o código Python, procurando padrões inseguros conhecidos, como senha escrita no código, uso de `eval` ou comando do sistema montado com texto de fora | a pasta `src/`, que é o código do sistema |
| pip-audit | 2.10.1 | as bibliotecas usadas pelo projeto, comparando cada versão com uma base pública de vulnerabilidades conhecidas | as 24 bibliotecas instaladas na venv do projeto |
| Safety | 3.8.1 | as mesmas bibliotecas, com a base de vulnerabilidades da empresa Safety | as mesmas 24 bibliotecas |

Ambiente: Windows 10 (versão 10.0.19045.6466) e Python 3.11.5.

As três ferramentas foram instaladas num ambiente virtual separado, fora do repositório, em
`D:\faculdade\alta-qualidade-av3\venv-ferramentas`. Elas trazem dezenas de bibliotecas próprias.
Se fossem instaladas na venv do projeto, o pip-audit e o Safety analisariam também essas
bibliotecas, e o resultado deixaria de ser só do projeto. As mesmas versões foram usadas antes e
depois, para a comparação ser justa.

A lista exata das bibliotecas do projeto foi gravada com `pip freeze` em
`dependencias_projeto.txt`, nas pastas `antes` e `depois`. As duas listas são iguais.

Os testes ficaram fora da análise do Bandit. Eles usam `assert` o tempo todo, e o Bandit aponta
cada `assert` como alerta, porque em código de produção ele pode ser desligado. Em teste, esse
uso é o normal e não afeta o sistema.

## 3. Comandos

Os mesmos comandos foram usados antes e depois, trocando só a pasta das evidências:

```
python -m pip freeze > docs\evidencias\antes\dependencias_projeto.txt
bandit --version
bandit -r src
pip-audit --version
pip-audit -r docs\evidencias\antes\dependencias_projeto.txt --no-deps
set PYTHONIOENCODING=utf-8
set NO_COLOR=1
safety --version
safety check -r docs\evidencias\antes\dependencias_projeto.txt
safety scan --target . < NUL
```

- `--no-deps` diz ao pip-audit que a lista já está completa, com as versões exatas. Sem essa
  opção, ele montaria um ambiente temporário para descobrir as dependências e poderia pegar
  versões diferentes das que o projeto usa.
- `PYTHONIOENCODING` e `NO_COLOR` evitam que o Safety pare com erro de codificação ao gravar o
  arquivo ou grave códigos de cor no meio do texto. Mesmo assim, ele gravou códigos de cor, que
  foram removidos das evidências sem mudar o texto, como anotado no cabeçalho delas.
- `< NUL` entrega uma entrada vazia para a pergunta de login do `safety scan` (seção 6).

## 4. Resultados

| Ferramenta | Antes | Depois | Evidências |
|---|---|---|---|
| Bandit | 133 linhas analisadas, nenhum problema | 319 linhas analisadas, nenhum problema | `antes/05_bandit.txt` e `depois/05_bandit.txt` |
| pip-audit | 24 bibliotecas, nenhuma vulnerabilidade conhecida, 2 avisos sobre hashes | igual | `antes/06_pip_audit.txt` e `depois/06_pip_audit.txt` |
| Safety, comando `check` | 24 bibliotecas, nenhuma vulnerabilidade, aviso de comando descontinuado | igual | `antes/07_safety.txt` e `depois/07_safety.txt` |
| Safety, comando `scan` | não rodou: exige conta | não rodou: exige conta | `antes/07_safety.txt` e `depois/07_safety.txt` |

O código de `src/` mais que dobrou com a modernização, de 133 para 319 linhas (ofertas, fábrica,
calculadoras e combos), e o Bandit continuou sem nenhum alerta. As bibliotecas do projeto não mudaram, então o resultado
do pip-audit e do Safety também não mudou.

## 5. Triagem das mensagens

Nenhuma ferramenta apontou vulnerabilidade. Mesmo assim, elas mostraram mensagens que precisam
ser entendidas, porque nem toda mensagem de ferramenta de segurança é uma vulnerabilidade.

| Mensagem | Ferramenta | Classificação | Relevância para o projeto | Ação |
|---|---|---|---|---|
| "--no-deps is supported, but users are encouraged to fully hash their pinned dependencies" e a sugestão de usar `pip-compile` | pip-audit | recomendação de boa prática, não é vulnerabilidade | baixa. Hashes são impressões digitais dos arquivos das bibliotecas e garantem que o arquivo instalado é exatamente o publicado. Protegem contra um pacote adulterado durante a instalação | não corrigido (seção 7) |
| "this command (`check`) has been DEPRECATED" | Safety | aviso de que o comando vai deixar de existir | não afeta o projeto. Afeta a ferramenta: o comando pode parar de funcionar numa análise futura | registrado como limitação (seção 6) |
| `AuthlibDeprecationWarning` sobre `authlib.jose` e `httpx` | Safety | aviso interno de bibliotecas usadas pelo próprio Safety | nenhuma. São bibliotecas do ambiente das ferramentas, não do projeto | nenhuma |
| "Please login or register Safety CLI" e "EOF when reading a line" | Safety | limitação de acesso | o `scan` não analisou nada. As bibliotecas foram verificadas pelo pip-audit e pelo `safety check` | tentativa registrada (seção 6) |

## 6. Limitação de acesso do Safety

O Safety tem dois comandos para analisar dependências. O `check`, antigo, funciona sem conta e foi
o que gerou o resultado. O `scan`, novo, exige uma conta gratuita no serviço da empresa Safety.
Sem login, ele pergunta se a pessoa quer se registrar ou entrar e espera a resposta.

Para registrar a limitação, o `scan` foi executado com entrada vazia (`< NUL`). Ele mostrou a
pergunta de login e parou com "EOF when reading a line". Essa saída está nas evidências 07, antes
e depois, como o item 5.8 do enunciado pede para o caso de a ferramenta exigir conta.

A equipe não criou conta no serviço, porque o enunciado aceita a evidência da tentativa e as
bibliotecas já foram verificadas por duas ferramentas. Se a conta for criada, o `scan` pode ser
repetido antes e depois e este relatório atualizado.

## 7. Correções e itens não corrigidos

Nenhuma correção de segurança foi necessária, porque nenhuma ferramenta apontou vulnerabilidade,
nem antes nem depois.

A modernização também não piorou o quadro:

- nenhuma biblioteca foi acrescentada ao projeto (RNF07). A lista de antes e a de depois são
  iguais;
- as ferramentas de segurança ficaram fora do ambiente do projeto;
- o código novo usa só a biblioteca padrão do Python, sem acesso a arquivos, rede, banco de dados
  ou comandos do sistema.

Item não corrigido: o uso de hashes recomendado pelo pip-audit. Adotar essa prática exigiria
mudar o `requirements.txt`, fixando versões e hashes, e provavelmente usar uma ferramenta nova
para gerá-los. O RNF07 pede o `requirements.txt` igual ao original, e o enunciado orienta evitar
dependências desnecessárias. Além disso, o código do sistema não usa nenhuma das 24 bibliotecas:
todas são ferramentas de teste (pytest, coverage, approvaltests e as dependências delas). Fica
registrado como recomendação para o futuro.

## 8. Riscos remanescentes

A ausência de alertas não prova que o sistema é seguro. Cada ferramenta tem um alcance limitado:

- o Bandit procura padrões conhecidos no código. Ele não entende a regra de negócio. Por exemplo,
  os defeitos de cálculo D12 e D13, mantidos por decisão da equipe, não são detectados por
  ferramenta de segurança: foram encontrados na leitura do código e registrados nos testes de
  caracterização;
- o pip-audit e o Safety só conhecem vulnerabilidades já publicadas nas suas bases. Uma falha
  descoberta depois da análise não aparece;
- o `requirements.txt` não fixa versões. Uma instalação nova pode trazer versões diferentes das
  24 analisadas, e essas versões precisariam ser auditadas de novo;
- o `safety check` está descontinuado e pode parar de funcionar, o que afeta a repetição desta
  análise no futuro.

## 9. Conclusão

Antes e depois da modernização, o Bandit não apontou nenhum problema no código, e o pip-audit e o
Safety não encontraram vulnerabilidade nas 24 bibliotecas do projeto. A modernização mais
que dobrou o código de `src/` sem trazer alertas e sem acrescentar bibliotecas. As mensagens das
ferramentas foram analisadas: nenhuma é vulnerabilidade do projeto. A limitação do `safety scan`,
que exige conta, foi registrada com a evidência da tentativa.
