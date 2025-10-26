import os
from pathlib import Path
import pandas as pd
import utils_bq as bq


bq.load_env()

# Carrega variáveis de ambiente 
TXT_PATH = os.getenv("SOURCE_PATH_ANALISES")
RAW_DATASET = os.getenv("RAW_DATASET_ID")
RAW_TABLE = os.getenv("RAW_TABLE_ANALISES")


def read_analises_txt(path: str | Path) -> pd.DataFrame:
    """
    Lê arquivo pipe-delimitado com header.
    Tipagem básica: valor_identificado como float.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    df = pd.read_csv(path, sep="|", dtype={
        "id_analise": "string",
        "cliente_id": "string",
        "tipo_tributo": "string",
        "periodo_analise": "string",
        "observacoes": "string",
    })

    # Normaliza tipos numéricos
    if "valor_identificado" in df.columns:
        df["valor_identificado"] = pd.to_numeric(df["valor_identificado"], errors="coerce")

    # Trim de espaços em texto
    for col in [
        "id_analise",
        "cliente_id",
        "tipo_tributo",
        "periodo_analise",
        "observacoes",
    ]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    return df


if __name__ == "__main__":
    df = read_analises_txt(TXT_PATH)
    table_id = bq.df_to_bq(df, dataset=RAW_DATASET, table_name=RAW_TABLE, write_mode="truncate")
