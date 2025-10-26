import os
import pandas as pd
import utils_bq as bq
import utils_curated as curated


bq.load_env()
# datasets e tabelas
PROCESSED_DATASET = os.getenv("PROCESSED_DATASET_ID")
ANALYTICS_DATASET = os.getenv("ANALYTICS_DATASET_ID")
TABLE_CLIENTES = os.getenv("TABLE_CLIENTES")
TABLE_ANALISES = os.getenv("TABLE_ANALISES_TRIBUTARIAS")
output_table = 'resumo_clientes_tributos'


# lê curated
df_clientes = bq.read_table_to_df(dataset_id=PROCESSED_DATASET, table_id=TABLE_CLIENTES)
df_analises = bq.read_table_to_df(dataset_id=PROCESSED_DATASET, table_id=TABLE_ANALISES)

# seleciona colunas úteis dos clientes para evitar duplicidade pós-merge
cols_cliente_dim = [
    "id_cliente", "razao_social", "cnpj", "porte_empresa", "setor", "cidade", "estado"
]
cols_cliente_dim = [c for c in cols_cliente_dim if c in df_clientes.columns]

# Alguns datasets usam id_cliente
if "cliente_id" not in df_analises.columns:
    if "id_cliente" in df_analises.columns:
        df_analises = df_analises.rename(columns={"id_cliente": "cliente_id"})
    else:
        raise ValueError("Coluna 'cliente_id' não encontrada em análises.")

# garantir tipos numéricos
if "valor_identificado" in df_analises.columns:
    df_analises["valor_identificado"] = pd.to_numeric(df_analises["valor_identificado"], errors="coerce")

# merge para enriquecer análises com dimensões de cliente
left_cols = ["cliente_id", "tipo_tributo", "id_analise", "periodo_analise", "valor_identificado"]
left_cols = [c for c in left_cols if c in df_analises.columns]

df_enriched = df_analises[left_cols].merge(
    df_clientes[cols_cliente_dim],
    how="left",
    left_on="cliente_id",
    right_on="id_cliente",
)

# agrega: resumo por cliente x tributo
agg = {
    "id_analise": "nunique",
}
if "valor_identificado" in df_enriched.columns:
    agg["valor_identificado"] = ["sum", "mean"]

group_cols = ["cliente_id", "tipo_tributo"]
for c in ["razao_social", "cnpj", "porte_empresa", "setor", "cidade", "estado"]:
    if c in df_enriched.columns:
        group_cols.append(c)

# Para evitar MultiIndex nos agregados
df_summary = df_enriched.groupby(group_cols, dropna=False).agg(agg).reset_index()
if "valor_identificado" in df_enriched.columns:
    # renomeia colunas agregadas
    df_summary.columns = [
        "_".join([c for c in col if c]) if isinstance(col, tuple) else col for col in df_summary.columns
    ]
    df_summary = df_summary.rename(columns={
        "id_analise_nunique": "qtd_analises",
        "valor_identificado_sum": "valor_total_identificado",
        "valor_identificado_mean": "valor_medio_identificado",
    })
else:
    df_summary = df_summary.rename(columns={
        "id_analise": "qtd_analises",
    })

# ordena colunas
desired_order = [
    "cliente_id", "razao_social", "cnpj", "porte_empresa", "setor", "cidade", "estado",
    "tipo_tributo", "qtd_analises", "valor_total_identificado", "valor_medio_identificado",
]
first_cols = [c for c in desired_order if c in df_summary.columns]
if first_cols:
    df_summary = curated.reorder_columns(df_summary, first=first_cols)

# escreve na camada analytics
bq.df_to_bq(
    df_summary,
    dataset=ANALYTICS_DATASET,
    table_name=output_table,
    write_mode="truncate",
)
