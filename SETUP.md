# Guía de Instalación — Todomotortaller

Instrucciones para ejecutar el proyecto en una PC nueva desde cero.

---

## Instalación de Software (por consola)

Abrir **PowerShell como Administrador** y ejecutar:

```powershell
# Instalar Git
winget install Git.Git --silent

# Instalar Node.js (incluye npm)
winget install OpenJS.NodeJS.LTS --silent

# Instalar Python 3.12
winget install Python.Python.3.12 --silent

# Instalar VS Code
winget install Microsoft.VisualStudioCode --silent
```

Reiniciar la terminal después de instalar todo.

Verificar que quedaron bien instalados:

```powershell
git --version
node --version
npm --version
python --version
code --version
```

---

## Extensiones de VS Code

| Extensión             | ID                          | Para qué sirve                    |
| --------------------- | --------------------------- | --------------------------------- |
| Python                | `ms-python.python`          | Intellisense, depuración          |
| Vue Language Features | `Vue.volar`                 | Resaltado y autocompletado `.vue` |
| ESLint                | `dbaeumer.vscode-eslint`    | Linting del frontend              |
| Prettier              | `esbenp.prettier-vscode`    | Formateo automático               |
| EditorConfig          | `EditorConfig.EditorConfig` | Consistencia de estilo            |

---

## Pasos de Instalación del Proyecto

### 1. Copiar el proyecto

Copiar toda la carpeta `2026-T303-G03` (del pendrive) al disco de la PC, por ejemplo al escritorio.

### 2. Backend (Python)

```powershell
cd ruta/del/proyecto/2026-T303-G03

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Frontend (Vue.js)

```powershell
cd ruta/del/proyecto/2026-T303-G03/frontend

# Instalar dependencias
npm install
```

### 4. Archivo .env

El archivo `.env` en la raíz del proyecto contiene las credenciales de Supabase y Cloudinary.
Como está en `.gitignore`, debe copiarse manualmente.

Ubicación esperada: `2026-T303-G03/.env`

Contenido requerido:

```
DATABASE_URL=postgresql+psycopg2://...
SECRET_KEY=...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
FRONTEND_URL=http://localhost:8080
```

---

## Ejecutar el proyecto

### Opción 1 — Script automático

Ejecutar el archivo `scripts\start_servers.bat`. Abre automáticamente el backend y frontend en ventanas separadas.

### Opción 2 — Manual (dos terminales)

**Terminal 1 — Backend**

```powershell
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend**

```powershell
cd frontend
npm run serve
```

El frontend se abre en: `http://localhost:8080`
La API del backend en: `http://localhost:8000`

---

## Notas importantes

- **No se copian** las carpetas `venv/` ni `node_modules/` — deben generarse con `pip install` y `npm install`
- **No es necesario** instalar PostgreSQL local — la base de datos está en Supabase (nube)
- **El `.env`** es el archivo más crítico — sin él el backend no puede conectarse a la BD ni a Cloudinary
- Para verificar que el backend funciona: `http://localhost:8000/` debe responder `{"message": "Todomotortaller API funcionando"}`
