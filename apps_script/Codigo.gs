/**********************************************************************
 *  Codigo.gs  —  Apps Script para la hoja "Usuarios" (Club Unión)
 *
 *  Permite que la app cambie contraseñas SIN usar Google Cloud y SIN tarjeta.
 *
 *  CÓMO USARLO (ver GUIA_CONTRASENAS.md, MÉTODO A):
 *   1. Abrí tu hoja de Google "Usuarios".
 *   2. Menú  Extensiones → Apps Script.
 *   3. Borrá lo que haya y pegá TODO este archivo.
 *   4. Cambiá el TOKEN de abajo por un secreto largo tuyo (inventalo).
 *   5. Implementar → Nueva implementación → tipo "Aplicación web":
 *         - Ejecutar como:  Yo
 *         - Quién tiene acceso:  Cualquier persona
 *      Copiá la URL que termina en /exec.
 *   6. En Streamlit Secrets poné:
 *         [usuarios_webapp]
 *         url = "...la URL /exec..."
 *         token = "...el mismo TOKEN de abajo..."
 **********************************************************************/

const TOKEN = "PEGÁ-UN-SECRETO-LARGO-ACÁ-Y-USALO-IGUAL-EN-SECRETS";
const HOJA = "Usuarios";

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    if (body.token !== TOKEN) return _json({ ok: false, error: "token invalido" });

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(HOJA);
    if (!sheet) return _json({ ok: false, error: "no existe la hoja " + HOJA });

    if (body.accion === "leer") {
      const valores = sheet.getDataRange().getValues();
      const limpio = valores.map(function (fila) {
        return fila.map(function (c) { return c === null ? "" : String(c); });
      });
      return _json({ ok: true, valores: limpio });
    }

    if (body.accion === "set_hash") {
      const datos = sheet.getDataRange().getValues();
      const headers = datos[0].map(function (h) { return String(h).trim().toLowerCase(); });
      const colUser = headers.indexOf("usuario");
      const colHash = headers.indexOf("password_hash");
      const colPass = headers.indexOf("password");
      if (colUser < 0) return _json({ ok: false, error: "falta columna usuario" });

      for (var i = 1; i < datos.length; i++) {
        if (String(datos[i][colUser]).trim().toLowerCase() ===
            String(body.usuario).trim().toLowerCase()) {
          if (colHash >= 0) sheet.getRange(i + 1, colHash + 1).setValue(body.hash);
          if (colPass >= 0) sheet.getRange(i + 1, colPass + 1).setValue("");
          return _json({ ok: true });
        }
      }
      return _json({ ok: false, error: "usuario no encontrado" });
    }

    return _json({ ok: false, error: "accion desconocida" });
  } catch (err) {
    return _json({ ok: false, error: String(err) });
  }
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
