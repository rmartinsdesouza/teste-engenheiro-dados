import os
import numpy as np
import pandas as pd
import utils_bq as bq
import utils_curated as curated


bq.load_env()
RAW_TABLE = os.getenv("TABLE_TAREFAS")
CURATED_TABLE = os.getenv("TABLE_TAREFAS")
RAW_DATASET = os.getenv("RAW_DATASET_ID")
PROCESSED_DATASET = os.getenv("PROCESSED_DATASET_ID")

# ler RAW
df_raw = bq.read_table_to_df(dataset_id=RAW_DATASET, table_id=RAW_TABLE)

# Converte arrays/objetos do BigQuery para listas/dicts Python antes de normalizar
records = df_raw.to_dict(orient="records")

def _ensure_list(x):
    if x is None:
        return []
    # numpy arrays -> list
    if isinstance(x, np.ndarray):
        return x.tolist()
    return x

for r in records:
    r["projetos"] = _ensure_list(r.get("projetos"))
    if isinstance(r["projetos"], dict):
        r["projetos"] = [r["projetos"]]
    normalized_projetos = []
    for p in r["projetos"] or []:
        p = dict(p)
        p["tarefas"] = _ensure_list(p.get("tarefas"))
        if isinstance(p["tarefas"], dict):
            p["tarefas"] = [p["tarefas"]]
        normalized_projetos.append(p)
    r["projetos"] = normalized_projetos
df = pd.json_normalize(
    records,
    record_path=["projetos", "tarefas"],
    meta=[
        ["projetos", "id_projeto"],
        ["projetos", "nome_projeto"],
        ["projetos", "cliente_id"],
        ["projetos", "responsavel"],
        ["projetos", "data_inicio"],
        ["projetos", "data_prevista_fim"],
        ["projetos", "status"],
        ["projetos", "valor_projeto"],
        ["projetos", "horas_totais_estimadas"],
        ["projetos", "horas_totais_realizadas"],
    ],
    sep="_",
    errors="ignore",
)


# limpeza básica
rename_map = {
    # campos da tarefa
    "horas_realizadas": "tarefa_horas_realizadas",
    "status_tarefa": "tarefa_status",
    "responsavel_tarefa": "tarefa_responsavel",
    "horas_estimadas": "tarefa_horas_estimadas",
    "data_prevista_fim": "tarefa_data_prevista_fim",
    "data_inicio": "tarefa_data_inicio",
    "descricao": "tarefa_descricao",
    "id_tarefa": "tarefa_id",

    "projetos_id_projeto": "projeto_id",
    "projetos_nome_projeto": "projeto_nome",
    "projetos_cliente_id": "projeto_cliente_id",
    "projetos_responsavel": "projeto_responsavel",
    "projetos_data_inicio": "projeto_data_inicio",
    "projetos_data_prevista_fim": "projeto_data_prevista_fim",
    "projetos_status": "projeto_status",
    "projetos_valor_projeto": "projeto_valor",
    "projetos_horas_totais_estimadas": "projeto_horas_totais_estimadas",
    "projetos_horas_totais_realizadas": "projeto_horas_totais_realizadas",
}

df = curated.clean_column_names(df, rename_map=rename_map)
df = curated.strip_strings(df)
df = curated.standardize_nulls(df)

# parse de datas em todas as colunas que contenham 'data'
date_cols = [c for c in df.columns if "data" in c]
if date_cols:
    df = curated.parse_dates(df, cols=date_cols)

# ordenação de colunas usando utils_curated.reorder_columns
desired_order = [
    "projeto_id",
    "projeto_nome",
    "projeto_cliente_id",
    "projeto_responsavel",
    "projeto_status",
    "projeto_data_inicio",
    "projeto_data_prevista_fim",
    "projeto_valor",
    "projeto_horas_totais_estimadas",
    "projeto_horas_totais_realizadas",
    "tarefa_id",
    "tarefa_descricao",
    "tarefa_status",
    "tarefa_responsavel",
    "tarefa_data_inicio",
    "tarefa_data_prevista_fim",
    "tarefa_horas_estimadas",
    "tarefa_horas_realizadas",
]
first_cols = [c for c in desired_order if c in df.columns]
if first_cols:
    df = curated.reorder_columns(df, first=first_cols)

# gravar na camada curated
bq.df_to_bq(
    df,
    table_name=CURATED_TABLE,
    dataset=PROCESSED_DATASET,
    write_mode="truncate",
)
