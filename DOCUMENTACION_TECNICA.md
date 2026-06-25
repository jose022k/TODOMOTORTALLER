# Documentación Técnica — Todomotortaller

Sistema Web PWA de Seguimiento y Hoja de Vida para Motos.

---

## 1. Stack Tecnológico

| Capa          | Tecnología                         | Versión                      |
| ------------- | ---------------------------------- | ---------------------------- |
| Backend       | Python + FastAPI                   | Python 3.12+ / FastAPI 0.111 |
| ORM           | SQLAlchemy                         | 2.0                          |
| Base de datos | PostgreSQL (Supabase)              | —                            |
| Frontend      | Vue.js 3 (Options API + `setup()`) | ^3.2.13                      |
| Estado        | Pinia                              | ^3.0.4                       |
| Enrutador     | Vue Router                         | ^4.0.3                       |
| HTTP          | Axios                              | ^1.16.1                      |
| Autenticación | JWT (python-jose + bcrypt)         | —                            |
| Archivos      | Cloudinary                         | —                            |
| QR            | qrcode[pil]                        | 7.4.2                        |
| PWA           | @vue/cli-plugin-pwa                | ~5.0.0                       |

---

## 2. Arquitectura General

### Comunicación Frontend ↔ Backend

El frontend Vue.js se comunica con el backend exclusivamente mediante **peticiones HTTP REST**.

```
Vue.js (localhost:8080)
  → axios (HTTP + JSON)
  → FastAPI (localhost:8000)
  → Service Layer
  → DAO Layer
  → PostgreSQL (Supabase - nube)
```

### Capas del Backend (por módulo)

Cada módulo sigue una arquitectura en 4 capas:

```
router.py  →  service.py  →  dao.py  →  models.py
  (ruta)      (lógica)      (datos)      (BD)
```

| Capa        | Archivo      | Ruta                       | Responsabilidad                                                                                                 |
| ----------- | ------------ | -------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Router**  | `router.py`  | `app/modules/*/router.py`  | Define endpoints HTTP, inyecta dependencias de autenticación, valida schemas de entrada. Sin lógica de negocio. |
| **Service** | `service.py` | `app/modules/*/service.py` | Lógica de negocio, reglas, validaciones, orquesta múltiples DAOs.                                               |
| **DAO**     | `dao.py`     | `app/modules/*/dao.py`     | CRUD directo a base de datos. Hereda de `BaseDAO`. Sin lógica de negocio.                                       |
| **Model**   | `models.py`  | `app/modules/*/models.py`  | Modelos SQLAlchemy planos (solo columnas y relaciones). Sin métodos de persistencia.                            |

### Capas del Frontend

```
frontend/src/views/  →  components/  →  stores/  →  services/api.js  →  Backend
(página)              (UI reusable)   (estado)     (HTTP client)
```

---

## 3. Patrones de Diseño

### 3.1 Data Mapper (SQLAlchemy)

Los modelos SQLAlchemy son planos — solo definen columnas y relaciones. No tienen métodos `save()` o `delete()`. Toda la persistencia pasa por los DAOs:

```python
# Modelo plano (solo datos)
class Cliente(Base):
    __tablename__ = "cliente"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)

# DAO maneja persistencia (herencia de BaseDAO)
cliente_dao = ClienteDAO()
cliente = cliente_dao.get_by_id(db, 1)
```

**BaseDAO genérico** — `app/core/base_dao.py`

- `BaseDAO[ModelType, CreateSchemaType, UpdateSchemaType]`
- Métodos: `get_by_id`, `get_all`, `create`, `update`, `delete`
- Todos los DAOs del proyecto heredan de esta clase.
- DAOs concretos: `app/modules/auth/dao.py` (AdminDAO, ClienteDAO, MecanicoDAO), `app/modules/chat/dao.py` (MensajeDAO), `app/modules/service_orders/dao.py` (OrdenServicioDAO, EvidenciaDAO), `app/modules/motorcycles/dao.py` (CatalogoMotoDAO)

### 3.2 Service Layer (Capa de Servicio)

