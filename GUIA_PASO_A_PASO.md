# 🟥 Guía paso a paso — De cero a la app publicada

Esta guía está pensada para alguien que **nunca** subió nada a GitHub ni usó Streamlit.
Vas a poder publicar la app **gratis** y obtener un link para compartir con los PF y coordinadores.

Hay **dos caminos**. Elegí UNO:

- **Camino A (recomendado, sin instalar nada):** todo desde la web del navegador. Más simple.
- **Camino B (con tu computadora):** instalás Git y probás la app en tu compu antes de publicar.

> ⏱️ El Camino A lleva unos 15–20 minutos.

---

## 🧰 Antes de empezar: ¿qué tengo?

Tenés una carpeta llamada **`union-fisico`** con estos archivos (los generé yo):

```
union-fisico/
├── app.py
├── config.py
├── auth.py
├── data_loader.py
├── analysis.py
├── charts.py
├── styles.py
├── requirements.txt
├── README.md
├── GUIA_PASO_A_PASO.md   ← este archivo
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
└── assets/
    └── escudo_union.png
```

Te lo entrego como un **archivo .zip**. Lo primero es **descomprimirlo** en tu computadora:
hacé clic derecho sobre el .zip → **Extraer todo** (Windows) o doble clic (Mac).
Vas a obtener la carpeta `union-fisico` con todo adentro.

> ⚠️ **Importante sobre las carpetas que empiezan con punto** (`.streamlit`, `.gitignore`):
> a veces el sistema las oculta. No las borres. Si no las ves, activá "Mostrar archivos ocultos"
> (en Windows: pestaña **Vista** → tildá **Elementos ocultos**).

---

# 🟦 CAMINO A — Todo desde la web (recomendado)

## PASO 1 — Crear una cuenta en GitHub

1. Entrá a **https://github.com**
2. Clic en **Sign up** (registrarse).
3. Poné un email, una contraseña y un nombre de usuario (ej: `pf-union`). Anotálos.
4. Confirmá el email que te llega.

> GitHub es como "Google Drive para proyectos de código". Es gratis.

## PASO 2 — Crear el repositorio (la "carpeta" en la nube)

1. Ya logueado en GitHub, arriba a la derecha clic en el **`+`** → **New repository**.
2. En **Repository name** escribí: `union-fisico`
3. Dejá la opción **Public** marcada (Streamlit gratis necesita que sea público).
   - 🔒 Tranquilo: **público** significa que se ve el código, **no tus contraseñas**.
     Las contraseñas NO se suben (más abajo te explico cómo cargarlas aparte y seguras).
4. **NO** tildes "Add a README" (ya tenemos uno).
5. Clic en **Create repository**.

## PASO 3 — Subir los archivos

1. En la página del repo recién creado, buscá el link **"uploading an existing file"**
   (o el botón **Add file** → **Upload files**).
2. Abrí la carpeta `union-fisico` en tu computadora.
3. **Seleccioná TODO lo de adentro** (no la carpeta, sino su contenido) y **arrastralo** a la
   ventana de GitHub. Asegurate de incluir:
   - todos los `.py`
   - `requirements.txt`, `README.md`, `GUIA_PASO_A_PASO.md`, `.gitignore`
   - la carpeta **`assets`** (con `escudo_union.png` adentro)
   - la carpeta **`.streamlit`** (con `config.toml`)
4. Esperá a que terminen de cargar (verás la lista de archivos abajo).
5. Más abajo, en **Commit changes**, clic en el botón verde **Commit changes**.

> 📌 Si la carpeta `.streamlit` no se sube arrastrando (a veces pasa con carpetas ocultas),
> hacé esto: **Add file → Create new file**, y en el nombre escribí
> `.streamlit/config.toml` (GitHub crea la carpeta sola al poner la barra `/`).
> Después pegás el contenido del archivo. Lo mismo para `assets`: subí el escudo con
> **Upload files** y nombrándolo dentro de `assets/`.

✅ Cuando termines, tu repo debe verse con todos los archivos listados.

## PASO 4 — Publicar en Streamlit Cloud (gratis)

1. Entrá a **https://share.streamlit.io**
2. Clic en **Sign in** → **Continue with GitHub** (usá la cuenta que creaste).
   Aceptá los permisos que pide.
3. Clic en **Create app** (o **New app**) → elegí **"Deploy a public app from GitHub"**.
4. Completá:
   - **Repository:** `tu-usuario/union-fisico`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Clic en **Deploy**.
6. Esperá 1–3 minutos mientras instala todo. Cuando termina, **¡tu app está online!**
   Te queda un link tipo: `https://union-fisico.streamlit.app`

🎉 Ese link es el que compartís con los profes.

## PASO 5 — Cargar las contraseñas de forma segura (recomendado)

Por seguridad, las contraseñas **no** se suben a GitHub. Se cargan aparte en Streamlit:

