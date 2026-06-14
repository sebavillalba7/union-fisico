"""
data_loader.py
==============
Carga las bases de datos CMJ y Nórdico desde Google Sheets (CSV publicado),
resuelve los nombres de columnas (flexible) y los renombra a nombres internos
estándar para que el resto de la app sea simple y robusto.

Columnas internas resultantes:
  comunes:  jugador, anio, cat, pos, test_id, fecha, fec_nac, dni, fecha_dt
  CMJ:      altura, ecc_pp, rsi
  Nórdico:  fza_izq, fza_der, dif, masa
"""

import io
import requests
import pandas as pd
import numpy as np
import streamlit as st

import config


def _find_column(df_cols, candidatos):
    """Busca la primera columna que coincida (ignorando mayúsculas y espacios)."""
    norm = {str(c).strip().lower(): c for c in df_cols}
    for cand in candidatos:
        key = str(cand).strip().lower()
        if key in norm:
            return norm[key]
    return None


def _to_number(serie):
    """Convierte a número soportando coma decimal y símbolos sueltos."""
    if serie.dtype.kind in "biufc":
        return pd.to_numeric(serie, errors="coerce")
    s = (
        serie.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(r"[^\d,.\-]", "", regex=True)
        .str.strip()
    )
    # Si usa coma como decimal (y no como separador de miles)
    s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False) \
        if s.str.contains(",").any() and not s.str.contains(r"\.\d{3}").any() else s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def _normalizar(df, metricas):
    """Renombra columnas comunes y de métricas a nombres internos."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    rename = {}

    # Columnas comunes
    for key, candidatos in config.COMMON_COLUMNS.items():
        col = _find_column(df.columns, candidatos)
        if col is not None:
            rename[col] = key

    # Métricas
    for m in metricas:
        col = _find_column(df.columns, m["col"])
        if col is not None:
            rename[col] = m["key"]

    df = df.rename(columns=rename)

    # Convertir métricas a número
    for m in metricas:
        if m["key"] in df.columns:
            df[m["key"]] = _to_number(df[m["key"]])

    # Año como texto (categórico) y limpio
    if "anio" in df.columns:
        df["anio"] = df["anio"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    if "cat" in df.columns:
        df["cat"] = df["cat"].astype(str).str.strip().map(config.normalizar_categoria)
    if "pos" in df.columns:
        df["pos"] = df["pos"].astype(str).str.strip()
    if "jugador" in df.columns:
        df["jugador"] = df["jugador"].astype(str).str.strip()

    # Fecha -> texto y datetime para ordenar/graficar
    if "fecha" in df.columns:
        df["fecha"] = df["fecha"].astype(str).str.strip()
        df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
    else:
        df["fecha_dt"] = pd.NaT

    # Eliminar filas totalmente vacías
    df = df.dropna(how="all")
    return df


@st.cache_data(ttl=600, show_spinner=False)
def cargar_csv(url: str) -> pd.DataFrame:
    """Descarga un CSV desde una URL y lo devuelve como DataFrame."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.content.decode("utf-8", errors="replace")))


@st.cache_data(ttl=600, show_spinner=False)
def cargar_datos():
    """Carga y normaliza ambas bases. Devuelve (df_cmj, df_nordico, error)."""
    error = None
    df_cmj = pd.DataFrame()
    df_nordico = pd.DataFrame()
    try:
        df_cmj = _normalizar(cargar_csv(config.URL_CMJ), config.CMJ_METRICS)
    except Exception as e:
        error = f"Error cargando CMJ: {e}"
    try:
        df_nordico = _normalizar(cargar_csv(config.URL_NORDICO), config.NORDICO_METRICS)
    except Exception as e:
        error = (error + " | " if error else "") + f"Error cargando Nórdico: {e}"
    return df_cmj, df_nordico, error
