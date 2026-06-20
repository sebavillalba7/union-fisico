"""
charts_stats.py
===============
Gráficos de la sección "Análisis Estadísticos" (Plotly), con etiquetas de
valores, diseño institucional y estética cuidada.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import config

ROJO = config.ROJO
AZUL = config.AZUL
GRIS = "#9CA3AF"
GRIS_CLARO = "#E5E7EB"


def _base(fig, titulo="", ylabel="", xlabel=""):
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15, color=AZUL)),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(color="#1f2937", size=13),
        margin=dict(l=55, r=20, t=55, b=45),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        bargap=0.25,
    )
    fig.update_xaxes(title=xlabel, showgrid=False, linecolor=GRIS_CLARO)
    fig.update_yaxes(title=ylabel, showgrid=True, gridcolor="#F0F1F3", zeroline=False)
    return fig


def barras_conteo(serie, titulo="", color=ROJO, xlabel="", ylabel="Cantidad"):
    """Barras verticales con la cantidad encima de cada barra."""
    x = [str(i) for i in serie.index]
    y = serie.values
    fig = go.Figure(go.Bar(
        x=x, y=y, marker_color=color,
        text=[f"{int(v)}" if pd.notna(v) else "" for v in y],
        textposition="outside", textfont=dict(size=13, color="#374151"),
        hovertemplate="%{x}: %{y}<extra></extra>",
    ))
    _base(fig, titulo, ylabel, xlabel)
    fig.update_xaxes(type="category")
    fig.update_yaxes(rangemode="tozero")
    return fig


def barras_agrupadas(tabla, titulo="", ylabel="Cantidad", xlabel=""):
    """Barras agrupadas: filas de la tabla en el eje X, una barra por columna."""
    x = [str(i) for i in tabla.index]
    paleta = ["#F4A6A9", ROJO, "#8E1116", AZUL, "#5B8FD4"]
    fig = go.Figure()
    for j, col in enumerate(tabla.columns):
        y = tabla[col].values
        fig.add_bar(
            name=f"Test {col}", x=x, y=y, marker_color=paleta[j % len(paleta)],
            text=[f"{int(v)}" if pd.notna(v) else "" for v in y],
            textposition="outside", textfont=dict(size=11),
            hovertemplate="%{x} · Test " + str(col) + ": %{y}<extra></extra>",
        )
    _base(fig, titulo, ylabel, xlabel)
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08)
    fig.update_xaxes(type="category")
    fig.update_yaxes(rangemode="tozero")
    return fig


def boxplot(series_dict, titulo="", ylabel="", xlabel="", puntos=True, unidad=""):
    """Boxplot por grupo + punto azul = promedio (estilo informe)."""
    fig = go.Figure()
    grupos, medias = [], []
    for g, vals in series_dict.items():
        v = pd.Series(vals).dropna()
        if v.empty:
            continue
        grupos.append(str(g))
        medias.append(v.mean())
        fig.add_trace(go.Box(
            y=v, name=str(g), marker_color=ROJO, line=dict(color=ROJO, width=1.5),
            fillcolor="rgba(225,27,34,0.06)",
            boxpoints="all" if puntos else "outliers",
            jitter=0.5, pointpos=0,
            marker=dict(size=4, color="rgba(225,27,34,0.35)"),
            hovertemplate="%{x}<br>%{y:.2f} " + unidad + "<extra></extra>",
            showlegend=False,
        ))
    # Promedios como puntos azules
    if grupos:
        fig.add_trace(go.Scatter(
            x=grupos, y=medias, mode="markers", name="Promedio",
            marker=dict(color=AZUL, size=9, line=dict(color="white", width=1.5)),
            hovertemplate="Promedio %{x}: %{y:.2f} " + unidad + "<extra></extra>",
        ))
    _base(fig, titulo, ylabel, xlabel)
    fig.update_xaxes(type="category")
    fig.update_yaxes(rangemode="tozero")
    return fig


def barras_izq_der(tabla, titulo="", ylabel="", xlabel="", unidad=""):
    """Barras agrupadas IZQUIERDO vs DERECHO con etiquetas de valor."""
    x = [str(i) for i in tabla.index]
    fig = go.Figure()
    colores = {"IZQUIERDO": ROJO, "DERECHO": AZUL}
    for col in [c for c in ["IZQUIERDO", "DERECHO"] if c in tabla.columns]:
        y = tabla[col].values
        fig.add_bar(
            name=col, x=x, y=y, marker_color=colores[col],
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in y],
            textposition="outside", textfont=dict(size=11),
            hovertemplate="%{x} · " + col + ": %{y:.1f} " + unidad + "<extra></extra>",
        )
    _base(fig, titulo, ylabel, xlabel)
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.1)
    fig.update_xaxes(type="category")
    fig.update_yaxes(rangemode="tozero")
    return fig


def barras_apiladas_pct(tabla, titulo="", xlabel="% de jugadores"):
    """Barras horizontales 100% del pie dominante por grupo."""
    y = [str(i) for i in tabla.index]
    colores = {"DERECHO": AZUL, "IZQUIERDO": ROJO, "SIN DATOS": GRIS_CLARO}
    fig = go.Figure()
    for col in [c for c in ["DERECHO", "IZQUIERDO", "SIN DATOS"] if c in tabla.columns]:
        vals = tabla[col].values
        fig.add_bar(
            name=col, y=y, x=vals, orientation="h",
            marker_color=colores[col],
            text=[f"{v:.0f}%" if pd.notna(v) and v >= 8 else "" for v in vals],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(size=11, color="white"),
            hovertemplate="%{y} · " + col + ": %{x:.0f}%<extra></extra>",
        )
    _base(fig, titulo, "", xlabel)
    fig.update_layout(barmode="stack")
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    return fig


def burbujas_posicion(df, valor_key="altura", titulo="", ylabel="Altura (cm)"):
    """Distribución por posición: cada jugador es una burbuja; tamaño según
    categoría (más grande = mayor / 2005)."""
    orden_cat = {c: i for i, c in enumerate(
        ["2012", "2011", "2010", "2009", "2008", "2007", "2006", "3a"])}
    d = df.copy()
    d["_size"] = d.get("cat", "").map(lambda c: orden_cat.get(str(c), 3)) + 3
    posiciones = sorted(d["pos"].dropna().unique().tolist())
    fig = go.Figure()
    for pos in posiciones:
        sub = d[d["pos"] == pos]
        fig.add_trace(go.Scatter(
            x=[pos] * len(sub), y=sub[valor_key],
            mode="markers",
            marker=dict(size=sub["_size"] * 1.6, color="rgba(225,27,34,0.30)",
                        line=dict(color=ROJO, width=0.5)),
            name=pos, showlegend=False,
            customdata=sub.get("jugador", pd.Series([""] * len(sub))),
            hovertemplate="%{customdata}<br>" + str(pos) + ": %{y:.1f}<extra></extra>",
        ))
        # promedio por posición
        m = sub[valor_key].mean()
        fig.add_trace(go.Scatter(
            x=[pos], y=[m], mode="markers",
            marker=dict(color=AZUL, size=11, line=dict(color="white", width=1.5)),
            name="Promedio", showlegend=False,
            hovertemplate="Promedio " + str(pos) + ": %{y:.1f}<extra></extra>",
        ))
    _base(fig, titulo, ylabel, "Posición")
    fig.update_yaxes(rangemode="tozero")
    return fig


def comparador_barras_linea(test_ids, izq, der, linea, labels, titulo="",
                            ylabel="", linea_label="Asimetría %", unidad=""):
    """Barras Izq/Der por TEST_ID + línea (asimetría o imbalance) en eje secundario."""
    x = [str(t) for t in test_ids]
    fig = go.Figure()
    fig.add_bar(name=labels[0], x=x, y=izq, marker_color=ROJO,
                text=[f"{v:.1f}" if pd.notna(v) else "" for v in izq],
                textposition="outside", textfont=dict(size=10),
                hovertemplate="Test %{x} · " + labels[0] + ": %{y:.1f}<extra></extra>")
    fig.add_bar(name=labels[1], x=x, y=der, marker_color="#F4A6A9",
                text=[f"{v:.1f}" if pd.notna(v) else "" for v in der],
                textposition="outside", textfont=dict(size=10),
                hovertemplate="Test %{x} · " + labels[1] + ": %{y:.1f}<extra></extra>")
    fig.add_trace(go.Scatter(
        name=linea_label, x=x, y=linea, mode="lines+markers+text",
        line=dict(color=AZUL, width=3), marker=dict(size=8),
        text=[f"{v:.1f}" if pd.notna(v) else "" for v in linea],
        textposition="top center", textfont=dict(size=11, color=AZUL),
        yaxis="y2",
        hovertemplate="Test %{x} · " + linea_label + ": %{y:.1f}<extra></extra>",
    ))
    _base(fig, titulo, ylabel, "TEST_ID")
    fig.update_layout(
        barmode="group",
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    title=linea_label, rangemode="tozero"),
    )
    fig.update_yaxes(rangemode="tozero")
    return fig
