"""
auth.py
=======
Manejo de usuarios, contraseñas, emails y permisos.

SEGURIDAD
---------
Las contraseñas NO se guardan en el código (sería público en GitHub).
Se leen desde Streamlit Secrets, que es PRIVADO:
    Manage app -> Settings -> Secrets

Formato esperado en Secrets (ver .streamlit/secrets.toml.example):

    [credentials.admin]
    password = "NuevaClaveSegura"
    email = "admin@union.com"
    acceso_total = true
    rol = "Administrador"

Soporta dos formas de clave por usuario:
  - password       -> texto plano (simple; el Secret ya es privado)
  - password_hash  -> hash pbkdf2 (más seguro; ver generar_hash() abajo)

Si no hay Secrets cargados, solo funciona el usuario de respaldo "admin"
con una clave temporal, para que puedas entrar y configurar el resto.
"""

import hashlib
import hmac
import os

import streamlit as st

# Estructura de usuarios SIN contraseñas (esto sí puede estar en GitHub).
# La contraseña y el email de cada uno se cargan desde Secrets.
USUARIOS_ESTRUCTURA = {
    "admin":       {"acceso_total": True,  "categoria": None,   "rol": "Administrador"},
    "Coordinador": {"acceso_total": True,  "categoria": None,   "rol": "Coordinador General"},
    "Coord_PFs":   {"acceso_total": True,  "categoria": None,   "rol": "Coordinador PF"},
    "Coord_Fza":   {"acceso_total": True,  "categoria": None,   "rol": "Coordinador Fuerza"},
    "Sec-Tecnica": {"acceso_total": True,  "categoria": None,   "rol": "Secretaría Técnica"},
    "PF-3a":       {"acceso_total": True,  "categoria": None,   "rol": "PF Tercera (2005)"},
    "PF-2012":     {"acceso_total": False, "categoria": "2012", "rol": "PF Categoría 2012"},
    "PF-2011":     {"acceso_total": False, "categoria": "2011", "rol": "PF Categoría 2011"},
    "PF-2010":     {"acceso_total": False, "categoria": "2010", "rol": "PF Categoría 2010"},
    "PF-2009":     {"acceso_total": False, "categoria": "2009", "rol": "PF Categoría 2009"},
    "PF-2008":     {"acceso_total": False, "categoria": "2008", "rol": "PF Categoría 2008"},
    "PF-2007":     {"acceso_total": False, "categoria": "2007", "rol": "PF Categoría 2007"},
    "PF-2006":     {"acceso_total": False, "categoria": "2006", "rol": "PF Categoría 2006"},
}

# Clave temporal SOLO si todavía no cargaste Secrets (cambiala enseguida).
_ADMIN_TEMP = "CambiarEsta.2025"


# ----------------------------------------------------------------------------
# Hash de contraseñas (opcional pero recomendado)
# ----------------------------------------------------------------------------
def generar_hash(password: str, salt: str = "union-cau") -> str:
    """Devuelve un hash pbkdf2 del password. Útil para guardar en vez del texto."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return dk.hex()


def _verificar(password: str, data: dict) -> bool:
    """Compara el password ingresado contra password_hash o password."""
    if "password_hash" in data and data["password_hash"]:
        return hmac.compare_digest(generar_hash(password), str(data["password_hash"]))
    if "password" in data and data["password"]:
        return hmac.compare_digest(password, str(data["password"]))
    return False


# ----------------------------------------------------------------------------
# Carga de usuarios
# ----------------------------------------------------------------------------
def get_usuarios():
    """Devuelve {usuario: {password/hash, email, acceso_total, categoria, rol}}.

    Prioridad:
      1) Streamlit Secrets  [credentials.*]   (recomendado)
      2) Respaldo mínimo: solo 'admin' con clave temporal.
    """
    try:
        if "credentials" in st.secrets:
            usuarios = {}
            for user, data in st.secrets["credentials"].items():
                base = USUARIOS_ESTRUCTURA.get(user, {})
                usuarios[user] = {
                    "password": data.get("password", ""),
                    "password_hash": data.get("password_hash", ""),
                    "email": data.get("email", ""),
                    "acceso_total": bool(data.get("acceso_total", base.get("acceso_total", False))),
                    "categoria": data.get("categoria", base.get("categoria")) or None,
                    "rol": data.get("rol", base.get("rol", user)),
                }
            if usuarios:
                return usuarios
    except Exception:
        pass

    # Respaldo: solo admin, para poder entrar y configurar Secrets.
    return {
        "admin": {
            "password": _ADMIN_TEMP, "password_hash": "", "email": "",
            "acceso_total": True, "categoria": None, "rol": "Administrador (temporal)",
        }
    }


def validar_login(usuario: str, password: str):
    """Devuelve el dict del usuario si las credenciales son correctas; si no, None."""
    usuarios = get_usuarios()
    if usuario in usuarios and _verificar(password, usuarios[usuario]):
        info = dict(usuarios[usuario])
        info["usuario"] = usuario
        return info
    return None


def categorias_permitidas(user_info: dict, todas: list):
    """Lista de categorías que el usuario puede ver."""
    if user_info.get("acceso_total"):
        return list(todas)
    cat = user_info.get("categoria")
    return [cat] if cat else []