La lógica de negocio está aislada en archivos `service.py` separados de los routers y DAOs. Ejemplos:

| Módulo         | Ruta                                    | Responsabilidad                                                                    |
| -------------- | --------------------------------------- | ---------------------------------------------------------------------------------- |
| Auth           | `app/modules/auth/service.py`           | registro, login, refresh token, actualización de perfil                            |
| Service Orders | `app/modules/service_orders/service.py` | creación de órdenes, cambio de estados, generación de QR                           |
| Chat           | `app/modules/chat/service.py`           | envío de mensajes, subida de evidencias a Cloudinary, edición con límite de 10 min |
| Motorcycles    | `app/modules/motorcycles/service.py`    | CRUD catálogo, validación de duplicados                                            |
| Users          | `app/modules/users/service.py`          | CRUD clientes y mecánicos, activar/desactivar                                      |
| Reports        | `app/modules/reports/service.py`        | 5 consultas de estadísticas agregadas                                              |
| Admin          | `app/modules/admin/service.py`          | dashboard con 8 contadores                                                         |

### 3.3 Inyección de Dependencias (FastAPI)

FastAPI inyecta la sesión de base de datos y el usuario autenticado mediante dependencias (`app/modules/auth/dependencies.py`):

```python
# Archivo: app/modules/auth/dependencies.py
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decodifica JWT, busca usuario en admin/cliente/mecanico
    ...

def get_current_admin(current_user = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(403)
    return current_user
```

La sesión de BD se inyecta desde `app/core/database.py` mediante la función `get_db()`. Los tokens JWT se crean y verifican en `app/modules/auth/utils.py`.

### 3.4 Frontend — Observer (Pinia + Reactividad)

Pinia (`frontend/src/stores/auth.js`) maneja el estado global de autenticación. Los componentes de Vue observan cambios reactivos:

```javascript
// Archivo: frontend/src/stores/auth.js
const user = ref(null); // reactivo
const isAdmin = computed(() => state.user?.rol === "admin"); // getter derivado
```

El interceptor de Axios (`frontend/src/services/api.js`) añade automáticamente el token Bearer a cada petición y maneja el refresh automático en caso de 401.

### 3.5 Autenticación — JWT (Access + Refresh Token)

Implementado en `app/modules/auth/utils.py` (creación/verificación) y `app/modules/auth/service.py` (lógica de login/refresh).

- **Access token**: expira en 15 minutos, enviado en header `Authorization: Bearer`
- **Refresh token**: expira en 7 días, usado para renovar el access token automáticamente
- El interceptor de Axios en el frontend (`frontend/src/services/api.js`) detecta 401 e intenta refrescar el token antes de redirigir al login

### 3.6 Separación de Modelos de Usuario (sin tabla Usuario única)

Definido en `app/modules/auth/models.py`. No existe una sola tabla `Usuario`. En su lugar hay tres tablas independientes:

| Tabla      | Clase                  | Archivo                      | Campos clave                                                       |
| ---------- | ---------------------- | ---------------------------- | ------------------------------------------------------------------ |
| `admin`    | `class Admin(Base)`    | `app/modules/auth/models.py` | id, nombre, email, contraseña                                      |
| `cliente`  | `class Cliente(Base)`  | `app/modules/auth/models.py` | id, nombre, cedula, email, contraseña, telefono, direccion, activo |
| `mecanico` | `class Mecanico(Base)` | `app/modules/auth/models.py` | id, nombre, email, contraseña, activo                              |

Cada tabla tiene su propio login y sus propias FK en tablas como `mensaje` y `notificacion`. Los DAOs correspondientes están en `app/modules/auth/dao.py`.

### 3.7 FKs Reales por Rol (no polimórficas)

Definido en `app/modules/chat/models.py` (tabla `mensaje`) y `app/modules/notifications/models.py` (tabla `notificacion`). Las columnas de origen son separadas por rol en lugar de usar un patrón polimórfico (tipo+id):

