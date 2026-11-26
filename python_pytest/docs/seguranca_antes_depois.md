
# Análise de segurança antes e depois

Projeto: Supermarket Receipt, versão python_pytest.

## 1. Objetivo

Este relatório registra a análise de segurança realizada com Bandit, pip-audit e Safety antes e depois da modernização. São apresentados as versões das ferramentas, o escopo e os comandos utilizados, os resultados, a triagem de cada mensagem, as ações tomadas, os itens não corrigidos e suas justificativas, a comparação entre antes e depois e as limitações encontradas (item 5.8 do enunciado).

## 2. Ferramentas, versões e ambiente

| Ferramenta | Versão | O que analisa | Escopo neste trabalho |
|---|---|---|---|
| Bandit | 1.9.4 | O código Python, procurando padrões inseguros conhecidos, como senhas escritas no código, uso de `eval` ou comandos do sistema montados com texto externo. | A pasta `src/`, que contém o código do sistema. |
| pip-audit | 2.10.1 | As bibliotecas usadas pelo projeto, comparando cada versão com uma base pública de vulnerabilidades conhecidas. | As 24 bibliotecas instaladas na venv do projeto. |
| Safety | 3.8.1 | As mesmas bibliotecas, usando a base de vulnerabilidades da empresa Safety. | As mesmas 24 bibliotecas. |

Ambiente: Windows 10 (versão 10.0.19045.6466) e Python 3.11.5.

As três ferramentas foram instaladas em um ambiente virtual separado, fora do repositório, em `D:\faculdade\alta-qualidade-av3\venv-ferramentas`. Elas possuem dezenas de bibliotecas próprias. Se fossem instaladas na venv do projeto, o pip-audit e o Safety também analisariam essas bibliotecas, e o resultado deixaria de representar apenas as dependências do projeto. As mesmas versões foram usadas antes e depois para garantir uma comparação consistente.

A lista exata das bibliotecas do projeto foi gerada com `pip freeze` e gravada em `dependencias_projeto.txt`, nas pastas `antes` e `depois`. As duas listas são iguais.

Os testes ficaram fora da análise do Bandit. Eles usam `assert` frequentemente, e o Bandit aponta cada `assert` como alerta porque, em código de produção, ele pode ser desligado. Nos testes, esse uso é normal e não afeta o funcionamento do sistema.

## 3. Comandos

Os mesmos comandos foram utilizados antes e depois, alterando apenas a pasta de destino das evidências:

