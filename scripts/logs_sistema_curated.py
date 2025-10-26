import os
import pandas as pd
import utils_bq as bq
import utils_curated as curated


bq.load_env()
RAW_TABLE = os.getenv("TABLE_LOGS")
CURATED_TABLE = os.getenv("TABLE_LOGS")
RAW_DATASET = os.getenv("RAW_DATASET_ID")
PROCESSED_DATASET = os.getenv("PROCESSED_DATASET_ID")

# ler raw
df = bq.read_table_to_df(dataset_id=RAW_DATASET, table_id=RAW_TABLE)

# limpeza básica
df = curated.clean_column_names(df)
df = curated.strip_strings(df)
df = curated.standardize_nulls(df)

# parse de datas comuns, se existirem
date_candidates = [c for c in ["timestamp", "data", "data_evento", "data_criacao", "data_atualizacao"] if c in df.columns]
if date_candidates:
    df = curated.parse_dates(df, cols=date_candidates)

# remoção de chaves duplicatas
df = curated.drop_duplicates(df, keys=["id_log"])

# gravar na camada curated
bq.df_to_bq(
    df,
    table_name=CURATED_TABLE,
    dataset=PROCESSED_DATASET,
    write_mode="truncate",
)