```sql
-- Definido en: app/modules/chat/models.py (clase Mensaje)
-- y app/modules/notifications/models.py (clase Notificacion)
CREATE TABLE mensaje (
    id SERIAL PRIMARY KEY,
    contenido TEXT,
    admin_id INT REFERENCES admin(id),
    cliente_id INT REFERENCES cliente(id),
    mecanico_id INT REFERENCES mecanico(id),
    CHECK (
        (admin_id IS NOT NULL AND cliente_id IS NULL AND mecanico_id IS NULL) OR
        (admin_id IS NULL AND cliente_id IS NOT NULL AND mecanico_id IS NULL) OR
        (admin_id IS NULL AND cliente_id IS NULL AND mecanico_id IS NOT NULL)
    )
);
```

Esto mantiene integridad referencial a diferencia del patrón polimórfico (tipo+id). La restricción CHECK asegura que exactamente un remitente no sea NULL.

---

## 4. Estructura del Proyecto Backend

```
app/
  main.py                           ← Punto de entrada, monta routers
  core/
    config.py                       ← Variables de entorno (JWT, Cloudinary, BD)
    database.py                     ← Engine SQLAlchemy, get_db(), ensure_schema_updates()
    base_dao.py                     ← BaseDAO genérico con CRUD
  modules/
    auth/                           ← Autenticación (login, registro, JWT)
      models.py                     ← Admin, Cliente, Mecanico
      schemas.py                    ← UserCreate, UserLogin, TokenResponse, etc.
      dao.py                        ← AdminDAO, ClienteDAO, MecanicoDAO
      service.py                    ← register_cliente, login, refresh_token
      router.py                     ← POST /auth/login, POST /auth/register/cliente, etc.
      dependencies.py               ← get_current_user, get_current_admin, get_current_mecanico
      utils.py                      ← hash_password, verify_password, create_access_token, etc.

    users/                          ← Gestión de usuarios (Admin)
      schemas.py                    ← ClienteUpdate, MecanicoUpdate, ClienteResponse, etc.
      service.py                    ← CRUD de clientes y mecánicos, activar/desactivar
      router.py                     ← GET/POST/PATCH /users/clients, /users/mechanics

    motorcycles/                    ← Catálogo de motos e historial
      models.py                     ← CatalogoMoto, MotoCliente, HistorialMantenimiento
      schemas.py                    ← CatalogoMotoBase, MotoClienteBase, etc.
      dao.py                        ← CatalogoMotoDAO
      service.py                    ← CRUD catálogo con validación de duplicados
      router.py                     ← GET/POST/PUT/DELETE /motorcycles/catalog

    service_orders/                 ← Órdenes de servicio (núcleo del negocio)
      models.py                     ← OrdenServicio, Evidencia
      schemas.py                    ← OrdenServicioCreate, StatusUpdate, TrackerResponse, etc.
      dao.py                        ← OrdenServicioDAO, EvidenciaDAO
      service.py                    ← create_order, update_status, assign_mechanic, get_tracker
      router.py                     ← CRUD /service-orders + /{id}/tracker público

    chat/                           ← Mensajería y evidencias
      models.py                     ← Mensaje
      schemas.py                    ← MensajeCreate, MensajeEdit, MensajeResponse
      dao.py                        ← MensajeDAO
      service.py                    ← send_message, edit_message, create_evidencia, etc.
      router.py                     ← GET/POST /chat/{orden_id}, evidencias, etc.

    notifications/                  ← Notificaciones Web Push
      models.py                     ← Notificacion
      schemas.py                    ← NotificacionBase, NotificacionCreate

    reports/                        ← Reportes y estadísticas
      service.py                    ← get_mecanico_mas_servicios, get_motos_mas_atendidas, etc.
      router.py                     ← GET /reports/* (admin only)

    admin/                          ← Dashboard
      schemas.py                    ← DashboardResponse
      service.py                    ← get_dashboard (8 contadores)
      router.py                     ← GET /admin/dashboard
```

### 4.1 Módulos en estado stub (no implementados completamente)

