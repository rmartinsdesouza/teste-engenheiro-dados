#!/usr/bin/env python3
import os
import pandas as pd
import utils_bq as bq

# Instancia variáveis de ambiente
bq.load_env()

# Caminhos e destino no BQ
logs_html = os.getenv("SOURCE_PATH_LOGS")
raw_dataset = os.getenv("RAW_DATASET_ID")
table_name = "logs_sistema"

# Carrega logs a partir de HTML
try:
    if not os.path.exists(logs_html):
        raise FileNotFoundError(f"Arquivo HTML não encontrado em '{logs_html}'")

    # pandas.read_html retorna uma lista de DataFrames
    tables = pd.read_html(logs_html)
    if not tables:
        raise ValueError("Nenhuma tabela encontrada no arquivo HTML")

    df = tables[0]

    # Renomeia colunas para compatibilidade com BigQuery
    rename_map = {
        "ID Log": "id_log",
        "Timestamp": "timestamp",
        "Usuário": "usuario",
        "Ação": "acao",
        "Entidade Afetada": "entidade_afetada",
        "Resultado": "resultado",
        "IP": "ip",
    }
    df = df.rename(columns=rename_map)

    # Tipagem básica
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

except Exception as e:
    bq.logger.error(f"Erro ao carregar o HTML: {e}")
    raise

# Salva DataFrame no BigQuery
bq.df_to_bq(df, raw_dataset, table_name, "truncate")
