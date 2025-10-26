#!/usr/bin/env python3
import os
import pandas as pd
import utils_bq as bq
import utils_curated as curated


bq.load_env()
RAW_TABLE = os.getenv("TABLE_CLIENTES")
CURATED_TABLE = os.getenv("TABLE_CLIENTES")
RAW_DATASET = os.getenv("RAW_DATASET_ID")
PROCESSED_DATASET = os.getenv("PROCESSED_DATASET_ID")

# Lê tabela RAW
df = bq.read_table_to_df(dataset_id=RAW_DATASET, table_id=RAW_TABLE)

# Realiza limpeza padronizada
df = curated.clean_column_names(df)
df = curated.strip_strings(df)
df = curated.standardize_nulls(df)

# cnpj apenas dígitos
df = curated.digits_only(df, cols=["cnpj"]) 

# padroniza nulos novamente (apos digits_only, cnpj vazio -> NA)
df = curated.standardize_nulls(df, cols=["cnpj"])  

# Converte em datas
df = curated.parse_dates(df, cols=["data_cadastro"])

# Remove chaves duplicatas
df = curated.drop_duplicates(df, keys=["id_cliente"])

# Garante chave não nula; descarta registros inválidos
df = curated.drop_na_rows(df, cols=["id_cliente"])

# Salva na camada curated
bq.df_to_bq(
    df,
    table_name=CURATED_TABLE,
    dataset=PROCESSED_DATASET,
    write_mode="truncate",
)

