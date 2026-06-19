"""
analysis_stats.py
=================
Cálculos para la sección "Análisis Estadísticos" (recreación del tablero Looker).
Todo en español, devolviendo DataFrames listos para graficar/tabular.

Convención de asimetría (igual que el informe):
  asimetría NEGATIVA  -> el registro mayor fue de la pierna IZQUIERDA
  asimetría POSITIVA  -> el registro mayor fue de la pierna DERECHA
"""

import numpy as np
import pandas as pd

import config

# Órdenes canónicos para los ejes
ORDEN_CAT = ["3a", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
ORDEN_ANIO_NAC = ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]


def _col_jugador(df):
    return "dni" if "dni" in df.columns and df["dni"].notna().any() else "jugador"


def ordenar_grupos(valores, grupo_col):
    """Ordena los valores de un grupo según el orden canónico conocido."""
    valores = [v for v in valores if str(v) not in ("", "nan", "None")]
    if grupo_col == "cat":
        base = ORDEN_CAT
    elif grupo_col == "anio_nac":
        base = ORDEN_ANIO_NAC
    else:
        return sorted(valores, key=lambda x: str(x))
    orden = {v: i for i, v in enumerate(base)}
    return sorted(valores, key=lambda x: orden.get(str(x), 999))


# ----------------------------------------------------------------------------
# PARTICIPACIÓN / ASISTENCIA
# ----------------------------------------------------------------------------
def conteo_jugadores(df, grupo_col):
    """Cantidad de jugadores DISTINTOS testeados por valor de grupo_col."""
    if grupo_col not in df.columns:
        return pd.DataFrame(columns=[grupo_col, "cantidad"])
    jcol = _col_jugador(df)
    g = (df.dropna(subset=[grupo_col])
           .groupby(grupo_col)[jcol].nunique()
           .reset_index(name="cantidad"))
    g[grupo_col] = g[grupo_col].astype(str)
    orden = ordenar_grupos(g[grupo_col].tolist(), grupo_col)
    g = g.set_index(grupo_col).reindex(orden).reset_index()
    return g.dropna(subset=["cantidad"])


def asistencia_por_testeo(df, grupo_col="anio_nac"):
    """Jugadores distintos por (grupo, TEST_ID). Devuelve tabla ancha:
    filas = grupo, columnas = test_id (1,2,3...)."""
    if grupo_col not in df.columns or "test_id" not in df.columns:
        return pd.DataFrame()
    jcol = _col_jugador(df)
    d = df.dropna(subset=[grupo_col, "test_id"]).copy()
    d[grupo_col] = d[grupo_col].astype(str)
    d["test_id"] = d["test_id"].astype(str).str.replace(r"\.0$", "", regex=True)
    tabla = (d.groupby([grupo_col, "test_id"])[jcol].nunique()
              .reset_index(name="cantidad")
              .pivot(index=grupo_col, columns="test_id", values="cantidad"))
    orden = ordenar_grupos(tabla.index.tolist(), grupo_col)
    tabla = tabla.reindex(orden)
    # ordenar columnas de test por número
    cols = sorted(tabla.columns, key=lambda x: (len(str(x)), str(x)))
    return tabla[cols]


# ----------------------------------------------------------------------------
# ESTADÍSTICOS POR GRUPO (MIN / PROM / MED / MAX)
# ----------------------------------------------------------------------------
def stats_por_grupo(df, grupo_col, valor_key):
    """DataFrame con MIN, PROM, MED, MAX y N por valor de grupo_col."""
    if grupo_col not in df.columns or valor_key not in df.columns:
        return pd.DataFrame()
    d = df.dropna(subset=[grupo_col, valor_key]).copy()
    d[grupo_col] = d[grupo_col].astype(str)
    g = d.groupby(grupo_col)[valor_key].agg(
        MIN="min", PROM="mean", MED="median", MAX="max", N="count")
    orden = ordenar_grupos(g.index.tolist(), grupo_col)
    return g.reindex(orden).dropna(how="all")


