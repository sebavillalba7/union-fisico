# Base de Datos Físicos - Juveniles · Club Atlético Unión

Aplicación web (Streamlit) para el control de información física de las
categorías inferiores del club. Lee en vivo las bases de datos de evaluaciones
**CMJ** y **Nórdico** publicadas desde Google Sheets.

## Características

- Login con usuarios y contraseñas por categoría y para coordinadores.
- Control de acceso: coordinadores ven todo, cada categoría ve solo sus datos.
- **Resumen General**: referencia visible para **todos** (promedios de todas las categorías) con tarjetas + tabla matriz con escala de color.
- **Análisis por Categoría** con pestañas:
  - **CMJ**: filtros en cascada, tarjetas, promedio por posición, detalle por test.
  - **Nórdico**: ídem con las métricas de fuerza/asimetría.
  - **Resumen Jugador**: datos personales, evolución, comparador, tabla resumen y radar.
- Exportación a PDF (impresión sin cortes) en cada sección.

> **Categorías:** son los años de nacimiento `2006` … `2012`. La **3ª** (Tercera) corresponde a los nacidos en **2005** y se muestra como *"3ª División (2005)"*. Si en tu planilla la columna **CAT** trae `2005`, `3ª` o `Tercera`, la app los unifica automáticamente con `3a` (ver `CAT_ALIASES` en `config.py`).

## Métricas

| Test | Métrica (planilla) | Etiqueta |
|------|--------------------|----------|
| CMJ | Jump Height (Imp-Mom) [cm] | Altura (cm) |
| CMJ | Eccentric Peak Power / BM [W/kg] | Ecc PP (W/kg) |
| CMJ | RSI-modified [m/s] | RSI-mod |
| Nórdico | L Max Force (N) | Fza Máx Izq (N) |
| Nórdico | R Max Force (N) | Fza Máx Der (N) |
| Nórdico | Max Imbalance (%) | Dif (%) |
| Nórdico | MASA ALCANZADA % | Masa Alcanzada (%) |

## Usuarios y contraseñas

> ⚠️ Cambialas antes de usarlo en serio (ver `auth.py` o `.streamlit/secrets.toml`).

**Acceso total**

| Usuario | Contraseña |
|---------|-----------|
| admin | Admin.Union2025 |
| Coordinador | Union2025.Coord |
| Coord_PFs | Union2025.PFs |
| Coord_Fza | Union2025.Fza |
| Sec-Tecnica | Union2025.SecTec |
| PF-3a | Tate3a.Total | (Tercera / 2005) |

**Solo su categoría**

| Usuario | Contraseña | Ve categoría |
|---------|-----------|--------------|
| PF-2012 | Tate2012.PF | 2012 |
| PF-2011 | Tate2011.PF | 2011 |
| PF-2010 | Tate2010.PF | 2010 |
| PF-2009 | Tate2009.PF | 2009 |
| PF-2008 | Tate2008.PF | 2008 |
| PF-2007 | Tate2007.PF | 2007 |
| PF-2006 | Tate2006.PF | 2006 |

## Ejecutar en tu computadora

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en `http://localhost:8501`.

## Ajustar columnas

Si tu planilla usa nombres de columnas distintos, editá las listas de
"candidatos" en `config.py` (sección MÉTRICAS y COMMON_COLUMNS). No hay que
tocar el resto del código.

## Estructura

```
union-fisico/
├── app.py              # App principal (login + secciones)
├── config.py           # Colores, URLs, métricas, columnas, categorías
├── auth.py             # Usuarios, contraseñas, permisos
├── data_loader.py      # Carga y normaliza los CSV de Google Sheets
├── analysis.py         # Cálculos (filtros, promedios, radar)
├── charts.py           # Gráficos Plotly
├── styles.py           # CSS, tarjetas, tablas, impresión PDF
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
└── assets/
    └── escudo_union.png
```

Ver **GUIA_PASO_A_PASO.md** para subirlo a GitHub y publicarlo gratis en Streamlit Cloud.