| Módulo           | Ruta                         | Estado                                                     |
| ---------------- | ---------------------------- | ---------------------------------------------------------- |
| `notifications/` | `app/modules/notifications/` | Modelo y schemas listos. Router sin endpoints funcionales. |
| `clients/`       | `app/modules/clients/`       | Router stub (solo health check).                           |
| `mechanics/`     | `app/modules/mechanics/`     | Router stub (solo health check).                           |
| WebSocket        | `app/core/websocket.py`      | Archivo vacío (placeholder para futura funcionalidad).     |

---

## 5. Estructura del Proyecto Frontend

```
frontend/src/
  main.js                           ← Arranque de Vue, instalación de Pinia y Router
  App.vue                           ← Componente raíz (header con nav + router-view)
  registerServiceWorker.js          ← Registro PWA (solo producción)

  assets/
    styles.css                      ← Variables CSS globales (color primario #FFAA00)
    logo.png                        ← Logo de Vue

  router/
    index.js                        ← 13 rutas con guardia de navegación por rol

  stores/
    auth.js                         ← Pinia store: login, logout, refresh, estado del usuario

  services/
    api.js                          ← Axios instance con interceptors JWT + refresh automático

  components/
    HelloWorld.vue                  ← Componente por defecto de Vue CLI
    ChatBox.vue                     ← Chat inline simple (en desuso, reemplazado por ChatModal)
    ChatModal.vue                   ← Modal WhatsApp-style completo (mensajes + evidencias + edición)
    EvidenceGallery.vue             ← Grid de fotos con subida y lightbox

  views/
    HomeView.vue                    ← Página de inicio pública
    AboutView.vue                   ← Página "Acerca de"
    LoginView.vue                   ← Selector de rol (Admin/Mecánico/Cliente)
    AdminLoginView.vue              ← Formulario login admin
    MecanicoLoginView.vue           ← Formulario login mecánico
    ClienteLoginView.vue            ← Formulario login cliente
    ClienteRegisterView.vue         ← Registro público de clientes
    RegisterView.vue                ← Registro de mecánicos (admin)
    Admin.vue                       ← Dashboard admin
    AdminUsersView.vue              ← CRUD de usuarios (mecánicos y clientes)
    AdminServiceOrdersView.vue      ← CRUD de órdenes de servicio + chat
    CatalogoMotosView.vue           ← Gestión del catálogo de motos
    MecanicoOrdersView.vue          ← Órdenes asignadas al mecánico
    ClienteOrdersView.vue           ← Órdenes del cliente (solo lectura + tracker)
    TrackerView.vue                 ← Tracker público vía QR (sin autenticación)
```

### 5.1 Guardia de Navegación (Router)

El archivo `frontend/src/router/index.js` implementa un guardia `beforeEach` que:

1. Permite acceso público a `/tracker/:id` y páginas de login/registro
2. Redirige al login si no hay token y la ruta requiere autenticación
3. Verifica que el rol del usuario coincida con el `meta.rol` de la ruta
4. Redirige a la página principal del rol si el usuario ya está autenticado e intenta acceder al login

---

## 6. Base de Datos — Tablas y Relaciones

### 6.1 Tablas

| Tabla                     | Modelo (archivo)                                                     | Descripción                           | FK                                                              |
| ------------------------- | -------------------------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------- |
| `admin`                   | `class Admin` — `app/modules/auth/models.py`                         | Administradores del sistema           | —                                                               |
| `cliente`                 | `class Cliente` — `app/modules/auth/models.py`                       | Clientes del taller                   | —                                                               |
| `mecanico`                | `class Mecanico` — `app/modules/auth/models.py`                      | Mecánicos del taller                  | —                                                               |
| `catalogo_moto`           | `class CatalogoMoto` — `app/modules/motorcycles/models.py`           | Catálogo maestro de modelos de motos  | —                                                               |
| `moto_cliente`            | `class MotoCliente` — `app/modules/motorcycles/models.py`            | Motos registradas de cada cliente     | `catalogo_moto_id`, `cliente_id`                                |
| `orden_servicio`          | `class OrdenServicio` — `app/modules/service_orders/models.py`       | Órdenes de servicio/reparación        | `cliente_id`, `mecanico_id`, `moto_cliente_id`                  |
| `evidencia`               | `class Evidencia` — `app/modules/service_orders/models.py`           | Evidencias (fotos) de órdenes         | `orden_servicio_id`, `mensaje_id`                               |
| `mensaje`                 | `class Mensaje` — `app/modules/chat/models.py`                       | Mensajes del chat                     | `orden_servicio_id`, `admin_id?`, `cliente_id?`, `mecanico_id?` |
| `notificacion`            | `class Notificacion` — `app/modules/notifications/models.py`         | Notificaciones del sistema            | `orden_servicio_id`, `admin_id?`, `cliente_id?`, `mecanico_id?` |
| `historial_mantenimiento` | `class HistorialMantenimiento` — `app/modules/motorcycles/models.py` | Historial de mantenimiento completado | `moto_cliente_id`, `orden_servicio_id`, `mecanico_id`           |