def series_por_grupo(df, grupo_col, valor_key):
    """Devuelve {grupo: np.array de valores} ordenado (para boxplots)."""
    if grupo_col not in df.columns or valor_key not in df.columns:
        return {}
    d = df.dropna(subset=[grupo_col, valor_key]).copy()
    d[grupo_col] = d[grupo_col].astype(str)
    orden = ordenar_grupos(d[grupo_col].unique().tolist(), grupo_col)
    return {g: d.loc[d[grupo_col] == g, valor_key].to_numpy() for g in orden}


# ----------------------------------------------------------------------------
# A 1 PIE (IZQUIERDO / DERECHO)
# ----------------------------------------------------------------------------
def stats_unipodal(df, grupo_col, izq_key, der_key):
    """Tabla MIN/PROM/MED/MAX para IZQ y DER por grupo."""
    if grupo_col not in df.columns:
        return pd.DataFrame()
    res = {}
    for lado, key in (("IZQ", izq_key), ("DER", der_key)):
        if key in df.columns:
            d = df.dropna(subset=[grupo_col, key]).copy()
            d[grupo_col] = d[grupo_col].astype(str)
            g = d.groupby(grupo_col)[key].agg(
                **{f"MIN {lado}": "min", f"PROM {lado}": "mean",
                   f"MED {lado}": "median", f"MAX {lado}": "max"})
            res[lado] = g
    if not res:
        return pd.DataFrame()
    out = pd.concat(res.values(), axis=1)
    orden = ordenar_grupos(out.index.tolist(), grupo_col)
    return out.reindex(orden).dropna(how="all")


def promedios_unipodal(df, grupo_col, izq_key, der_key):
    """Promedios IZQ y DER por grupo (para barras)."""
    if grupo_col not in df.columns:
        return pd.DataFrame()
    d = df.copy()
    d[grupo_col] = d[grupo_col].astype(str)
    cols = {}
    if izq_key in d.columns:
        cols["IZQUIERDO"] = d.groupby(grupo_col)[izq_key].mean()
    if der_key in d.columns:
        cols["DERECHO"] = d.groupby(grupo_col)[der_key].mean()
    if not cols:
        return pd.DataFrame()
    out = pd.DataFrame(cols)
    orden = ordenar_grupos(out.index.tolist(), grupo_col)
    return out.reindex(orden).dropna(how="all")


# ----------------------------------------------------------------------------
# ASIMETRÍAS
# ----------------------------------------------------------------------------
def asim_firmada(serie_izq, serie_der):
    """% de asimetría con signo (negativo = izquierda mayor)."""
    izq = pd.to_numeric(serie_izq, errors="coerce")
    der = pd.to_numeric(serie_der, errors="coerce")
    mx = np.maximum(izq.abs(), der.abs())
    with np.errstate(divide="ignore", invalid="ignore"):
        val = (der - izq) / mx * 100.0
    return pd.Series(val, index=izq.index)


def stats_asimetria(df, grupo_col, asym_key=None, izq_key=None, der_key=None):
    """MIN/PROM/MED/MAX de la asimetría firmada por grupo.
    Usa izq/der si están (signo consistente); si no, la columna asym_key."""
    if grupo_col not in df.columns:
        return pd.DataFrame()
    d = df.copy()
    d[grupo_col] = d[grupo_col].astype(str)
    if izq_key and der_key and izq_key in d.columns and der_key in d.columns:
        d["_asim"] = asim_firmada(d[izq_key], d[der_key])
    elif asym_key and asym_key in d.columns:
        d["_asim"] = pd.to_numeric(d[asym_key], errors="coerce")
    else:
        return pd.DataFrame()
    d = d.dropna(subset=["_asim"])
    g = d.groupby(grupo_col)["_asim"].agg(
        MIN="min", PROM="mean", MED="median", MAX="max", N="count")
    orden = ordenar_grupos(g.index.tolist(), grupo_col)
    return g.reindex(orden).dropna(how="all")


