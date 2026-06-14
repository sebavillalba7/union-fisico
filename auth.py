"""
auth.py
=======
Manejo de usuarios, contraseñas y permisos.

- Los usuarios con "acceso_total=True" ven TODAS las categorías.
- Los usuarios de categoría solo ven su propia categoría (campo "categoria").

SEGURIDAD:
Por defecto las credenciales están acá para que la app funcione enseguida.
Para mayor seguridad podés moverlas a .streamlit/secrets.toml (ver README).
Si existe el bloque [credentials] en secrets, se usa ese en lugar de este.
"""

import streamlit as st

# ----------------------------------------------------------------------------
# USUARIOS POR DEFECTO
#   usuario: {"password": ..., "acceso_total": bool, "categoria": str|None, "rol": str}
# "categoria" debe coincidir con la columna CAT de la planilla.
# ----------------------------------------------------------------------------
USUARIOS_DEFAULT = {
    # ---------------- ADMINISTRADOR ----------------
    "admin":        {"password": "Admin.Union2025",  "acceso_total": True,  "categoria": None, "rol": "Administrador"},

    # ---------------- COORDINADORES (acceso total) ----------------
    "Coordinador":  {"password": "Union2025.Coord",  "acceso_total": True,  "categoria": None, "rol": "Coordinador General"},
    "Coord_PFs":    {"password": "Union2025.PFs",    "acceso_total": True,  "categoria": None, "rol": "Coordinador PF"},
    "Coord_Fza":    {"password": "Union2025.Fza",    "acceso_total": True,  "categoria": None, "rol": "Coordinador Fuerza"},
    "Sec-Tecnica":  {"password": "Union2025.SecTec", "acceso_total": True,  "categoria": None, "rol": "Secretaría Técnica"},

    # ---------------- CATEGORÍAS (solo sus datos) ----------------
    "PF-2012":      {"password": "Tate2012.PF",      "acceso_total": False, "categoria": "2012", "rol": "PF Categoría 2012"},
    "PF-2011":      {"password": "Tate2011.PF",      "acceso_total": False, "categoria": "2011", "rol": "PF Categoría 2011"},
    "PF-2010":      {"password": "Tate2010.PF",      "acceso_total": False, "categoria": "2010", "rol": "PF Categoría 2010"},
    "PF-2009":      {"password": "Tate2009.PF",      "acceso_total": False, "categoria": "2009", "rol": "PF Categoría 2009"},
    "PF-2008":      {"password": "Tate2008.PF",      "acceso_total": False, "categoria": "2008", "rol": "PF Categoría 2008"},
    "PF-2007":      {"password": "Tate2007.PF",      "acceso_total": False, "categoria": "2007", "rol": "PF Categoría 2007"},
    "PF-2006":      {"password": "Tate2006.PF",      "acceso_total": False, "categoria": "2006", "rol": "PF Categoría 2006"},

    # PF-3a: acceso total (puede ver todas las categorías)
    "PF-3a":        {"password": "Tate3a.Total",     "acceso_total": True,  "categoria": None, "rol": "PF Tercera"},
}


def get_usuarios():
    """Devuelve el diccionario de usuarios. Prioriza st.secrets si existe."""
    try:
        if "credentials" in st.secrets:
            # En secrets se define como: [credentials.usuario] password=..., etc.
            usuarios = {}
            for user, data in st.secrets["credentials"].items():
                usuarios[user] = {
                    "password": data.get("password", ""),
                    "acceso_total": bool(data.get("acceso_total", False)),
                    "categoria": data.get("categoria") or None,
                    "rol": data.get("rol", user),
                }
            if usuarios:
                return usuarios
    except Exception:
        pass
    return USUARIOS_DEFAULT


def validar_login(usuario: str, password: str):
    """Devuelve el dict del usuario si las credenciales son correctas, si no None."""
    usuarios = get_usuarios()
    if usuario in usuarios and password == usuarios[usuario]["password"]:
        info = dict(usuarios[usuario])
        info["usuario"] = usuario
        return info
    return None


def categorias_permitidas(user_info: dict, todas: list):
    """Devuelve la lista de categorías que el usuario puede ver."""
    if user_info.get("acceso_total"):
        return list(todas)
    cat = user_info.get("categoria")
    return [cat] if cat else []