### 6.2 Estados de Orden de Servicio

```
pendiente → en_proceso → completada
                      ↘ cancelada
```

### 6.3 Vista `historial_moto`

Definida en `sql/create_tables.sql`. Es una **VIEW** de SQL (no tabla física) que combina `orden_servicio` + `moto_cliente` + `cliente` + `mecanico` + `catalogo_moto`.

---

## 7. Pull Requests (Historial Completo)

| PR # | Rama                            | Commit Hash | Fecha      | Descripción                                                                                             |
| ---- | ------------------------------- | ----------- | ---------- | ------------------------------------------------------------------------------------------------------- |
| #1   | `chore/project-setup`           | `ecfd6b0`   | 2026-05-17 | Estructura inicial del proyecto y configuración base                                                    |
| #2   | `chore/project-setup`           | `e6ad761`   | 2026-05-17 | Configuración del frontend Vue.js                                                                       |
| #3   | `chore/project-setup`           | `42ead99`   | 2026-05-20 | Corrección de configuración ESLint                                                                      |
| #4   | `chore/project-setup`           | `1690164`   | 2026-05-24 | Configuración final del proyecto e inicialización del CHANGELOG                                         |
| #5   | `feature/auth-module`           | `5d1ab20`   | 2026-05-24 | Módulo de autenticación: login, JWT, registro de clientes                                               |
| #6   | `feature/auth-module`           | `7b5a032`   | 2026-06-09 | Refactorización: separación de modelos de usuario por rol, vistas de login independientes, route guards |
| #7   | `feature/motorcycles-module`    | `0d18f87`   | 2026-06-09 | CRUD de catálogo de motos con vista frontend                                                            |
| #8   | `feature/users-module`          | `258e64c`   | 2026-06-12 | CRUD de usuarios (clientes y mecánicos) con campo activo                                                |
| #9   | `feature/service-orders-module` | `928cdd2`   | 2026-06-12 | Órdenes de servicio completo: CRUD, QR, selección de color del catálogo, historial de mantenimiento     |
| #10  | `feature/auth-module`           | `4c19ce8`   | 2026-06-12 | Merge final del módulo auth con actualizaciones menores                                                 |
| #11  | `feature/motorcycles-module`    | `7e17ed9`   | 2026-06-12 | Merge final del módulo motorcycles                                                                      |
| #12  | `feature/users-module`          | `1984f9e`   | 2026-06-12 | Merge final del módulo users                                                                            |
| #13  | `chore/project-setup`           | `9ae8cbe`   | 2026-06-12 | Resolución de conflictos en .gitignore y configuración de scripts/                                      |
| #14  | `feature/chat-module`           | `f4fd274`   | 2026-06-21 | Módulo de chat completo: mensajería, evidencias, edición, modal WhatsApp-style, Cloudinary              |

---

## 8. Flujo de Negocio Completo

