"""
charts.py
=========
Construcción de gráficos interactivos con Plotly.
"""

import plotly.graph_objects as go
import pandas as pd

import config

PALETA = [config.ROJO, config.AZUL, "#2E7D32", "#F9A825", "#6A1B9A", "#00838F"]


def _layout_base(fig, titulo=""):
    fig.update_layout(
        title=titulo,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#1f2937", size=13),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef0f2")
    fig.update_yaxes(showgrid=True, gridcolor="#eef0f2")
    return fig


def linea_evolucion(df_fechas, metricas, titulo="Evolución"):
    """df_fechas: salida de valores_max_por_fecha (col 'fecha', 'fecha_dt' + métricas)."""
    fig = go.Figure()
    if df_fechas.empty:
        return _layout_base(fig, titulo)
    x = df_fechas["fecha"]
    for i, m in enumerate(metricas):
        if m["key"] in df_fechas.columns:
            fig.add_trace(go.Scatter(
                x=x, y=df_fechas[m["key"]], mode="lines+markers",
                name=m["label"], line=dict(color=PALETA[i % len(PALETA)], width=3),
                marker=dict(size=8),
            ))
    return _layout_base(fig, titulo)


def barras_fza_izq_der(df_fechas, titulo="Fuerza Izq vs Der (Nórdico)"):
    """Barras agrupadas comparando fza izquierda y derecha por fecha."""
    fig = go.Figure()
    if df_fechas.empty:
        return _layout_base(fig, titulo)
    x = df_fechas["fecha"]
    if "fza_izq" in df_fechas.columns:
        fig.add_trace(go.Bar(x=x, y=df_fechas["fza_izq"], name="Fza Máx Izq (N)",
                             marker_color=config.AZUL))
    if "fza_der" in df_fechas.columns:
        fig.add_trace(go.Bar(x=x, y=df_fechas["fza_der"], name="Fza Máx Der (N)",
                             marker_color=config.ROJO))
    fig.update_layout(barmode="group")
    return _layout_base(fig, titulo)


def linea_simple(df_fechas, key, label, color, titulo=""):
    fig = go.Figure()
    if not df_fechas.empty and key in df_fechas.columns:
        fig.add_trace(go.Scatter(
            x=df_fechas["fecha"], y=df_fechas[key], mode="lines+markers",
            name=label, line=dict(color=color, width=3), marker=dict(size=8),
        ))
    return _layout_base(fig, titulo)


def radar(perfiles_escalados, metricas, titulo="Perfil Radar", reales=None):
    """perfiles_escalados: dict {nombre: {key: valor_0_100}}.
    reales (opcional): dict {nombre: {key: valor_real}} para mostrar en el hover."""
    fig = go.Figure()
    categorias = [m["label"] for m in metricas]
    keys = [m["key"] for m in metricas]
    decs = {m["key"]: m.get("decimals", 1) for m in metricas}

    def _fmt(v, dec):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return "—"
        return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    for i, (nombre, vals) in enumerate(perfiles_escalados.items()):
        r = [vals.get(k, 0) for k in keys]
        r_closed = r + [r[0]]
        theta_closed = categorias + [categorias[0]]
        color = PALETA[i % len(PALETA)]

        # customdata = valor real por métrica (si está disponible)
        if reales and nombre in reales:
            cd = [_fmt(reales[nombre].get(k), decs[k]) for k in keys]
            cd_closed = cd + [cd[0]]
            fig.add_trace(go.Scatterpolar(
                r=r_closed, theta=theta_closed, name=nombre, fill="toself",
                line=dict(color=color, width=2), opacity=0.6,
                customdata=cd_closed,
                hovertemplate="<b>%{theta}</b><br>Valor real: %{customdata}"
                              "<br>Escala 0–100: %{r:.0f}<extra>" + str(nombre) + "</extra>",
            ))
        else:
            fig.add_trace(go.Scatterpolar(
                r=r_closed, theta=theta_closed, name=nombre, fill="toself",
                line=dict(color=color, width=2), opacity=0.6,
            ))
    fig.update_layout(
        title=titulo,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        paper_bgcolor="white",
        font=dict(color="#1f2937"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(l=60, r=60, t=60, b=60),
    )
    return fig
