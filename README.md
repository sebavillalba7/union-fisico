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
- **Análisis Estadísticos** (recreación del informe Looker, con datos vivos):
  - Participación (testeados por año/categoría, asistencia por testeo).
  - CMJ: boxplots Min/Prom/Med/Max de Altura, Ecc PP y RSI por año y categoría.
  - Por posición (burbujas por categoría).
  - CMJ a 1 pie: Izq/Der, asimetrías y pie dominante.
  - Nórdico a 1 pie: ídem con fuerza máxima.
  - Comparador individual por test (asimetrías de un jugador).
  > Lee la planilla completa de ForceDecks (`URL_CMJ_FULL` en `config.py`, gid 1351515444),
  > que incluye las columnas a 1 pie. Las vistas agregadas son referencia para todos; el
  > comparador individual respeta los permisos.
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

> 🔒 **Las contraseñas YA NO están en el código.** Se cargan en **Streamlit Secrets**
> (privado, no se sube a GitHub). Copiá el contenido de `.streamlit/secrets.toml.example`
> en *Manage app → Settings → Secrets* y cambiá las claves por las reales.
>
> Si todavía no cargaste Secrets, solo funciona el usuario **`admin`** con la clave
> temporal **`CambiarEsta.2025`** para que puedas entrar y configurarlo.

**Usuarios incluidos (sus claves se definen en Secrets):**

| Usuario | Acceso | Categoría |
|---------|--------|-----------|
| admin, Coordinador, Coord_PFs, Coord_Fza, Sec-Tecnica | Total | — |
| PF-3a | Total | Tercera (2005) |
| PF-2012 … PF-2006 | Solo su categoría | 2012 … 2006 |

Cada usuario en Secrets admite: `password` (texto), opcional `password_hash` (más seguro)
y `email`. Para generar un hash: `python -c "import auth; print(auth.generar_hash('TuClave'))"`.

### Cambio de contraseña automático (opcional)

Cada usuario puede **cambiar su propia contraseña** y recuperarla con su **usuario + email**
(sin enviar correos). Se guarda cifrado en una **hoja de Google**. Hay dos formas de
conectarla y la app detecta sola cuál usaste:

- **Apps Script (recomendado, SIN tarjeta ni Google Cloud).**
- Cuenta de servicio de Google Cloud (alternativa).

Ver **`GUIA_CONTRASENAS.md`** (incluye el script `apps_script/Codigo.gs`).

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
