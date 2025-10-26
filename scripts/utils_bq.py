from http import client
import os
import json
from pathlib import Path
import sys
from dotenv import load_dotenv
from google.cloud import bigquery
import bigframes.pandas as bf
from google.api_core.exceptions import NotFound
import logging
import pandas as pd
from datetime import datetime, timezone


# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
def load_env():
    load_dotenv(override=False)
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        cred_path = Path("cred.json")
        if cred_path.exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path.resolve())


def create_dataset(dataset_name: str, location: str | None = None):
    """
    Create ou lista um dataset no BigQuery 
    Returns (project_id, dataset_id)
    """

    client = bigquery.Client()
    project_id = client.project
    dataset_id = f"{project_id}.{dataset_name}"

    try:
        dataset = bigquery.Dataset(dataset_id)
        dataset = client.create_dataset(dataset, exists_ok=True)
        logger.info(f"Dataset criado: {dataset.full_dataset_id}")
    except Exception as e:
        logger.error(f"Erro ao criar dataset: {e}")
        raise

    return project_id, dataset_id


def df_to_bq(df: pd.DataFrame, dataset: str, table_name: str, write_mode: str = "truncate") -> str:
    """
    Create ou insere uma tabela no BigQuery a partir de um DataFrame.
    Returns (project_id, dataset_id)
    """
    try:
        client = bigquery.Client()
        project_id = client.project
        table_id = f"{project_id}.{dataset}.{table_name}"

        job_config = bigquery.LoadJobConfig(autodetect=True)

        if write_mode == "truncate":
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        elif write_mode == "append":
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
        else:
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        logger.info(f"DataFrame Header: {df.head()}")
        logger.info(f"DataFrame carregado em BigQuery: {table_id}")

    except Exception as e:
        logger.error(f"Erro ao carregar DataFrame em BigQuery: {e}")
        raise

    return table_id


def json_file_to_bq(json_path: str | Path, dataset: str, table: str, write_mode: str = "truncate") -> str:
    """
    Carrega um arquivo JSON diretamente no BigQuery.
    """
    client = bigquery.Client()
    project_id = client.project
    table_id = f"{project_id}.{dataset}.{table}"

    json_path = Path(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    job_config = bigquery.LoadJobConfig(autodetect=True)
    if write_mode == "truncate":
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    elif write_mode == "append":
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    else:
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY

    records: list[dict]
    if isinstance(data, list):
        if all(isinstance(x, dict) for x in data):
            records = data  # type: ignore
        else:
            records = [{"raw": json.dumps(x, ensure_ascii=False)} for x in data]
    elif isinstance(data, dict):
        records = [data]
    else:
        records = [{"raw": json.dumps(data, ensure_ascii=False)}]

    job = client.load_table_from_json(records, table_id, job_config=job_config)
    job.result()
    logger.info(f"JSON carregado em BigQuery: {table_id}")
    return table_id


def read_table_to_df(
    dataset_id: str,
    table_id: str
    ) -> pd.DataFrame:
    """
    Lê uma tabela do BigQuery e retorna um DataFrame pandas.
    """

    client = bigquery.Client()
    project_id = client.project
    dataset_id = dataset_id
    table_id = table_id

    table_fqn = f"{project_id}.{dataset_id}.{table_id}"
    
    try:
        query = f"SELECT * FROM `{table_fqn}`"
        logger.info(f"Executando query: {query}")
        df = client.query(query).to_dataframe()
    except Exception as e:
        logger.error(f"Erro ao ler tabela {table_fqn} do BigQuery: {e}")
        raise
    logger.info(f"Tabela {table_fqn} lida com sucesso. {df.head()}")
    return df

if __name__ == "__main__":
    load_env()