def series_asimetria(df, grupo_col, asym_key=None, izq_key=None, der_key=None):
    """{grupo: array de asimetrías firmadas} para boxplot."""
    if grupo_col not in df.columns:
        return {}
    d = df.copy()
    d[grupo_col] = d[grupo_col].astype(str)
    if izq_key and der_key and izq_key in d.columns and der_key in d.columns:
        d["_asim"] = asim_firmada(d[izq_key], d[der_key])
    elif asym_key and asym_key in d.columns:
        d["_asim"] = pd.to_numeric(d[asym_key], errors="coerce")
    else:
        return {}
    d = d.dropna(subset=["_asim"])
    orden = ordenar_grupos(d[grupo_col].unique().tolist(), grupo_col)
    return {g: d.loc[d[grupo_col] == g, "_asim"].to_numpy() for g in orden}


def pie_dominante(serie_izq, serie_der):
    """Serie DERECHO/IZQUIERDO/SIN DATOS según cuál pierna es mayor."""
    izq = pd.to_numeric(serie_izq, errors="coerce")
    der = pd.to_numeric(serie_der, errors="coerce")
    out = np.where(der > izq, "DERECHO",
                   np.where(izq > der, "IZQUIERDO", "SIN DATOS"))
    out = pd.Series(out, index=izq.index)
    out[izq.isna() | der.isna()] = "SIN DATOS"
    return out


def distribucion_pie_dom(df, grupo_col, pie_col=None, izq_key=None, der_key=None):
    """% de jugadores por pie dominante (DERECHO/IZQUIERDO/SIN DATOS) por grupo.
    Devuelve tabla ancha (filas=grupo, columnas=pie, valores=% 0-100)."""
    if grupo_col not in df.columns:
        return pd.DataFrame()
    d = df.copy()
    d[grupo_col] = d[grupo_col].astype(str)
    if pie_col and pie_col in d.columns:
        d["_pie"] = d[pie_col].astype(str).str.upper().str.strip()
        d["_pie"] = d["_pie"].replace({"L": "IZQUIERDO", "R": "DERECHO",
                                       "LEFT": "IZQUIERDO", "RIGHT": "DERECHO",
                                       "": "SIN DATOS", "NAN": "SIN DATOS"})
    elif izq_key and der_key and izq_key in d.columns and der_key in d.columns:
        d["_pie"] = pie_dominante(d[izq_key], d[der_key])
    else:
        return pd.DataFrame()
    tabla = (d.groupby([grupo_col, "_pie"]).size()
              .reset_index(name="n")
              .pivot(index=grupo_col, columns="_pie", values="n").fillna(0))
    pct = tabla.div(tabla.sum(axis=1), axis=0) * 100.0
    for c in ["IZQUIERDO", "DERECHO", "SIN DATOS"]:
        if c not in pct.columns:
            pct[c] = 0.0
    pct = pct[["DERECHO", "IZQUIERDO", "SIN DATOS"]]
    orden = ordenar_grupos(pct.index.tolist(), grupo_col)
    return pct.reindex(orden).dropna(how="all")


# ----------------------------------------------------------------------------
# POSICIÓN (burbujas)
# ----------------------------------------------------------------------------
def datos_posicion(df, valor_key="altura"):
    """Para el gráfico por posición: cada jugador con su valor y categoría
    (la categoría define el tamaño de burbuja)."""
    cols = [c for c in ["pos", valor_key, "cat", "jugador"] if c in df.columns]
    if "pos" not in cols or valor_key not in cols:
        return pd.DataFrame()
    d = df[cols].dropna(subset=["pos", valor_key]).copy()
    d["pos"] = d["pos"].astype(str).str.strip()
    return d


# ----------------------------------------------------------------------------
# COMPARADOR INDIVIDUAL (por TEST_ID)
# ----------------------------------------------------------------------------
def datos_jugador_por_test(df, jugador, claves):
    """Valores de un jugador por TEST_ID (ordenado). Devuelve DataFrame
    con columnas test_id + las claves pedidas (promedio por test si hay varias filas)."""
    if "jugador" not in df.columns or "test_id" not in df.columns:
        return pd.DataFrame()
    d = df[df["jugador"] == jugador].copy()
    if d.empty:
        return pd.DataFrame()
    d["test_id"] = d["test_id"].astype(str).str.replace(r"\.0$", "", regex=True)
    keys = [k for k in claves if k in d.columns]
    g = d.groupby("test_id")[keys].mean().reset_index()
    g = g.sort_values("test_id", key=lambda s: s.astype(str))
    return g