```
1. Admin precarga motos en catalogo_moto (CRUD en /admin/catalog)
   → Servicio: app/modules/motorcycles/service.py
   → Vista: frontend/src/views/CatalogoMotosView.vue

2. Cliente se registra (público en /register/cliente)
   → Servicio: app/modules/auth/service.py (register_cliente)
   → Vista: frontend/src/views/ClienteRegisterView.vue

3. Cliente inicia sesión (/loginCliente)
   → Servicio: app/modules/auth/service.py (login)
   → Vista: frontend/src/views/ClienteLoginView.vue

4. Admin crea moto_cliente con datos de placa, año, color y referencia al catálogo
   → Servicio: app/modules/service_orders/service.py (create_order)
   → Modelo: app/modules/motorcycles/models.py (MotoCliente)

5. Admin crea orden_servicio (POST /service-orders)
   → Servicio: app/modules/service_orders/service.py (create_order)
   → Router: app/modules/service_orders/router.py
   → Vista: frontend/src/views/AdminServiceOrdersView.vue
   - Estado inicial: pendiente
   - Se asigna mecánico
   - Se especifica moto del cliente (existente o nueva)

6. Mecánico cambia estado a en_proceso (PATCH /service-orders/{id}/status)
   → Servicio: app/modules/service_orders/service.py (update_order_status)
   → Vista: frontend/src/views/MecanicoOrdersView.vue

7. Durante el trabajo:
   - Chat habilitado (solo en estado en_proceso)
   - Mensajes entre cliente, mecánico y admin
     → Servicio: app/modules/chat/service.py (send_message, get_messages)
     → Modal: frontend/src/components/ChatModal.vue
   - Evidencias (fotos) subidas a Cloudinary
     → Servicio: app/modules/chat/service.py (create_evidencia)
   - Mensajes editables dentro de 10 minutos
     → Servicio: app/modules/chat/service.py (edit_message)

8. Mecánico/Admin completa la orden:
   - Estado: completada
   - Se registra fecha_cierre
   - Se genera QR con el ID de la orden
   - Se inserta registro en historial_mantenimiento
   → Servicio: app/modules/service_orders/service.py (_completar_orden)
   → Modelo QR: app/modules/motorcycles/models.py (MotoCliente.codigo_qr)

9. Cliente escanea el QR →
   → Endpoint público: GET /service-orders/{id}/tracker
   → Servicio: app/modules/service_orders/service.py (get_order_tracker)
   -> Vista: frontend/src/views/TrackerView.vue
   - Ve tracker público con la orden y su estado
   - Puede ver todo su historial de mantenimiento
```

---

## 9. API — Endpoints Principales

### Autenticación (`/auth`) — Router: `app/modules/auth/router.py`

| Método | Ruta                     | Acceso                    |
| ------ | ------------------------ | ------------------------- |
| POST   | `/auth/register/cliente` | Público                   |
| POST   | `/auth/login`            | Público (Admin)           |
| POST   | `/auth/loginMecanico`    | Público                   |
| POST   | `/auth/loginCliente`     | Público                   |
| POST   | `/auth/refresh`          | Público (token requerido) |
| GET    | `/auth/me`               | Autenticado               |
| PUT    | `/auth/me`               | Autenticado               |

### Usuarios (`/users`) — Router: `app/modules/users/router.py`

| Método | Ruta                               | Acceso |
| ------ | ---------------------------------- | ------ |
| POST   | `/users/mechanics`                 | Admin  |
| GET    | `/users/clients`                   | Admin  |
| GET    | `/users/clients/{id}`              | Admin  |
| PATCH  | `/users/clients/{id}`              | Admin  |
| PATCH  | `/users/clients/{id}/deactivate`   | Admin  |
| GET    | `/users/mechanics`                 | Admin  |
| GET    | `/users/mechanics/{id}`            | Admin  |
| PATCH  | `/users/mechanics/{id}`            | Admin  |
| PATCH  | `/users/mechanics/{id}/deactivate` | Admin  |

### Órdenes de Servicio (`/service-orders`) — Router: `app/modules/service_orders/router.py`

| Método | Ruta                            | Acceso                         |
| ------ | ------------------------------- | ------------------------------ |
| POST   | `/service-orders`               | Admin                          |
| GET    | `/service-orders`               | Autenticado (filtrado por rol) |
| GET    | `/service-orders/{id}`          | Autenticado                    |
| PATCH  | `/service-orders/{id}/status`   | Mecánico/Admin                 |
| PATCH  | `/service-orders/{id}/mechanic` | Admin                          |
| GET    | `/service-orders/{id}/tracker`  | Público                        |

