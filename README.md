# Teste Engenheiro de Dados — Setup simples

Este projeto fornece um ETL local mínimo para processar os arquivos em `dados/` e gerar saídas em `output/`, com opção (opcional) para carregar a tabela `dados_clientes` no BigQuery.

## Estrutura

- `dados/` — arquivos de entrada (CSV, JSON, XML, HTML, TXT)
- `scripts/main.py` — script principal ETL
- `output/` — saídas geradas (CSV/Parquet e/ou texto)
- `cred.json` — credencial (conta de serviço GCP)
- `.env.example` — variáveis de ambiente de exemplo
- `requirements.txt` — dependências Python

## Pré-requisitos

- Python 3.10+ (recomendado)

## Ambiente virtual

Crie e ative um novo ambiente virtual (ex.: `.venv-gcp`) e instale as dependências:

```bash
python3 -m venv .venv-gcp
source .venv-gcp/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Se preferir, ajuste o nome do ambiente.

## Variáveis de ambiente

Crie um `.env` (opcional) copiando o exemplo:

```bash
cp .env.example .env
```

- Por padrão, se `cred.json` existir na raiz, o script já configura `GOOGLE_APPLICATION_CREDENTIALS` automaticamente.
- Para BigQuery, informe `GCP_PROJECT_ID`, `BQ_DATASET` e `BQ_TABLE` (ou use flags na linha de comando).

## Executar ETL local

```bash
python scripts/main.py --dados-dir dados --output-dir output
```

O script irá:
- Ler `dados_clientes.csv` → salvar CSV e Parquet em `output/`
- Ler `tarefas_projetos.json` → normalizar e salvar em `output/`
- Ler `notas_fiscais.xml` → extrair texto de elementos (caminho/tag) e salvar em `output/`
- Ler `logs_sistema.html` → extrair tabelas (se houver) ou texto e salvar em `output/`
- Copiar `analises_tributarias.txt` para `output/`

## Carregar no BigQuery (opcional)

Para enviar apenas `dados_clientes` ao BigQuery:

```bash
python scripts/main.py \
  --dados-dir dados \
  --output-dir output \
  --to-bq \
  --project-id "SEU_PROJECT" \
  --dataset "SEU_DATASET" \
  --table "dados_clientes"
```

Requer a credencial GCP válida (conta de serviço) e permissões de acesso ao projeto e dataset.

## Observações

- O processamento de XML/HTML é genérico e simples. Se o teste exigir um schema específico, podemos evoluir o parser facilmente.
- As saídas Parquet dependem do `pyarrow`; se falhar, o script segue apenas com CSV.