1. En **https://share.streamlit.io**, entrá a tu app.
2. Abajo a la derecha clic en **Manage app** → menú **⋮** (tres puntitos) → **Settings** → **Secrets**.
3. Abrí el archivo **`.streamlit/secrets.toml.example`** (te lo di en la carpeta),
   copiá TODO su contenido y pegalo en ese cuadro de **Secrets**.
4. Clic en **Save**. La app se reinicia sola.

> Si **NO** hacés este paso, la app igual funciona con las contraseñas que ya vienen por
> defecto en el código. Pero como el repo es público, **lo ideal es hacer el Paso 5** para
> que las claves no queden a la vista.

> 🔑 **Cambiar contraseñas:** editá los valores dentro del cuadro de Secrets cuando quieras
> y guardá. No hace falta tocar GitHub.

---

# 🟩 CAMINO B — Probarla en tu computadora primero (opcional)

Hacé esto solo si querés ver la app en tu compu antes de publicarla.

## B1 — Instalar Python
1. Entrá a **https://www.python.org/downloads/** y descargá Python 3.11 o superior.
2. Al instalar en Windows, **tildá "Add Python to PATH"** antes de continuar.

## B2 — Abrir la terminal en la carpeta
- **Windows:** abrí la carpeta `union-fisico`, clic en la barra de dirección, escribí `cmd` y Enter.
- **Mac:** abrí **Terminal**, escribí `cd ` (con espacio) y arrastrá la carpeta a la ventana, Enter.

## B3 — Instalar las librerías
Escribí en la terminal:
```
pip install -r requirements.txt
```

## B4 — Ejecutar la app
```
streamlit run app.py
```
Se abre sola en el navegador en `http://localhost:8501`. Para frenarla: `Ctrl + C` en la terminal.

> Para publicarla igual tenés que hacer el **Camino A** (subir a GitHub + Streamlit Cloud).

---

# 👤 Usuarios y contraseñas

| Usuario | Contraseña | Acceso |
|---|---|---|
| admin | `Admin.Union2025` | Total |
| Coordinador | `Union2025.Coord` | Total |
| Coord_PFs | `Union2025.PFs` | Total |
| Coord_Fza | `Union2025.Fza` | Total |
| Sec-Tecnica | `Union2025.SecTec` | Total |
| PF-3a | `Tate3a.Total` | Total |
| PF-2012 | `Tate2012.PF` | Solo 2012 |
| PF-2011 | `Tate2011.PF` | Solo 2011 |
| PF-2010 | `Tate2010.PF` | Solo 2010 |
| PF-2009 | `Tate2009.PF` | Solo 2009 |
| PF-2008 | `Tate2008.PF` | Solo 2008 |
| PF-2007 | `Tate2007.PF` | Solo 2007 |
| PF-2006 | `Tate2006.PF` | Solo 2006 |

> Cambiá estas claves cuando quieras desde **Secrets** (Paso 5) o en el archivo `auth.py`.

---

# ❓ Problemas frecuentes

**La app dice "Error al cargar datos" o aparece vacía.**
- Revisá que las planillas de Google sigan **publicadas como CSV**
  (en Google Sheets: *Archivo → Compartir → Publicar en la web → CSV*).
- Las URLs están en `config.py`. Si cambiaste de planilla, actualizalas ahí.

**Veo las tarjetas pero sin números / faltan columnas.**
- Los nombres de las columnas de tu planilla deben coincidir con los que busca la app.
  En `config.py`, dentro de `COMMON_COLUMNS` y de las métricas, hay **listas de nombres posibles**.
  Si tu planilla usa otro nombre (ej. la columna de categoría se llama "Categoria" y no "CAT"),
  agregalo a la lista correspondiente y volvé a subir `config.py` a GitHub.

**Las categorías no coinciden.**
- En `config.py`, la lista `CATEGORIAS` es `2006`…`2012` y `3a`. Esos valores tienen que ser
  **iguales** a los que figuran en la columna **CAT** de tu planilla. Si en la planilla dice
  "Cat 2010" o "2010 ", ajustá la planilla o la lista para que coincidan exactamente.

**Quiero cambiar el escudo.**
- Reemplazá `assets/escudo_union.png` por tu imagen (mismo nombre) y volvé a subirla a GitHub.

**Cómo actualizar la app después de un cambio.**
- Editás el archivo en GitHub (lápiz ✏️) o volvés a subirlo con *Upload files* → *Commit*.
  Streamlit detecta el cambio y se actualiza solo en 1–2 minutos.

---

# 🖨️ Exportar a PDF

Dentro de cada apartado hay un botón **🖨️ Imprimir / Guardar PDF**.
1. Clic en el botón (se abre el cuadro de impresión del navegador).
2. En **Destino** elegí **"Guardar como PDF"**.
3. Recomendado: tamaño **A4**, márgenes **Predeterminados**, y tildá **Gráficos de fondo**
   para que se vean los colores.
4. **Guardar**.

La app ya está configurada para **no cortar** las tarjetas ni las tablas entre hojas.

---

¡Listo! Con esto tenés la app publicada y compartible. Cualquier número, nombre de columna o
contraseña se ajusta y se vuelve a subir a GitHub en segundos.
