import os
import pandas as pd
import utils_bq as bq

# Instancia variáveis de ambiente
bq.load_env()

clientes_csv = os.getenv("SOURCE_PATH_CLIENTES")
raw_dataset = os.getenv("RAW_DATASET_ID")
table_name = os.getenv("TABLE_CLIENTES")


# Carrega clientes do CSV
try:
    if not os.path.exists(clientes_csv):
        raise FileNotFoundError(
            bq.logger.error(f"Arquivo CSV não encontrado em '{clientes_csv}'")
        )
    df = pd.read_csv(clientes_csv, encoding="utf-8", header=0)
except Exception as e:
    bq.logger.error(f"Erro ao carregar o CSV: {e}")
    raise


# Salva DataFrame no BigQuery
bq.df_to_bq(df, raw_dataset, table_name, "truncate")
