# Documentação Técnica

Este diretório reúne a documentação técnica do desafio, cobrindo visão da solução, execução, decisões técnicas, arquitetura visual, dicionário de dados e otimizações sugeridas.

- Visão geral e execução rápida: veja abaixo
- Dicionário de dados: consulte `docs/dicionario_dados.md`
- Otimizações e próximos passos: consulte `docs/otimizacoes.md`
- Diagrama de arquitetura (Mermaid): `docs/diagrama_arquitetura.mmd` (renderizado também neste README)

## Visão geral da solução

A solução implementa um pipeline simples em 3 camadas no BigQuery:

- RAW (psa_raw): carrega os arquivos da pasta `dados/` quase “como vieram” (CSV, TXT, JSON, XML/HTML)
- Curated (psa_curated): padroniza nomes de colunas, normaliza nulos, converte datas, de-duplica chaves e, quando necessário, “achata” estruturas (ex.: tarefas de projetos)
- Analytics (psa_analytics): agrega tabelas de curated e produz visões analíticas (fatos/dimensões mínimas)

Todos os scripts residem em `scripts/` e há um orquestrador simples (`run_all.py`) que executa na ordem RAW → Curated → Analytics.

Principais decisões e padrões:

- Colunas em snake_case e strings trimadas
- Nulos padronizados e chaves obrigatórias não nulas em curated
- Datas como tipos nativos (DATE/TIMESTAMP) sempre que possível
- Flatten JSON via `pandas.json_normalize` (Opção A: linha por tarefa, duplicando metadados do projeto)
- IO centralizado em `utils_bq.py` (ler/escrever DataFrame ↔ BigQuery)

## Como executar

Pré-requisitos:

- Python 3.11+ (testado com 3.12)
- Projeto GCP com BigQuery habilitado
- Credenciais: `cred.json` na raiz (ou `GOOGLE_APPLICATION_CREDENTIALS` no ambiente)

Instalação:

```bash
python3 -m venv .venv-gcp
source .venv-gcp/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Execução completa (todas as camadas):

```bash
# usando a venv do projeto
./.venv-gcp/bin/python scripts/run_all.py
```

Execução por grupo (opcional):

```bash
# RAW apenas
RUN_GROUP=raw ./.venv-gcp/bin/python scripts/run_all.py
# Curated apenas
RUN_GROUP=curated ./.venv-gcp/bin/python scripts/run_all.py
# Analytics apenas
RUN_GROUP=analytics ./.venv-gcp/bin/python scripts/run_all.py
```

Variáveis de ambiente relevantes (com defaults no runner):

- RAW_DATASET_ID=psa_raw
- PROCESSED_DATASET_ID=psa_curated
- ANALYTICS_DATASET_ID=psa_analytics
- TABLE_CLIENTES=clientes
- TABLE_ANALISES_TRIBUTARIAS=analises_tributarias
- TABLE_NOTAS=notas_fiscais
- TABLE_TAREFAS=tarefas_projetos
- RAW_TABLE_ANALISES=analises_tributarias
- RAW_TABLE_TAREFAS=tarefas_projetos
- RAW_TABLE_NOTAS=notas_fiscais_raw
- SOURCE_PATH_CLIENTES=dados/dados_clientes.csv
- SOURCE_PATH_ANALISES=dados/analises_tributarias.txt
- SOURCE_PATH_NOTAS=dados/notas_fiscais.xml
- SOURCE_PATH_TAREFAS=dados/tarefas_projetos.json

O runner tenta criar os datasets ausentes no início. As tabelas são criadas automaticamente via `autodetect` durante os loads.

## Decisões técnicas (justificadas)

- Separação RAW/Curated/Analytics: desacopla ingestão de limpezas e das visões analíticas; facilita reprocessamento e governança
- RAW “quase igual à origem”: mantém rastreabilidade e reprodutibilidade
- Curated limpo e consistente: evita joins quebrando por espaços/acentos/maiúsculas diferentes; chaves e datas coerentes
- JSON flatten (tarefas): adotado formato linha por tarefa (Opção A) para facilitar métricas de produtividade e status
- Datas como DATE/TIMESTAMP: formatação (ISO) fica a cargo do consumo; evita ambiguidade de string
- BigQuery IO centralizado: reduz duplicação e garante comportamento consistente de escrita/leitura
- Agregações Analytics minimalistas: apenas o necessário ao problema (resumo de tributos por cliente e performance de projetos)

## Estrutura de pastas (resumo)

```text
cred.json
README.md
requirements.txt
dados/
  analises_tributarias.txt
  dados_clientes.csv
  logs_sistema.html
  notas_fiscais.xml
  tarefas_projetos.json
docs/
  README.md
  dicionario_dados.md
  otimizacoes.md
  diagrama_arquitetura.mmd
scripts/
  run_all.py
  utils_bq.py
  utils_curated.py
  clientes_raw.py
  analises_tributarias_raw.py
  notas_fiscais_raw.py
  tarefas_projetos_raw.py
  logs_sistema.py
  clientes_curated.py
  analises_tributarias_curated.py
  notas_fiscais_curated.py
  logs_sistema_curated.py
  tarefas_projetos_curated.py
  resumo_clientes_tributos.py
  performance_projetos.py
```

## Diagrama de arquitetura (Mermaid)

```mermaid
flowchart LR
  subgraph Local
    A[Arquivos em dados/\nCSV | TXT | JSON | XML/HTML]
  end

  A -->|load| R1[(psa_raw.clientes)]
  A -->|load| R2[(psa_raw.analises_tributarias)]
  A -->|load| R3[(psa_raw.tarefas_projetos)]
  A -->|load| R4[(psa_raw.logs_sistema)]
  A -->|load| R5[(psa_raw.notas_fiscais_raw/notas_fiscais)]

  R1 --> C1[(psa_curated.clientes)]
  R2 --> C2[(psa_curated.analises_tributarias)]
  R3 --> C3[(psa_curated.tarefas_projetos)]
  R4 --> C4[(psa_curated.logs_sistema)]
  R5 --> C5[(psa_curated.notas_fiscais)]

  C1 & C2 --> A1[(psa_analytics.resumo_clientes_tributos)]
  C3 --> A2[(psa_analytics.performance_projetos)]

  subgraph Execução
    X[Runner scripts/run_all.py]\nOrdem: RAW -> Curated -> Analytics
  end

  X -.-> R1
  X -.-> C1
  X -.-> A1
```

Observação: o arquivo-fonte do diagrama está em `docs/diagrama_arquitetura.mmd`. Para exportar para PNG, você pode usar a extensão Mermaid do VS Code ou o CLI `mmdc`.
