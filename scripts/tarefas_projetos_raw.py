import os
from pathlib import Path
import utils_bq as bq


bq.load_env()

# Carrega variáveis
json_path = os.getenv("SOURCE_PATH_TAREFAS")
raw_dataset = os.getenv("RAW_DATASET_ID")
table_name = os.getenv("RAW_TABLE_TAREFAS")

# Validação simples de existência do arquivo
if not Path(json_path).exists():
    raise FileNotFoundError(f"Arquivo JSON não encontrado em '{json_path}'")

# Carrega JSON bruto no BigQuery (autodetect)
bq.json_file_to_bq(json_path, dataset=raw_dataset, table=table_name, write_mode="truncate")
