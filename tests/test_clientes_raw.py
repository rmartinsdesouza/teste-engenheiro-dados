import os
import runpy
import sys
from pathlib import Path

import types
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_clientes_raw_load_calls_df_to_bq(monkeypatch, tmp_path):
    # preparar arquivo temporário (o script valida a existência física)
    src = tmp_path / "dados_clientes.csv"
    src.write_text("id_cliente,razao_social,cnpj\nCLI0001,Empresa A,00.000.000/0000-00\n", encoding="utf-8")

    # monkeypatch para read_csv retornar um DF controlado (independente do conteúdo)
    def fake_read_csv(path, *args, **kwargs):
        return pd.DataFrame(
            [{"id_cliente": "CLI0001", "razao_social": "Empresa A", "cnpj": "00.000.000/0000-00"}]
        )

    captured = {}

    def fake_df_to_bq(df: pd.DataFrame, dataset: str, table_name: str, write_mode: str = "truncate"):
        captured["shape"] = df.shape
        captured["dataset"] = dataset
        captured["table_name"] = table_name
        captured["write_mode"] = write_mode
        return f"fake.{dataset}.{table_name}"

    monkeypatch.setenv("SOURCE_PATH_CLIENTES", str(src))
    monkeypatch.setenv("RAW_DATASET_ID", "psa_raw")
    monkeypatch.setenv("TABLE_CLIENTES", "clientes")

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    fake_bq = types.SimpleNamespace(
        load_env=lambda: None,
        df_to_bq=fake_df_to_bq,
    )
    sys.modules["utils_bq"] = fake_bq

    runpy.run_path(str(SCRIPTS / "clientes_raw.py"), run_name="__main__")

    assert captured["shape"] == (1, 3)
    assert captured["dataset"] == "psa_raw"
    assert captured["table_name"] == "clientes"
    assert captured["write_mode"] == "truncate"