```powershell
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

- `--no-deps` informa ao pip-audit que a lista já contém todas as dependências, com suas versões exatas. Sem essa opção, ele criaria um ambiente temporário para descobrir as dependências e poderia obter versões diferentes das utilizadas pelo projeto.
- `PYTHONIOENCODING` e `NO_COLOR` foram definidos para evitar que o Safety apresentasse erro de codificação ao gravar o arquivo ou inserisse códigos de cor no texto. Mesmo assim, foram gravados códigos de cor, que foram removidos das evidências sem alterar o conteúdo, conforme anotado nos cabeçalhos dos arquivos.
- `< NUL` fornece uma entrada vazia para a solicitação de login do comando `safety scan` (seção 6).

## 4. Resultados

| Ferramenta | Antes | Depois | Evidências |
|---|---|---|---|
| Bandit | 133 linhas analisadas, nenhum problema | 319 linhas analisadas, nenhum problema | `antes/05_bandit.txt` e `depois/05_bandit.txt` |
| pip-audit | 24 bibliotecas, nenhuma vulnerabilidade conhecida, 2 avisos sobre hashes | Igual | `antes/06_pip_audit.txt` e `depois/06_pip_audit.txt` |
| Safety, comando `check` | 24 bibliotecas, nenhuma vulnerabilidade, aviso de comando descontinuado | Igual | `antes/07_safety.txt` e `depois/07_safety.txt` |
| Safety, comando `scan` | Não executou a análise: exige conta | Não executou a análise: exige conta | `antes/07_safety.txt` e `depois/07_safety.txt` |

O código de `src/` mais que dobrou com a modernização, passando de 133 para 319 linhas, com a inclusão das ofertas, da fábrica, das calculadoras e dos combos. Mesmo com esse aumento, o Bandit continuou sem apontar alertas. Como as bibliotecas do projeto não mudaram, os resultados do pip-audit e do Safety também permaneceram iguais.

## 5. Triagem das mensagens

Nenhuma ferramenta apontou vulnerabilidades. Mesmo assim, foram exibidas mensagens que precisam ser interpretadas, pois nem toda mensagem de uma ferramenta de segurança representa uma vulnerabilidade.

| Mensagem | Ferramenta | Classificação | Relevância para o projeto | Ação |
|---|---|---|---|---|
| `"--no-deps is supported, but users are encouraged to fully hash their pinned dependencies"` e a sugestão de usar `pip-compile` | pip-audit | Recomendação de boa prática, não é vulnerabilidade. | Baixa. Hashes são impressões digitais dos arquivos das bibliotecas e ajudam a garantir que o arquivo instalado corresponde exatamente ao publicado. Protegem contra a instalação de um pacote adulterado. | Não corrigido (seção 7). |
| `"this command (check) has been DEPRECATED"` | Safety | Aviso de que o comando será descontinuado. | Não afeta o projeto diretamente. Afeta a ferramenta: o comando pode deixar de funcionar em uma análise futura. | Registrado como limitação (seção 6). |
| `AuthlibDeprecationWarning` sobre `authlib.jose` e `httpx` | Safety | Aviso interno relacionado às bibliotecas utilizadas pelo próprio Safety. | Nenhuma. São bibliotecas do ambiente das ferramentas, não do projeto. | Nenhuma ação necessária. |
| `"Please login or register Safety CLI"` e `"EOF when reading a line"` | Safety | Limitação de acesso. | O comando `scan` não realizou a análise. As bibliotecas foram verificadas pelo pip-audit e pelo comando `safety check`. | Tentativa registrada (seção 6). |

## 6. Limitação de acesso do Safety

O Safety disponibiliza dois comandos para analisar dependências. O `check`, mais antigo, funciona sem conta e foi o que gerou o resultado apresentado neste relatório. O `scan`, mais novo, exige uma conta gratuita no serviço da empresa Safety. Sem login, ele solicita que a pessoa se registre ou entre na conta e aguarda uma resposta.

Para registrar essa limitação, o comando `scan` foi executado com uma entrada vazia (`< NUL`). Ele exibiu a solicitação de login e foi interrompido com a mensagem `"EOF when reading a line"`. Essa saída está registrada nas evidências 07, antes e depois, atendendo ao item 5.8 do enunciado para situações em que a ferramenta exige uma conta.

A equipe não criou uma conta no serviço, pois o enunciado aceita a evidência da tentativa e as bibliotecas já foram verificadas por duas ferramentas. Caso uma conta seja criada, o `scan` poderá ser executado novamente antes e depois, e este relatório poderá ser atualizado.

## 7. Correções e itens não corrigidos

Nenhuma correção de segurança foi necessária, pois nenhuma ferramenta apontou vulnerabilidades, nem antes nem depois da modernização.

A modernização também não piorou o cenário:

- nenhuma biblioteca foi acrescentada ao projeto (RNF07). As listas de antes e depois são iguais;
- as ferramentas de segurança foram mantidas fora do ambiente virtual do projeto;
- o código novo utiliza apenas a biblioteca padrão do Python, sem acesso a arquivos, rede, banco de dados ou comandos do sistema.

**Item não corrigido: recomendação de uso de hashes pelo pip-audit.**

Adotar essa prática exigiria alterar o `requirements.txt`, fixando versões e hashes, e provavelmente utilizar uma ferramenta nova para gerá-los. O RNF07 determina que o `requirements.txt` permaneça igual ao original, e o enunciado orienta evitar dependências desnecessárias.

Além disso, o código do sistema não utiliza nenhuma das 24 bibliotecas analisadas: todas são ferramentas de teste (pytest, coverage, approvaltests e suas dependências). Portanto, a recomendação fica registrada para uma possível adoção futura.

## 8. Riscos remanescentes

A ausência de alertas não comprova que o sistema seja totalmente seguro. Cada ferramenta possui um alcance limitado:

- O Bandit procura padrões conhecidos no código, mas não entende as regras de negócio. Por exemplo, os defeitos de cálculo D12 e D13, mantidos por decisão da equipe, não são detectados por ferramentas de segurança. Eles foram encontrados durante a leitura do código e registrados nos testes de caracterização.
- O pip-audit e o Safety identificam apenas vulnerabilidades já publicadas em suas bases. Uma falha descoberta posteriormente não aparecerá nos resultados desta análise.
- O `requirements.txt` não fixa versões. Uma nova instalação pode trazer versões diferentes das 24 analisadas, que precisariam passar por uma nova auditoria.
- O comando `safety check` está descontinuado e pode deixar de funcionar, o que afetaria a repetição desta análise no futuro.

## 9. Conclusão

Antes e depois da modernização, o Bandit não apontou problemas no código, e o pip-audit e o Safety não encontraram vulnerabilidades nas 24 bibliotecas do projeto. A modernização mais que dobrou o código de `src/` sem gerar alertas e sem acrescentar bibliotecas.

As mensagens apresentadas pelas ferramentas foram analisadas, e nenhuma foi identificada como vulnerabilidade do projeto. A limitação do `safety scan`, que exige uma conta, também foi registrada com a evidência da tentativa de execução.
