"""
config.py
=========
Configuración central de la aplicación:
- Colores institucionales
- URLs de las bases de datos (Google Sheets publicadas como CSV)
- Definición de métricas (CMJ y Nórdico)
- Mapeo flexible de nombres de columnas
- Categorías

Si alguna columna de tu planilla tiene un nombre distinto al esperado,
agregalo a la lista de "candidatos" de esa columna más abajo. No hace falta
tocar el resto del código.
"""

# ----------------------------------------------------------------------------
# COLORES INSTITUCIONALES (Club Atlético Unión)
# ----------------------------------------------------------------------------
ROJO = "#E11B22"      # Rojo Unión (color principal de acento)
AZUL = "#0A3D7A"      # Azul (color secundario de acento)
BLANCO = "#FFFFFF"    # Fondo
GRIS = "#6B7280"      # Texto secundario
GRIS_CLARO = "#F3F4F6"

# ----------------------------------------------------------------------------
# URLs DE LAS BASES DE DATOS
# ----------------------------------------------------------------------------
URL_CMJ = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0w8CiSwcdg9Fe6cPxka8Y86YQfqqHFcEQiR9F4Ls6_DgU3LvvGrEUgCZTwkUkbw0oj4EANyzB7MpP/pub?gid=589925252&single=true&output=csv"
URL_NORDICO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0w8CiSwcdg9Fe6cPxka8Y86YQfqqHFcEQiR9F4Ls6_DgU3LvvGrEUgCZTwkUkbw0oj4EANyzB7MpP/pub?gid=853002356&single=true&output=csv"

# ----------------------------------------------------------------------------
# MÉTRICAS
# Cada métrica tiene:
#  - key: nombre interno (no cambiar)
#  - col: lista de posibles nombres en la planilla (el primero que aparezca se usa)
#  - label: cómo se muestra en la app
#  - higher_better: True si "más es mejor" (para escalas de color y radar)
#  - decimals: cantidad de decimales a mostrar
# ----------------------------------------------------------------------------
CMJ_METRICS = [
    {
        "key": "altura",
        "col": ["Jump Height (Imp-Mom) [cm]", "Jump Height (Imp-Mom) (cm)",
                "Jump Height (Imp-Mom)", "Altura cm", "Altura"],
        "label": "Altura (cm)",
        "higher_better": True,
        "decimals": 1,
    },
    {
        "key": "ecc_pp",
        "col": ["Eccentric Peak Power / BM [W/kg]", "Eccentric Peak Power / BM (W/kg)",
                "Eccentric Peak Power/BM [W/kg]", "Ecc PP"],
        "label": "Ecc PP (W/kg)",
        "higher_better": True,
        "decimals": 1,
    },
    {
        "key": "rsi",
        "col": ["RSI-modified [m/s]", "RSI-modified (m/s)", "RSI-modified", "RSI-m", "RSI-m2"],
        "label": "RSI-mod",
        "higher_better": True,
        "decimals": 2,
    },
]

NORDICO_METRICS = [
    {
        "key": "fza_izq",
        "col": ["L Max Force (N)", "L Max Force [N]", "Fza Max Izq", "Fza Máx Izq"],
        "label": "Fza Máx Izq (N)",
        "higher_better": True,
        "decimals": 0,
    },
    {
        "key": "fza_der",
        "col": ["R Max Force (N)", "R Max Force [N]", "Fza Max Der", "Fza Máx Der"],
        "label": "Fza Máx Der (N)",
        "higher_better": True,
        "decimals": 0,
    },
    {
        "key": "dif",
        "col": ["Max Imbalance (%)", "Max Imbalance [%]", "Dif %", "Dif (%)"],
        "label": "Dif (%)",
        "higher_better": False,   # menos asimetría es mejor
        "decimals": 1,
    },
    {
        "key": "masa",
        "col": ["MASA ALCANZADA %", "MASA ALCANZADA (%)", "MASA ALCANZADA", "Masa %"],
        "label": "Masa Alcanzada (%)",
        "higher_better": True,
        "decimals": 1,
    },
]

# Diccionarios rápidos por key
CMJ_BY_KEY = {m["key"]: m for m in CMJ_METRICS}
NORDICO_BY_KEY = {m["key"]: m for m in NORDICO_METRICS}
ALL_METRICS = CMJ_METRICS + NORDICO_METRICS

# ----------------------------------------------------------------------------
# COLUMNAS COMUNES (datos del jugador / del test)
# clave interna -> posibles nombres en la planilla
# ----------------------------------------------------------------------------
COMMON_COLUMNS = {
    "jugador":  ["JUGADOR", "Jugador", "NOMBRE", "Nombre", "APELLIDO Y NOMBRE"],
    "anio":     ["AÑO", "ANIO", "Año", "ANO", "AÑO ", "TEMPORADA"],
    "cat":      ["CAT", "CATEGORIA", "CATEGORÍA", "Categoria"],
    "pos":      ["POS", "POSICION", "POSICIÓN", "Posicion", "PUESTO"],
    "test_id":  ["TEST_ID", "TEST ID", "TESTID", "ID TEST", "ID_TEST"],
    "fecha":    ["FECHA", "Fecha", "DATE", "Date"],
    "fec_nac":  ["FEC NAC", "FEC_NAC", "FECHA NAC", "FECHA NACIMIENTO", "F NAC", "NACIMIENTO"],
    "dni":      ["DNI", "Dni", "DOCUMENTO", "DOC"],
}

# ----------------------------------------------------------------------------
# CATEGORÍAS
# El valor debe coincidir con lo que aparece en la columna CAT de tu planilla.
# Si en tu planilla las categorías figuran distinto (ej "Sub 14" en vez de "2012"),
# ajustá esta lista y el mapeo de usuarios en auth.py
# ----------------------------------------------------------------------------
CATEGORIAS = ["2006", "2007", "2008", "2009", "2010", "2011", "2012", "3a"]

# Categoría que representa a "Tercera" (para comparaciones del radar)
CATEGORIA_3A = "3a"

# ----------------------------------------------------------------------------
# TEXTOS
# ----------------------------------------------------------------------------
TITULO_APP = "Base de Datos Físicos - Juveniles"
NOMBRE_CLUB = "Club Atlético Unión"
