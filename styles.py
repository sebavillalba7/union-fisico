"""
styles.py
=========
Inyección de CSS (colores del club, tarjetas, tablas matriz con escala de
color) y configuración para imprimir/exportar a PDF sin cortar contenido.
"""

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import config


def inyectar_css():
    st.markdown(f"""
    <style>
    /* ---------- Base ---------- */
    .stApp {{ background-color: {config.BLANCO}; }}
    .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1300px; }}
    h1, h2, h3, h4 {{ color: {config.AZUL}; }}

    /* Título principal con franja roja */
    .titulo-principal {{
        color: {config.AZUL}; font-weight: 800; font-size: 2rem;
        border-left: 8px solid {config.ROJO}; padding-left: 14px; margin-bottom: .3rem;
    }}
    .subtitulo {{ color: {config.GRIS}; font-size: .95rem; margin-bottom: 1rem; }}

    /* ---------- Tarjetas de métricas ---------- */
    .metric-card {{
        background: #fff; border: 1px solid #e8eaed; border-top: 4px solid {config.ROJO};
        border-radius: 12px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06);
        height: 100%;
    }}
    .metric-card.azul {{ border-top: 4px solid {config.AZUL}; }}
    .metric-label {{ font-size: .8rem; color: {config.GRIS}; font-weight: 600;
                     text-transform: uppercase; letter-spacing: .3px; }}
    .metric-value {{ font-size: 1.8rem; font-weight: 800; color: {config.AZUL}; line-height: 1.1; }}
    .metric-minmax {{ font-size: .72rem; color: {config.GRIS}; margin-top: 4px; }}
    .metric-minmax .mn {{ color: {config.AZUL}; font-weight: 700; }}
    .metric-minmax .mx {{ color: {config.ROJO}; font-weight: 700; }}

    /* Encabezado de categoría */
    .cat-header {{
        background: linear-gradient(90deg, {config.ROJO}, {config.AZUL});
        color: #fff; padding: 8px 16px; border-radius: 8px; font-weight: 700;
        font-size: 1.15rem; margin: 18px 0 12px 0;
    }}

    /* ---------- Tablas matriz ---------- */
    .matriz-wrap {{ overflow-x: auto; }}
    table.matriz {{ border-collapse: collapse; width: 100%; font-size: .85rem; }}
    table.matriz th {{ background: {config.AZUL}; color: #fff; padding: 8px 10px;
                       text-align: center; position: sticky; top: 0; }}
    table.matriz td {{ padding: 7px 10px; text-align: center; border-bottom: 1px solid #eee; }}
    table.matriz td.idx {{ text-align: left; font-weight: 700; color: {config.AZUL};
                           background: {config.GRIS_CLARO}; }}

    /* Botón login / acento */
    .stButton > button {{ background: {config.ROJO}; color: #fff; border: none;
        border-radius: 8px; font-weight: 700; padding: .5rem 1.2rem; }}
    .stButton > button:hover {{ background: {config.AZUL}; color: #fff; }}

    /* ---------- IMPRESIÓN / PDF ---------- */
    @media print {{
        /* Ocultar barra lateral y controles de Streamlit al imprimir */
        section[data-testid="stSidebar"], header, footer,
        [data-testid="stToolbar"], [data-testid="stDecoration"],
        .no-print {{ display: none !important; }}
        .stApp {{ background: #fff !important; }}
        .block-container {{ max-width: 100% !important; padding: 0 !important; }}

        /* Evitar que se corten tarjetas, tablas y gráficos entre hojas */
        .metric-card, table.matriz, .cat-header, .grafico-box,
        .stPlotlyChart, .element-container {{
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }}
        @page {{ size: A4 portrait; margin: 12mm; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def boton_imprimir(etiqueta="🖨️ Exportar a PDF / Imprimir"):
    """Botón que abre el diálogo de impresión del navegador (Guardar como PDF)."""
    components.html(f"""
        <button onclick="window.parent.print()" style="
            background:{config.AZUL}; color:#fff; border:none; border-radius:8px;
            font-weight:700; padding:.5rem 1.1rem; cursor:pointer; font-size:.9rem;">
            {etiqueta}
        </button>
        <div style="font-size:.72rem;color:#6B7280;margin-top:4px;">
            En el diálogo elegí <b>"Guardar como PDF"</b>. También podés usar Ctrl+P.
        </div>
    """, height=70)


def tarjeta_metrica(label, valor, mn, mx, decimales=1, azul=False):
    """Devuelve el HTML de una tarjeta de métrica (promedio + min/max)."""
    def fmt(v):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return "—"
        return f"{v:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    clase = "metric-card azul" if azul else "metric-card"
    return f"""
    <div class="{clase}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{fmt(valor)}</div>
        <div class="metric-minmax">
            mín <span class="mn">{fmt(mn)}</span> &nbsp;·&nbsp;
            máx <span class="mx">{fmt(mx)}</span>
        </div>
    </div>"""


def tabla_matriz_html(df, decimales_por_col=None, escala_color=True, higher_better=None):
    """
    Genera una tabla HTML estilo matriz con escala de color por columna.
    - df: DataFrame (index = filas, columns = variables)
    - decimales_por_col: dict {columna: decimales}
    - higher_better: dict {columna: bool} para orientar la escala de color
    """
    if df is None or df.empty:
        return "<p style='color:#6B7280'>Sin datos para mostrar.</p>"

    decimales_por_col = decimales_por_col or {}
    higher_better = higher_better or {}

    # Calcular min/max por columna para la escala
    rangos = {c: (df[c].min(), df[c].max()) for c in df.columns}

    def color_celda(col, val):
        if not escala_color or pd.isna(val):
            return ""
        lo, hi = rangos[col]
        if hi == lo:
            return ""
        pct = (val - lo) / (hi - lo)
        if not higher_better.get(col, True):
            pct = 1 - pct  # invertir si menos es mejor
        # Verde (bueno) -> Amarillo -> Rojo (malo)
        if pct >= 0.5:
            # verde a amarillo
            r = int(255 * (1 - (pct - 0.5) * 2))
            g = 200
            b = 80
        else:
            r = 230
            g = int(120 + 160 * (pct * 2))
            b = 80
        return f"background-color: rgba({r},{g},{b},0.55);"

    html = ["<div class='matriz-wrap'><table class='matriz'>"]
    # encabezado
    html.append("<thead><tr><th></th>")
    for c in df.columns:
        html.append(f"<th>{c}</th>")
    html.append("</tr></thead><tbody>")
    # filas
    for idx, fila in df.iterrows():
        html.append(f"<tr><td class='idx'>{idx}</td>")
        for c in df.columns:
            val = fila[c]
            dec = decimales_por_col.get(c, 1)
            if pd.isna(val):
                txt = "—"
                estilo = ""
            else:
                txt = f"{val:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
                estilo = color_celda(c, val)
            html.append(f"<td style='{estilo}'>{txt}</td>")
        html.append("</tr>")
    html.append("</tbody></table></div>")
    return "".join(html)
