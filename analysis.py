"""
analysis.py
===========
Lógica de cálculo (sin Streamlit, para poder testearla):
- Filtros en cascada
- Promedio/mín/máx por categoría y por posición
- Valores máximos por jugador/fecha
- Datos de referencia para el radar (promedios)
"""

import numpy as np
import pandas as pd

import config


# ----------------------------------------------------------------------------
# FILTROS
# ----------------------------------------------------------------------------
def aplicar_filtros(df, selecciones: dict):
    """Aplica un diccionario {columna: [valores]} al DataFrame."""
    out = df.copy()
    for col, valores in selecciones.items():
        if valores and col in out.columns:
            out = out[out[col].isin(valores)]
    return out


def opciones_disponibles(df, col):
    """Valores únicos ordenados de una columna (para los desplegables)."""
    if col not in df.columns:
        return []
    vals = df[col].dropna().unique().tolist()
    try:
        # intento de orden numérico si corresponde
        return sorted(vals, key=lambda x: (str(x)))
    except Exception:
        return sorted(map(str, vals))


# ----------------------------------------------------------------------------
# AGREGACIONES
# ----------------------------------------------------------------------------
def resumen_metricas(df, metricas):
    """Devuelve dict {key: {'prom':, 'min':, 'max':, 'n':}} para cada métrica."""
    res = {}
    for m in metricas:
        k = m["key"]
        if k in df.columns and df[k].notna().any():
            s = df[k].dropna()
            res[k] = {"prom": float(s.mean()), "min": float(s.min()),
                      "max": float(s.max()), "n": int(s.count())}
        else:
            res[k] = {"prom": np.nan, "min": np.nan, "max": np.nan, "n": 0}
    return res


def matriz_por_grupo(df, grupo_col, metricas, agg="mean"):
    """Tabla: filas = valores de grupo_col, columnas = métricas (agregadas)."""
    keys = [m["key"] for m in metricas if m["key"] in df.columns]
    if grupo_col not in df.columns or not keys:
        return pd.DataFrame()
    g = df.groupby(grupo_col)[keys].agg(agg)
    # renombrar a labels
    labels = {m["key"]: m["label"] for m in metricas}
    g = g.rename(columns=labels)
    return g


def valores_max_por_fecha(df, metricas):
    """Para un jugador: toma el valor MÁXIMO de cada métrica por fecha.
    Devuelve DataFrame indexado por fecha (ordenado temporalmente)."""
    keys = [m["key"] for m in metricas if m["key"] in df.columns]
    if not keys or "fecha" not in df.columns:
        return pd.DataFrame()
    g = df.groupby(["fecha"], as_index=False).agg(
        {**{k: "max" for k in keys}, "fecha_dt": "first"}
    )
    g = g.sort_values("fecha_dt")
    return g


def valor_unico(df, metrica_key, agg="max"):
    """Un solo valor agregado de una métrica (para comparaciones)."""
    if metrica_key not in df.columns or df[metrica_key].dropna().empty:
        return np.nan
    return float(getattr(df[metrica_key].dropna(), agg)())


# ----------------------------------------------------------------------------
# DATOS PARA EL RADAR
# ----------------------------------------------------------------------------
def _media_metricas(df, metricas):
    """Media de cada métrica sobre un DataFrame -> dict key: valor."""
    out = {}
    for m in metricas:
        k = m["key"]
        if k in df.columns and df[k].notna().any():
            out[k] = float(df[k].dropna().mean())
        else:
            out[k] = np.nan
    return out


def perfil_jugador(df_cmj, df_nordico, jugador, metricas_cmj, metricas_nordico, agg="max"):
    """Perfil de un jugador: valor agregado de cada métrica (cmj + nórdico)."""
    out = {}
    dcj = df_cmj[df_cmj["jugador"] == jugador] if "jugador" in df_cmj.columns else pd.DataFrame()
    dn = df_nordico[df_nordico["jugador"] == jugador] if "jugador" in df_nordico.columns else pd.DataFrame()
    for m in metricas_cmj:
        out[m["key"]] = valor_unico(dcj, m["key"], agg)
    for m in metricas_nordico:
        out[m["key"]] = valor_unico(dn, m["key"], agg)
    return out


def referencia_radar(df_cmj, df_nordico, tipo, pos=None,
                     metricas_cmj=None, metricas_nordico=None,
                     cat_3a=config.CATEGORIA_3A):
    """
    Devuelve dict key->valor promedio según el tipo de referencia:
      - 'PROM POS'     : promedio de la posición (en el df recibido, ya filtrado por categoría)
      - 'PROM EQUIPO'  : promedio del equipo (todo el df recibido)
      - 'PROM POS 3a'  : promedio de la posición pero en categoría 3a
      - 'PROM 3a'      : promedio del equipo de 3a
    NOTA: para las opciones de 3a se debe pasar el dataset COMPLETO (sin filtrar
    por categoría) para que existan los datos de 3a.
    """
    metricas_cmj = metricas_cmj or config.CMJ_METRICS
    metricas_nordico = metricas_nordico or config.NORDICO_METRICS

    dcj, dn = df_cmj, df_nordico
    if tipo == "PROM POS" and pos is not None:
        dcj = dcj[dcj["pos"] == pos] if "pos" in dcj.columns else dcj
        dn = dn[dn["pos"] == pos] if "pos" in dn.columns else dn
    elif tipo == "PROM EQUIPO":
        pass  # usa todo
    elif tipo == "PROM POS 3a" and pos is not None:
        dcj = dcj[(dcj.get("cat") == cat_3a) & (dcj.get("pos") == pos)] if "cat" in dcj.columns else dcj
        dn = dn[(dn.get("cat") == cat_3a) & (dn.get("pos") == pos)] if "cat" in dn.columns else dn
    elif tipo == "PROM 3a":
        dcj = dcj[dcj.get("cat") == cat_3a] if "cat" in dcj.columns else dcj
        dn = dn[dn.get("cat") == cat_3a] if "cat" in dn.columns else dn

    out = {}
    out.update(_media_metricas(dcj, metricas_cmj))
    out.update(_media_metricas(dn, metricas_nordico))
    return out


def escalar_para_radar(perfiles: dict, df_cmj, df_nordico, metricas):
    """
    Escala cada métrica a 0-100 usando min-max del dataset completo.
    Para métricas donde 'menos es mejor' (ej. Dif %), invierte la escala
    para que más área en el radar = mejor rendimiento.
    perfiles: dict {nombre_serie: {key: valor}}
    Devuelve: dict {nombre_serie: {key: valor_escalado_0_100}}
    """
    rangos = {}
    for m in metricas:
        k = m["key"]
        vals = []
        if k in df_cmj.columns:
            vals.append(df_cmj[k].dropna())
        if k in df_nordico.columns:
            vals.append(df_nordico[k].dropna())
        s = pd.concat(vals) if vals else pd.Series(dtype=float)
        if not s.empty:
            rangos[k] = (float(s.min()), float(s.max()))
        else:
            rangos[k] = (0.0, 1.0)

    escalados = {}
    for nombre, perfil in perfiles.items():
        esc = {}
        for m in metricas:
            k = m["key"]
            v = perfil.get(k, np.nan)
            lo, hi = rangos[k]
            if pd.isna(v) or hi == lo:
                esc[k] = 0.0
            else:
                pct = (v - lo) / (hi - lo) * 100.0
                if not m["higher_better"]:
                    pct = 100.0 - pct  # invertir: menos es mejor
                esc[k] = max(0.0, min(100.0, pct))
        escalados[nombre] = esc
    return escalados
