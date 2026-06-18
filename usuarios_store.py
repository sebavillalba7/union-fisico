"""
usuarios_store.py
=================
Almacén de usuarios con LECTURA y ESCRITURA, para que cada usuario pueda
cambiar su contraseña y quede guardada.

Soporta DOS métodos (elegí UNO en Secrets):

  MÉTODO A — Google Apps Script (RECOMENDADO, NO pide tarjeta)
  ------------------------------------------------------------
  Un script dentro de tu propia hoja, publicado como "app web".
  En Secrets:

      [usuarios_webapp]
      url = "https://script.google.com/macros/s/XXXX/exec"
      token = "un-secreto-largo-igual-al-del-script"

  MÉTODO B — Cuenta de servicio de Google Cloud (requiere proyecto en Cloud)
  -------------------------------------------------------------------------
      [gcp_service_account]
      ... (JSON de la cuenta de servicio)
      [usuarios_sheet]
      url = "https://docs.google.com/spreadsheets/d/XXXX/edit"
      hoja = "Usuarios"

Si no hay nada configurado, las funciones devuelven None/False y la app usa
el respaldo de Secrets [credentials.*]. Nunca rompe.
"""

import streamlit as st


# ----------------------------------------------------------------------------
# Detección de método
# ----------------------------------------------------------------------------
def _modo():
    try:
        if "usuarios_webapp" in st.secrets:
            return "webapp"
        if "gcp_service_account" in st.secrets and "usuarios_sheet" in st.secrets:
            return "gspread"
    except Exception:
        pass
    return None


def disponible() -> bool:
    return _modo() is not None


# ----------------------------------------------------------------------------
# Parseo común: lista de dicts -> {usuario: {campos}}
# ----------------------------------------------------------------------------
def _parsear_registros(registros):
    usuarios = {}
    for r in registros:
        rr = {str(k).strip().lower(): v for k, v in r.items()}
        u = str(rr.get("usuario", "")).strip()
        if not u:
            continue
        acc = str(rr.get("acceso_total", "")).strip().lower()
        usuarios[u] = {
            "email": str(rr.get("email", "")).strip(),
            "password": str(rr.get("password", "")).strip(),
            "password_hash": str(rr.get("password_hash", "")).strip(),
            "acceso_total": acc in ("true", "1", "si", "sí", "x", "verdadero"),
            "categoria": (str(rr.get("categoria", "")).strip() or None),
            "rol": str(rr.get("rol", "")).strip() or u,
        }
    return usuarios or None


def _matriz_a_registros(valores):
    """Convierte una matriz [[encabezados], [fila], ...] en lista de dicts."""
    if not valores or len(valores) < 2:
        return []
    headers = [str(h).strip() for h in valores[0]]
    registros = []
    for fila in valores[1:]:
        d = {}
        for i, h in enumerate(headers):
            d[h] = fila[i] if i < len(fila) else ""
        registros.append(d)
    return registros


# ----------------------------------------------------------------------------
# MÉTODO A — Apps Script (HTTP)
# ----------------------------------------------------------------------------
def _webapp_post(payload):
    import requests
    conf = st.secrets["usuarios_webapp"]
    payload = dict(payload)
    payload["token"] = conf["token"]
    resp = requests.post(conf["url"], json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=120, show_spinner=False)
def _leer_webapp():
    try:
        data = _webapp_post({"accion": "leer"})
        if data.get("ok"):
            return _matriz_a_registros(data.get("valores", []))
    except Exception as e:
        print("usuarios_store(webapp): error leyendo:", e)
    return None


def _set_hash_webapp(usuario, nuevo_hash):
    try:
        data = _webapp_post({"accion": "set_hash", "usuario": usuario, "hash": nuevo_hash})
        if data.get("ok"):
            _leer_webapp.clear()
            return True
        print("usuarios_store(webapp): set_hash respondió", data)
    except Exception as e:
        print("usuarios_store(webapp): error escribiendo:", e)
    return False


# ----------------------------------------------------------------------------
# MÉTODO B — gspread (cuenta de servicio)
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _worksheet():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        conf = st.secrets["usuarios_sheet"]
        sh = client.open_by_url(conf["url"]) if "url" in conf else client.open_by_key(conf["id"])
        return sh.worksheet(conf.get("hoja", "Usuarios"))
    except Exception as e:
        print("usuarios_store(gspread): no se pudo abrir la hoja:", e)
        return None


@st.cache_data(ttl=120, show_spinner=False)
def _leer_gspread():
    ws = _worksheet()
    if ws is None:
        return None
    try:
        return ws.get_all_records()
    except Exception as e:
        print("usuarios_store(gspread): error leyendo:", e)
        return None


def _set_hash_gspread(usuario, nuevo_hash):
    ws = _worksheet()
    if ws is None:
        return False
    try:
        encabezados = [str(c).strip().lower() for c in ws.row_values(1)]
        col_usuario = (encabezados.index("usuario") + 1) if "usuario" in encabezados else 1
        col_hash = (encabezados.index("password_hash") + 1) if "password_hash" in encabezados else None
        col_pass = (encabezados.index("password") + 1) if "password" in encabezados else None
        fila = None
        for i, v in enumerate(ws.col_values(col_usuario), start=1):
            if str(v).strip().lower() == usuario.strip().lower():
                fila = i
                break
        if not fila:
            return False
        if col_hash:
            ws.update_cell(fila, col_hash, nuevo_hash)
        if col_pass:
            ws.update_cell(fila, col_pass, "")
        _leer_gspread.clear()
        return True
    except Exception as e:
        print("usuarios_store(gspread): error escribiendo:", e)
        return False


# ----------------------------------------------------------------------------
# API pública (elige el método solo)
# ----------------------------------------------------------------------------
def leer_usuarios():
    modo = _modo()
    if modo == "webapp":
        regs = _leer_webapp()
    elif modo == "gspread":
        regs = _leer_gspread()
    else:
        return None
    if regs is None:
        return None
    return _parsear_registros(regs)


def set_password_hash(usuario, nuevo_hash) -> bool:
    modo = _modo()
    if modo == "webapp":
        return _set_hash_webapp(usuario, nuevo_hash)
    if modo == "gspread":
        return _set_hash_gspread(usuario, nuevo_hash)
    return False