### Chat (`/chat`) — Router: `app/modules/chat/router.py`

| Método | Ruta                                         | Acceso                                      |
| ------ | -------------------------------------------- | ------------------------------------------- |
| GET    | `/chat/{orden_id}`                           | Participantes de la orden                   |
| POST   | `/chat/{orden_id}`                           | Participantes de la orden                   |
| GET    | `/chat/{orden_id}/evidencias`                | Participantes de la orden                   |
| POST   | `/chat/{orden_id}/evidencias`                | Participantes de la orden (solo en_proceso) |
| PUT    | `/chat/{orden_id}/{mensaje_id}`              | Remitente del mensaje                       |
| DELETE | `/chat/{orden_id}/evidencias/{evidencia_id}` | Participantes de la orden                   |

### Catálogo de Motos (`/motorcycles`) — Router: `app/modules/motorcycles/router.py`

| Método | Ruta                        | Acceso      |
| ------ | --------------------------- | ----------- |
| GET    | `/motorcycles/catalog`      | Autenticado |
| GET    | `/motorcycles/catalog/{id}` | Autenticado |
| POST   | `/motorcycles/catalog`      | Admin       |
| PUT    | `/motorcycles/catalog/{id}` | Admin       |
| DELETE | `/motorcycles/catalog/{id}` | Admin       |

### Reportes (`/reports`) — Router: `app/modules/reports/router.py`

| Método | Ruta                                  | Acceso |
| ------ | ------------------------------------- | ------ |
| GET    | `/reports/mecanicos/mas-servicios`    | Admin  |
| GET    | `/reports/motos/mas-atendidas`        | Admin  |
| GET    | `/reports/clientes/recurrentes`       | Admin  |
| GET    | `/reports/tiempo-promedio-reparacion` | Admin  |
| GET    | `/reports/mecanicos/rendimiento`      | Admin  |

### Dashboard (`/admin`) — Router: `app/modules/admin/router.py`

| Método | Ruta               | Acceso |
| ------ | ------------------ | ------ |
| GET    | `/admin/dashboard` | Admin  |

---

## 10. Convenciones de Código

### Backend (Python)

- **Nombres de tablas y columnas**: en español (`orden_servicio`, `moto_cliente`, `fecha_creacion`) — definido en `app/modules/*/models.py`
- **Nombres de código**: en inglés (`class OrdenServicioDAO`, `def create_order`) — definido en `app/modules/*/`
- **Arquitectura**: Router → Service → DAO → DB (Data Mapper) — BaseDAO en `app/core/base_dao.py`
- **Autenticación**: dependencias de FastAPI para cada rol — definido en `app/modules/auth/dependencies.py`

### Frontend (Vue.js)

- **Idioma de UI**: español (etiquetas, mensajes, estados) — en `frontend/src/views/*.vue`
- **Nombres de componentes/variables**: en inglés
- **Estado global**: Pinia store — `frontend/src/stores/auth.js`
- **Peticiones HTTP**: Axios con interceptors JWT — `frontend/src/services/api.js`

### Git

- **Ramas**: `<tipo>/<descripcion-en-kebab-case>` (ej: `feature/chat-module`)
- **Commits**: `<tipo>: <descripción>` (tipos: `feat`, `fix`, `refactor`, `chore`, `docs`)

---

## 11. Variables de Entorno (`.env`)

```
DATABASE_URL=postgresql+psycopg2://...
SECRET_KEY=...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
FRONTEND_URL=http://localhost:8080
```

---

## 12. Usuarios de Prueba

| Rol        | Email                       | Contraseña               |
| ---------- | --------------------------- | ------------------------ |
| Admin      | `admin@todomotortaller.com` | `Admintaller$`           |
| Cliente    | `josepalma@gmail.com`       | (registrado por usuario) |
| Mecánico 1 | `prueba@gmail.com`          | (asignado por admin)     |
| Mecánico 2 | `test@test.com`             | `test123`                |
