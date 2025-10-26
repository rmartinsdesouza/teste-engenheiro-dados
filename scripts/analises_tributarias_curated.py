import os
import pandas as pd
import utils_bq as bq
import utils_curated as curated


bq.load_env()
RAW_TABLE = os.getenv("TABLE_ANALISES_TRIBUTARIAS")
CURATED_TABLE = os.getenv("TABLE_ANALISES_TRIBUTARIAS")
RAW_DATASET = os.getenv("RAW_DATASET_ID")
PROCESSED_DATASET = os.getenv("PROCESSED_DATASET_ID")

# Lê tabela RAW
df = bq.read_table_to_df(dataset_id=RAW_DATASET, table_id=RAW_TABLE)

# limpeza básica
df = curated.clean_column_names(df)
df = curated.strip_strings(df)
df = curated.standardize_nulls(df)

# gravar na camada curated
bq.df_to_bq(
    df,
    table_name=CURATED_TABLE,
    dataset=PROCESSED_DATASET,
    write_mode="truncate",
)
