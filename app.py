"""
app.py
======
Aplicación principal — Base de Datos Físicos Juveniles (Club Atlético Unión).

Estructura:
  1. Login (escudo centrado, fondo blanco, acentos rojo/azul)
  2. Sidebar con escudo + navegación + selector de categorías
  3. Sección "Resumen General" (tarjetas por categoría + tabla matriz)
  4. Sección "Análisis por Categoría" con pestañas:
        - CMJ
        - Nórdico
        - Resumen Jugador (evolución, comparar, radar)

Cada sección puede exportarse a PDF con el botón de imprimir.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st

import config
import auth
import data_loader
import analysis
import charts
import styles

# ----------------------------------------------------------------------------
# CONFIG DE PÁGINA
# ----------------------------------------------------------------------------
RUTA_ESCUDO = os.path.join(os.path.dirname(__file__), "assets", "escudo_union.png")

st.set_page_config(
    page_title=config.TITULO_APP,
    page_icon=RUTA_ESCUDO if os.path.exists(RUTA_ESCUDO) else "⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.inyectar_css()


# ----------------------------------------------------------------------------
# ESTADO DE SESIÓN
# ----------------------------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = None


# ----------------------------------------------------------------------------
# LOGIN
# ----------------------------------------------------------------------------
def pantalla_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(styles.escudo_html(RUTA_ESCUDO, width=180), unsafe_allow_html=True)
        st.markdown(
            f"<h2 style='text-align:center;color:{config.AZUL};margin-bottom:0'>{config.NOMBRE_CLUB}</h2>"
            f"<p style='text-align:center;color:{config.ROJO};font-weight:700;margin-top:4px'>"
            f"{config.TITULO_APP}</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar", use_container_width=True):
            info = auth.validar_login(usuario.strip(), password)
            if info:
                st.session_state.auth = info
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
        st.markdown(
            "<p style='text-align:center;color:#9CA3AF;font-size:.75rem;margin-top:1.5rem'>"
            "Acceso restringido · Cuerpo Técnico</p>",
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------------------
# HELPERS DE UI
# ----------------------------------------------------------------------------
def titulo_principal():
    st.markdown(f"<div class='titulo-principal'>{config.TITULO_APP}</div>", unsafe_allow_html=True)
    u = st.session_state.auth
    st.markdown(f"<div class='subtitulo'>Usuario: <b>{u['usuario']}</b> · {u['rol']}</div>",
                unsafe_allow_html=True)


def fila_tarjetas(resumen, metricas, azul=False):
    """Muestra una fila de tarjetas (una por métrica)."""
    cols = st.columns(len(metricas))
    for i, m in enumerate(metricas):
        r = resumen.get(m["key"], {})
        with cols[i]:
            st.markdown(
                styles.tarjeta_metrica(
                    m["label"], r.get("prom"), r.get("min"), r.get("max"),
                    decimales=m["decimals"], azul=azul,
                ),
                unsafe_allow_html=True,
            )


def filtros_cascada(df, key_prefix, cols_orden):
    """Renderiza multiselects en cascada. Cada filtro depende de los anteriores.
    Devuelve (df_filtrado, selecciones)."""
    filtrado = df.copy()
    n = len(cols_orden)
    fila1 = cols_orden[: (n + 1) // 2]
    fila2 = cols_orden[(n + 1) // 2:]
    selecciones = {}

    for grupo in (fila1, fila2):
        if not grupo:
            continue
        cols = st.columns(len(grupo))
        for i, (col, label) in enumerate(grupo):
            with cols[i]:
                if col in filtrado.columns:
                    opts = analysis.opciones_disponibles(filtrado, col)
                    key = f"{key_prefix}_{col}"
                    # sanear selección previa que ya no es válida
                    prev = [v for v in st.session_state.get(key, []) if v in opts]
                    st.session_state[key] = prev
                    if col == "cat":
                        sel = st.multiselect(label, opts, key=key,
                                             format_func=config.etiqueta_categoria)
                    else:
                        sel = st.multiselect(label, opts, key=key)
                else:
                    sel = []
                    st.caption(f"({label} no disponible)")
                selecciones[col] = sel
            if sel:
                filtrado = filtrado[filtrado[col].isin(sel)]
    return filtrado, selecciones


ORDEN_FILTROS = [
    ("anio", "Año"),
    ("fecha", "Fecha"),
    ("pos", "Posición"),
    ("cat", "Categoría"),
    ("test_id", "Test ID"),
    ("jugador", "Jugador"),
]


def tabla_listado(df, metricas, key):
    """Tabla con datos de cada test (jugador, año, cat, pos, test_id, fecha + métricas)."""
    cols_base = [("jugador", "JUGADOR"), ("anio", "AÑO"), ("cat", "CAT"),
                 ("pos", "POS"), ("test_id", "TEST_ID"), ("fecha", "FECHA")]
    columnas = [c for c, _ in cols_base if c in df.columns]
    columnas += [m["key"] for m in metricas if m["key"] in df.columns]
    if not columnas:
        st.info("Sin columnas disponibles.")
        return
    vista = df[columnas].copy()
    rename = {c: lbl for c, lbl in cols_base}
    rename.update({m["key"]: m["label"] for m in metricas})
    vista = vista.rename(columns=rename)
    # redondeo
    for m in metricas:
        if m["label"] in vista.columns:
            vista[m["label"]] = vista[m["label"]].round(m["decimals"])
    st.dataframe(vista, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------------
# SECCIÓN 1: RESUMEN GENERAL
# ----------------------------------------------------------------------------
def seccion_resumen(df_cmj, df_nordico, cats_disponibles):
    st.markdown("## 📊 Resumen General")
    st.caption("Referencia general del club: promedios de todas las categorías. "
               "Visible para todo el cuerpo técnico.")
    styles.boton_imprimir()

    # Filtros: año y (opcional) categorías a mostrar. Por defecto, todas.
    c1, c2 = st.columns([1, 1.4])
    with c1:
        anios = sorted(set(
            analysis.opciones_disponibles(df_cmj, "anio") +
            analysis.opciones_disponibles(df_nordico, "anio")
        ))
        anios_sel = st.multiselect("Año (uno o varios)", anios, default=anios, key="res_anio")
    with c2:
        cats_sel = st.multiselect(
            "Categorías a mostrar", cats_disponibles, default=cats_disponibles,
            key="res_cats", format_func=config.etiqueta_categoria)
    if not cats_sel:
        cats_sel = cats_disponibles

    dcj = df_cmj[df_cmj["anio"].isin(anios_sel)] if anios_sel and "anio" in df_cmj.columns else df_cmj
    dn = df_nordico[df_nordico["anio"].isin(anios_sel)] if anios_sel and "anio" in df_nordico.columns else df_nordico

    # --- Tarjetas por categoría ---
    for cat in cats_sel:
        st.markdown(f"<div class='cat-header'>Categoría {config.etiqueta_categoria(cat)}</div>",
                    unsafe_allow_html=True)
        dcj_c = dcj[dcj["cat"] == cat] if "cat" in dcj.columns else pd.DataFrame()
        dn_c = dn[dn["cat"] == cat] if "cat" in dn.columns else pd.DataFrame()

        res_cmj = analysis.resumen_metricas(dcj_c, config.CMJ_METRICS)
        res_nor = analysis.resumen_metricas(dn_c, config.NORDICO_METRICS)

        st.markdown("**Saltos (CMJ)**")
        fila_tarjetas(res_cmj, config.CMJ_METRICS, azul=False)
        st.markdown("**Nórdico**")
        fila_tarjetas(res_nor, config.NORDICO_METRICS, azul=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # --- Tabla matriz: categorías x métricas ---
    st.markdown("### Tabla resumen (todas las categorías)")
    filas = {}
    for cat in cats_sel:
        dcj_c = dcj[dcj["cat"] == cat] if "cat" in dcj.columns else pd.DataFrame()
        dn_c = dn[dn["cat"] == cat] if "cat" in dn.columns else pd.DataFrame()
        fila = {}
        for m in config.CMJ_METRICS:
            fila[m["label"]] = dcj_c[m["key"]].mean() if m["key"] in dcj_c.columns else np.nan
        for m in config.NORDICO_METRICS:
            fila[m["label"]] = dn_c[m["key"]].mean() if m["key"] in dn_c.columns else np.nan
        filas[config.etiqueta_categoria(cat)] = fila

    matriz = pd.DataFrame(filas).T
    if not matriz.empty:
        dec = {m["label"]: m["decimals"] for m in config.ALL_METRICS}
        hb = {m["label"]: m["higher_better"] for m in config.ALL_METRICS}
        st.markdown(styles.tabla_matriz_html(matriz, decimales_por_col=dec, higher_better=hb),
                    unsafe_allow_html=True)
    else:
        st.info("No hay datos para las categorías seleccionadas.")


# ----------------------------------------------------------------------------
# SECCIÓN 2: ANÁLISIS POR CATEGORÍA
# ----------------------------------------------------------------------------
def tab_test(df, metricas, titulo, key_prefix, azul=False):
    """Pestaña genérica para CMJ o Nórdico."""
    st.markdown(f"### {titulo}")
    styles.boton_imprimir()

    df_f, _ = filtros_cascada(df, key_prefix, ORDEN_FILTROS)

    if df_f.empty:
        st.info("No hay datos para los filtros seleccionados.")
        return

    # Tarjetas resumen
    st.markdown("#### Resumen (promedio · mín · máx)")
    res = analysis.resumen_metricas(df_f, metricas)
    fila_tarjetas(res, metricas, azul=azul)

    # Tabla por posición
    st.markdown("#### Promedio por posición")
    mp = analysis.matriz_por_grupo(df_f, "pos", metricas, agg="mean")
    if not mp.empty:
        dec = {m["label"]: m["decimals"] for m in metricas}
        hb = {m["label"]: m["higher_better"] for m in metricas}
        st.markdown(styles.tabla_matriz_html(mp, decimales_por_col=dec, higher_better=hb),
                    unsafe_allow_html=True)
    else:
        st.caption("Sin datos de posición.")

    # Tabla de jugadores
    st.markdown("#### Detalle por test")
    tabla_listado(df_f, metricas, key=f"{key_prefix}_tabla")


def tab_resumen_jugador(df_cmj, df_nordico, df_cmj_full, df_nordico_full, key_prefix):
    st.markdown("### Resumen Jugador")
    styles.boton_imprimir()

    # Filtros en cascada (sobre CMJ; sirven para acotar jugador/fecha)
    base = df_cmj if not df_cmj.empty else df_nordico
    df_f, sel = filtros_cascada(base, key_prefix, ORDEN_FILTROS)

    jugadores = analysis.opciones_disponibles(df_f, "jugador")
    if not jugadores:
        st.info("No hay jugadores para los filtros seleccionados.")
        return
    jugador = st.selectbox("Seleccioná un jugador", jugadores, key=f"{key_prefix}_jug")

    # Datos del jugador en ambas bases (respetando filtros de año/fecha si aplican)
    anios_sel = sel.get("anio", [])
    dcj = df_cmj[df_cmj["jugador"] == jugador] if "jugador" in df_cmj.columns else pd.DataFrame()
    dn = df_nordico[df_nordico["jugador"] == jugador] if "jugador" in df_nordico.columns else pd.DataFrame()
    if anios_sel:
        if "anio" in dcj.columns:
            dcj = dcj[dcj["anio"].isin(anios_sel)]
        if "anio" in dn.columns:
            dn = dn[dn["anio"].isin(anios_sel)]

    # --- Datos personales ---
    st.markdown("#### Datos del jugador")
    cols_pers = [("jugador", "JUGADOR"), ("fec_nac", "FEC NAC"), ("anio", "AÑO"),
                 ("cat", "CAT"), ("dni", "DNI"), ("pos", "POS"),
                 ("test_id", "TEST_ID"), ("fecha", "FECHA")]
    fuente = dcj if not dcj.empty else dn
    presentes = [(c, l) for c, l in cols_pers if c in fuente.columns]
    if presentes:
        vista = fuente[[c for c, _ in presentes]].rename(columns=dict(presentes))
        st.dataframe(vista, use_container_width=True, hide_index=True)

    # --- Tarjetas CMJ ---
    st.markdown("#### CMJ — Resumen")
    fila_tarjetas(analysis.resumen_metricas(dcj, config.CMJ_METRICS), config.CMJ_METRICS)

    # --- Evolución CMJ (máximo por fecha) ---
    st.markdown("#### Evolución CMJ (valor máximo por fecha)")
    ev_cmj = analysis.valores_max_por_fecha(dcj, config.CMJ_METRICS)
    if not ev_cmj.empty:
        st.plotly_chart(charts.linea_evolucion(ev_cmj, config.CMJ_METRICS, "Evolución CMJ"),
                        use_container_width=True)
        # resumen debajo
        primeras = ev_cmj.iloc[0]
        ultimas = ev_cmj.iloc[-1]
        resumen_txt = []
        for m in config.CMJ_METRICS:
            if m["key"] in ev_cmj.columns and pd.notna(primeras[m["key"]]) and pd.notna(ultimas[m["key"]]):
                ini, fin = primeras[m["key"]], ultimas[m["key"]]
                if ini != 0:
                    delta = (fin - ini) / abs(ini) * 100
                    signo = "▲" if delta >= 0 else "▼"
                    resumen_txt.append(f"**{m['label']}**: {signo} {delta:+.1f}% (de {ini:.{m['decimals']}f} a {fin:.{m['decimals']}f})")
        if resumen_txt:
            st.caption("Variación entre el primer y último test: " + " · ".join(resumen_txt))
    else:
        st.caption("Sin datos de CMJ para este jugador.")

    # --- Nórdico: barras Izq/Der + evolución asimetría y masa ---
    st.markdown("#### Nórdico")
    ev_nor = analysis.valores_max_por_fecha(dn, config.NORDICO_METRICS)
    if not ev_nor.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.barras_fza_izq_der(ev_nor), use_container_width=True)
        with c2:
            st.plotly_chart(charts.linea_simple(ev_nor, "dif", "Dif (%)", config.ROJO,
                            "Evolución Asimetría (%)"), use_container_width=True)
        st.plotly_chart(charts.linea_simple(ev_nor, "masa", "Masa Alcanzada (%)", config.AZUL,
                        "Evolución Masa Alcanzada (%)"), use_container_width=True)
    else:
        st.caption("Sin datos de Nórdico para este jugador.")

    # --- COMPARAR ---
    st.markdown("#### 🔁 COMPARAR")
    with st.expander("Abrir comparador de tests", expanded=False):
        # Usa los datos permitidos (df_cmj/df_nordico ya vienen filtrados por categoría)
        comparador(df_cmj, df_nordico, key_prefix)

    # --- Tabla resumen jugador (variables en columnas, fechas en filas) ---
    st.markdown("#### Tabla resumen del jugador")
    tabla = tabla_resumen_jugador(dcj, dn)
    if not tabla.empty:
        dec = {m["label"]: m["decimals"] for m in config.ALL_METRICS}
        hb = {m["label"]: m["higher_better"] for m in config.ALL_METRICS}
        st.markdown(styles.tabla_matriz_html(tabla, decimales_por_col=dec, higher_better=hb),
                    unsafe_allow_html=True)

    # --- RADAR ---
    st.markdown("#### 🕸️ Perfil Radar")
    radar_jugador(jugador, dcj, dn, df_cmj_full, df_nordico_full, key_prefix)


def tabla_resumen_jugador(dcj, dn):
    """Variables en columnas (cmj+nordico), fechas en filas, valor máx por fecha."""
    partes = []
    if not dcj.empty:
        g = analysis.valores_max_por_fecha(dcj, config.CMJ_METRICS)
        if not g.empty:
            g = g.set_index("fecha")
            ren = {m["key"]: m["label"] for m in config.CMJ_METRICS}
            partes.append(g.rename(columns=ren)[[v for v in ren.values() if v in g.rename(columns=ren).columns]])
    if not dn.empty:
        g = analysis.valores_max_por_fecha(dn, config.NORDICO_METRICS)
        if not g.empty:
            g = g.set_index("fecha")
            ren = {m["key"]: m["label"] for m in config.NORDICO_METRICS}
            partes.append(g.rename(columns=ren)[[v for v in ren.values() if v in g.rename(columns=ren).columns]])
    if not partes:
        return pd.DataFrame()
    out = pd.concat(partes, axis=1)
    return out


def comparador(df_cmj_full, df_nordico_full, key_prefix):
    """Comparar métricas entre dos (jugador, fecha)."""
    todas = config.CMJ_METRICS + config.NORDICO_METRICS
    labels = [m["label"] for m in todas]
    sel_labels = st.multiselect("Métricas a comparar (sugerido: 3 de CMJ + 3 de Nórdico)",
                                labels, default=labels[:6], key=f"{key_prefix}_cmp_met")
    metricas_sel = [m for m in todas if m["label"] in sel_labels]

    def selector(lado):
        jugs = analysis.opciones_disponibles(df_cmj_full, "jugador") or \
               analysis.opciones_disponibles(df_nordico_full, "jugador")
        jug = st.selectbox(f"Jugador {lado}", jugs, key=f"{key_prefix}_cmp_jug_{lado}")
        fechas_cmj = df_cmj_full[df_cmj_full.get("jugador") == jug]["fecha"].dropna().unique().tolist() \
            if "jugador" in df_cmj_full.columns else []
        fechas_nor = df_nordico_full[df_nordico_full.get("jugador") == jug]["fecha"].dropna().unique().tolist() \
            if "jugador" in df_nordico_full.columns else []
        fechas = sorted(set(fechas_cmj) | set(fechas_nor))
        fecha = st.selectbox(f"Fecha {lado}", fechas, key=f"{key_prefix}_cmp_fec_{lado}") if fechas else None
        return jug, fecha

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Referencia A**")
        jugA, fecA = selector("A")
    with c2:
        st.markdown("**Comparar con B**")
        jugB, fecB = selector("B")

    def valor(jug, fec, m):
        df = df_cmj_full if m in config.CMJ_METRICS else df_nordico_full
        if "jugador" not in df.columns or m["key"] not in df.columns:
            return np.nan
        sub = df[df["jugador"] == jug]
        if fec is not None and "fecha" in sub.columns:
            sub = sub[sub["fecha"] == fec]
        return analysis.valor_unico(sub, m["key"], "max")

    filas = []
    for m in metricas_sel:
        a = valor(jugA, fecA, m)
        b = valor(jugB, fecB, m)
        if pd.notna(a) and pd.notna(b) and a != 0:
            diff = (b - a) / abs(a) * 100
            diff_txt = f"{diff:+.1f}%"
        else:
            diff_txt = "—"
        filas.append({
            "Métrica": m["label"],
            f"A · {jugA} ({fecA})": None if pd.isna(a) else round(a, m["decimals"]),
            f"B · {jugB} ({fecB})": None if pd.isna(b) else round(b, m["decimals"]),
            "Dif. % (B vs A)": diff_txt,
        })
    if filas:
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
        st.caption("La diferencia se calcula como (B − A) / A × 100. "
                   "Valores positivos indican que B es mayor que A; negativos, menor. "
                   "Recordá que en **Dif (%)** del nórdico un valor más bajo es mejor (menos asimetría).")


def radar_jugador(jugador, dcj, dn, df_cmj_full, df_nordico_full, key_prefix):
    metricas = config.ALL_METRICS
    # Perfil del jugador (máximo por métrica)
    perfil_jug = {}
    for m in config.CMJ_METRICS:
        perfil_jug[m["key"]] = analysis.valor_unico(dcj, m["key"], "max")
    for m in config.NORDICO_METRICS:
        perfil_jug[m["key"]] = analysis.valor_unico(dn, m["key"], "max")

    # Posición y categoría del jugador
    pos_jug = None
    cat_jug = None
    fuente = dcj if not dcj.empty else dn
    if "pos" in fuente.columns and not fuente.empty:
        pos_jug = fuente["pos"].mode().iloc[0] if not fuente["pos"].mode().empty else None
    if "cat" in fuente.columns and not fuente.empty:
        cat_jug = fuente["cat"].mode().iloc[0] if not fuente["cat"].mode().empty else None

    opcion = st.selectbox("Comparar contra:",
                          ["PROM POS", "PROM EQUIPO", "PROM POS 3a", "PROM 3a"],
                          key=f"{key_prefix}_radar_ref")

    # df de la categoría del jugador (para POS / EQUIPO)
    dcj_cat = df_cmj_full[df_cmj_full.get("cat") == cat_jug] if "cat" in df_cmj_full.columns else df_cmj_full
    dn_cat = df_nordico_full[df_nordico_full.get("cat") == cat_jug] if "cat" in df_nordico_full.columns else df_nordico_full

    if opcion in ("PROM POS", "PROM EQUIPO"):
        ref = analysis.referencia_radar(dcj_cat, dn_cat, opcion, pos=pos_jug)
    else:  # 3a usa dataset completo
        ref = analysis.referencia_radar(df_cmj_full, df_nordico_full, opcion, pos=pos_jug)

    perfiles = {jugador: perfil_jug, opcion: ref}
    escalados = analysis.escalar_para_radar(perfiles, df_cmj_full, df_nordico_full, metricas)
    st.plotly_chart(charts.radar(escalados, metricas,
                    f"{jugador} vs {opcion}"), use_container_width=True)
    st.caption("Valores escalados 0–100 según el rango de todo el plantel. "
               "En todas las métricas, **más área = mejor** (en *Dif %* la escala está invertida "
               "porque menos asimetría es mejor).")


# ----------------------------------------------------------------------------
# APP PRINCIPAL (post-login)
# ----------------------------------------------------------------------------
def app_principal():
    user = st.session_state.auth

    # Cargar datos
    with st.spinner("Cargando bases de datos..."):
        df_cmj_full, df_nordico_full, error = data_loader.cargar_datos()

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown(styles.escudo_html(RUTA_ESCUDO, width=120), unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;font-weight:700;color:{config.AZUL}'>"
                    f"{config.NOMBRE_CLUB}</div>", unsafe_allow_html=True)
        st.markdown("---")

        seccion = st.radio("Navegación",
                           ["📊 Resumen General", "🔬 Análisis por Categoría"],
                           key="nav")
        st.markdown("---")

        cats_perm = auth.categorias_permitidas(user, config.CATEGORIAS)
        if user.get("acceso_total"):
            cats_sel = st.multiselect(
                "Categorías", cats_perm, default=cats_perm, key="cats_sel",
                format_func=config.etiqueta_categoria)
        else:
            cats_sel = cats_perm
            etiqueta = config.etiqueta_categoria(cats_perm[0]) if cats_perm else "—"
            st.info(f"Categoría asignada: **{etiqueta}**")
        st.markdown("---")
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.auth = None
            st.rerun()

    titulo_principal()

    if error:
        st.error("⚠️ Hubo un problema al cargar los datos: " + error)
        st.info("Verificá que las URLs de Google Sheets en config.py estén publicadas como CSV "
                "y sean accesibles.")
    if df_cmj_full.empty and df_nordico_full.empty:
        st.warning("No se cargaron datos. Revisá la conexión y las URLs.")
        return

    if seccion.startswith("📊"):
        # Resumen General: referencia para TODOS, con todas las categorías.
        seccion_resumen(df_cmj_full, df_nordico_full, config.CATEGORIAS)
    else:
        # Análisis por Categoría: datos detallados, restringidos por permiso.
        dcj = df_cmj_full[df_cmj_full["cat"].isin(cats_sel)] if "cat" in df_cmj_full.columns else df_cmj_full
        dn = df_nordico_full[df_nordico_full["cat"].isin(cats_sel)] if "cat" in df_nordico_full.columns else df_nordico_full
        if not cats_sel:
            st.warning("Seleccioná al menos una categoría en la barra lateral.")
            return
        st.markdown("## 🔬 Análisis por Categoría")
        t1, t2, t3 = st.tabs(["🦵 CMJ (Saltos)", "💪 Nórdico", "👤 Resumen Jugador"])
        with t1:
            tab_test(dcj, config.CMJ_METRICS, "CMJ — Saltos", "cmj", azul=False)
        with t2:
            tab_test(dn, config.NORDICO_METRICS, "Nórdico", "nor", azul=True)
        with t3:
            tab_resumen_jugador(dcj, dn, df_cmj_full, df_nordico_full, "res")


# ----------------------------------------------------------------------------
# ROUTER
# ----------------------------------------------------------------------------
if st.session_state.auth is None:
    pantalla_login()
else:
    app_principal()
