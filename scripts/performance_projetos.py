import os
import pandas as pd
import numpy as np
import utils_bq as bq
import utils_curated as curated

bq.load_env()
PROCESSED_DATASET = os.getenv("PROCESSED_DATASET_ID")
ANALYTICS_DATASET = os.getenv("ANALYTICS_DATASET_ID")
TABLE_TAREFAS = os.getenv("TABLE_TAREFAS")
OUTPUT_TABLE = "performance_projetos"


# lê curated tarefas e projetos
df = bq.read_table_to_df(dataset_id=PROCESSED_DATASET, table_id=TABLE_TAREFAS)

# garante numéricos para horas
df["tarefa_horas_estimadas"] = pd.to_numeric(df.get("tarefa_horas_estimadas"), errors="coerce")
df["tarefa_horas_realizadas"] = pd.to_numeric(df.get("tarefa_horas_realizadas"), errors="coerce")
df[["tarefa_horas_estimadas", "tarefa_horas_realizadas"]] = df[["tarefa_horas_estimadas", "tarefa_horas_realizadas"]].fillna(0)


KEYS = [
    "projeto_id",
    "projeto_nome",
    "projeto_cliente_id",
    "projeto_responsavel",
    "projeto_status",
    "projeto_data_inicio",
    "projeto_data_prevista_fim",
]
existing_keys = [c for c in KEYS if c in df.columns]

# agregados por projeto
agg_df = (
    df.groupby(existing_keys, dropna=False)
      .agg(
          qtd_tarefas=("tarefa_id", "nunique"),
          horas_estimadas_total=("tarefa_horas_estimadas", "sum"),
          horas_realizadas_total=("tarefa_horas_realizadas", "sum"),
      )
      .reset_index()
)

# métricas derivadas
agg_df["horas_saldo"] = agg_df["horas_estimadas_total"] - agg_df["horas_realizadas_total"]
agg_df["pct_execucao"] = np.where(
    agg_df["horas_estimadas_total"] > 0,
    agg_df["horas_realizadas_total"] / agg_df["horas_estimadas_total"],
    np.nan,
)

# distribuição por status (pivot)
if "tarefa_status" in df.columns:
    pivot = (
        pd.pivot_table(
            df,
            index=existing_keys,
            columns="tarefa_status",
            values="tarefa_id",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    # normaliza nomes das colunas do pivot: prefixo e snake_case
    status_cols = [c for c in pivot.columns if c not in existing_keys]
    rename_status = {}
    for sc in status_cols:
        col = f"tarefas_status_{str(sc)}"
        # limpeza simples para snake_case ascii
        col = (
            col.lower()
               .replace(" ", "_")
               .replace("-", "_")
               .replace("/", "_")
        )
        rename_status[sc] = col
    pivot = pivot.rename(columns=rename_status)

    # join com agregados
    perf = agg_df.merge(pivot, how="left", on=existing_keys)
else:
    perf = agg_df.copy()

# ordenação de colunas
BASE_ORDER = existing_keys + [
    "qtd_tarefas",
    "horas_estimadas_total",
    "horas_realizadas_total",
    "horas_saldo",
    "pct_execucao",
]
first_cols = [c for c in BASE_ORDER if c in perf.columns]
if first_cols:
    perf = curated.reorder_columns(perf, first=first_cols)

# grava em analytics
bq.df_to_bq(
    perf,
    dataset=ANALYTICS_DATASET,
    table_name=OUTPUT_TABLE,
    write_mode="truncate",
)
