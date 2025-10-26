"""
Utilitários para a camada curated (limpeza e padronização de dados).

Objetivo:
- Centralizar funções de limpeza (nomes de colunas, strings, tipos, datas, nulos)
- Facilitar leitura da camada raw (via BigQuery) e escrita na curated
- Evitar repetição de código entre os arquivos *_curated.py
"""

import os
import re
import unicodedata
from typing import Iterable, Mapping, Sequence
import pandas as pd
import utils_bq as bq

logger = bq.logger

# Column name cleaning
def _to_ascii(text: str):
    text_norm = unicodedata.normalize("NFKD", text)
    return text_norm.encode("ascii", "ignore").decode("ascii")


def _to_snake_case(text: str):
    # Substitui separadores por underscore, remove duplicados e deixa minúsculo
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_").lower()


def clean_column_names(
    df: pd.DataFrame,
    rename_map: Mapping[str, str] | None = None,
    ascii_only: bool = True,
    snake_case: bool = True,
):
    """
    Padroniza nomes de colunas:
    - aplica rename_map primeiro (se fornecido)
    - remove acentos (ascii_only)
    - converte para snake_case (snake_case)
    """
    cols = list(df.columns)

    # Renomeia por mapeamento explícito
    if rename_map:
        df = df.rename(columns=rename_map)
        cols = list(df.columns)

    new_cols: list[str] = []
    for c in cols:
        new_c = c
        if ascii_only:
            new_c = _to_ascii(new_c)
        if snake_case:
            new_c = _to_snake_case(new_c)
        new_cols.append(new_c)

    df.columns = new_cols
    return df


# String cleaning helpers
def strip_strings(df: pd.DataFrame, cols: Iterable[str] | None = None):
    """Aplica strip() nas colunas de texto (todas se cols=None)."""
    target_cols = cols or [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    for c in target_cols:
        df[c] = df[c].astype("string").str.strip()
    return df


def collapse_spaces(df: pd.DataFrame, cols: Iterable[str] | None = None):
    """Colapsa múltiplos espaços em um único espaço nas colunas de texto."""
    target_cols = cols or [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    for c in target_cols:
        df[c] = df[c].astype("string").str.replace(r"\s+", " ", regex=True)
    return df


def remove_special_chars(
    df: pd.DataFrame,
    cols: Iterable[str] | None = None,
    allowed_pattern: str = r"[^0-9a-zA-Z _\-@\.\/]",
    replace_with: str = "",
):
    """Remove caracteres especiais das colunas de texto (mantém básicos por padrão)."""
    target_cols = cols or [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    for c in target_cols:
        df[c] = df[c].astype("string").str.replace(allowed_pattern, replace_with, regex=True)
    return df


def digits_only(df: pd.DataFrame, cols: Iterable[str]):
    """Mantém apenas dígitos (0-9) nas colunas informadas.

    Exemplo: '12.345/0001-99' -> '12345000199'
    """
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype("string").str.replace(r"\D+", "", regex=True)
    return df


def to_lower(df: pd.DataFrame, cols: Iterable[str] | None = None):
    target_cols = cols or [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    for c in target_cols:
        df[c] = df[c].astype("string").str.lower()
    return df


# Types, dates, ordering, dedup
def cast_columns(df: pd.DataFrame, types: Mapping[str, str]):
    """Faz astype com errors='ignore' conforme mapeamento informado."""
    for col, dtype in types.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(dtype)
            except Exception:  # mantém valor original se falhar
                logger.warning(f"Falha ao converter coluna {col} para {dtype}")
    return df


def parse_dates(df: pd.DataFrame, cols: Iterable[str], dayfirst: bool = False):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=dayfirst)
    return df


def drop_duplicates(df: pd.DataFrame, keys: Iterable[str] | None = None):
    return df.drop_duplicates(subset=list(keys) if keys else None, keep="last")


def reorder_columns(df: pd.DataFrame, first: Sequence[str]):
    """Reordena colunas colocando 'first' no início e mantendo o resto na ordem original."""
    rest = [c for c in df.columns if c not in first]
    return df[first + rest]


# Null handling helpers
def standardize_nulls(
    df: pd.DataFrame,
    cols: Iterable[str] | None = None,
    null_tokens: Iterable[str] | None = None,
):
    """Converte valores 'nulos' comuns para NA nas colunas de texto.

    - Substitui strings vazias/espaços e tokens como 'null', 'None', 'N/A', 'na' por NA.
    - Aplica apenas em colunas string (ou nas informadas em cols).
    """
    tokens = set(null_tokens or ["", "null", "NULL", "None", "N/A", "na", "NaN"])
    target_cols = cols or [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    for c in target_cols:
        s = df[c].astype("string").str.strip()
        df[c] = s.where(~s.isin(tokens), other=pd.NA)
    return df


def drop_na_rows(df: pd.DataFrame, cols: Iterable[str]):
    """Remove linhas onde alguma das colunas informadas é nula (NA/NaN)."""
    return df.dropna(subset=list(cols))


def fillna_values(df: pd.DataFrame, fill_map: dict[str, object]):
    """Preenche NA/NaN conforme mapeamento coluna -> valor."""
    for col, val in fill_map.items():
        if col in df.columns:
            df[col] = df[col].fillna(val)
    return df
