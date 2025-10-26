import os
import pandas as pd
import utils_bq as bq


# Carrega variáveis
bq.load_env()
XML_PATH = os.getenv("SOURCE_PATH_NOTAS")
RAW_DATASET = os.getenv("RAW_DATASET_ID")
RAW_TABLE = "notas_fiscais"

logger = bq.logger

# Lê XML
try:
    df = pd.read_xml(XML_PATH)
except Exception as e:
    logger.error(f"Erro ao processar XML: {e}")
    raise

# Salva DataFrame no BigQuery
bq.df_to_bq(df, dataset=RAW_DATASET, table_name=RAW_TABLE, write_mode="truncate")
