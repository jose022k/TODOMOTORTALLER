# Documentación Técnica — Todomotortaller

Sistema Web PWA de Seguimiento y Hoja de Vida para Motos.

---

## 1. Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Backend | Python + FastAPI | Python 3.12+ / FastAPI 0.111 |
| ORM | SQLAlchemy | 2.0 |
| Base de datos | PostgreSQL (Supabase) | — |
| Frontend | Vue.js 3 (Options API + `setup()`) | ^3.2.13 |
| Estado | Pinia | ^3.0.4 |
| Enrutador | Vue Router | ^4.0.3 |
| HTTP | Axios | ^1.16.1 |
| Autenticación | JWT (python-jose + bcrypt) | — |
| Archivos | Cloudinary | — |
| QR | qrcode[pil] | 7.4.2 |
| PWA | @vue/cli-plugin-pwa | ~5.0.0 |

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

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| **Router** | `router.py` | Define endpoints HTTP, inyecta dependencias de autenticación, valida schemas de entrada. Sin lógica de negocio. |
| **Service** | `service.py` | Lógica de negocio, reglas, validaciones, orquesta múltiples DAOs. |
| **DAO** | `dao.py` | CRUD directo a base de datos. Hereda de `BaseDAO`. Sin lógica de negocio. |
| **Model** | `models.py` | Modelos SQLAlchemy planos (solo columnas y relaciones). Sin métodos de persistencia. |

### Capas del Frontend

```
views/  →  components/  →  stores/  →  services/api.js  →  Backend
(página)    (UI reusable)   (estado)     (HTTP client)
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

**BaseDAO genérico** (`app/core/base_dao.py`):
- `BaseDAO[ModelType, CreateSchemaType, UpdateSchemaType]`
- Métodos: `get_by_id`, `get_all`, `create`, `update`, `delete`
- Todos los DAOs del proyecto heredan de esta clase.

### 3.2 Service Layer (Capa de Servicio)

La lógica de negocio está aislada en archivos `service.py` separados de los routers y DAOs. Ejemplos:

- `auth/service.py` — registro, login, refresh token, actualización de perfil
- `service_orders/service.py` — creación de órdenes, cambio de estados, generación de QR
- `chat/service.py` — envío de mensajes, subida de evidencias a Cloudinary, edición con límite de 10 min

### 3.3 Inyección de Dependencias (FastAPI)

FastAPI inyecta la sesión de base de datos y el usuario autenticado mediante dependencias:

```python
# app/modules/auth/dependencies.py
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decodifica JWT, busca usuario en admin/cliente/mecanico
    ...

def get_current_admin(current_user = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(403)
    return current_user
```

### 3.4 Frontend — Observer (Pinia + Reactividad)

Pinia maneja el estado global de autenticación. Los componentes de Vue observan cambios reactivos:

```javascript
// stores/auth.js
const user = ref(null);  // reactivo
const isAdmin = computed(() => state.user?.rol === 'admin');  // getter derivado
```

### 3.5 Autenticación — JWT (Access + Refresh Token)

- **Access token**: expira en 15 minutos, enviado en header `Authorization: Bearer`
- **Refresh token**: expira en 7 días, usado para renovar el access token automáticamente
- El interceptor de Axios en el frontend detecta 401 e intenta refrescar el token antes de redirigir al login

### 3.6 Separación de Modelos de Usuario (sin tabla Usuario única)

No existe una sola tabla `Usuario`. En su lugar hay tres tablas independientes:

- `admin` — administradores del taller
- `cliente` — clientes (con campos adicionales: cedula, telefono, direccion, activo)
- `mecanico` — mecánicos (con campo activo)

Cada tabla tiene su propio login y sus propias FK en tablas como `mensaje` y `notificacion`.

### 3.7 FKs Reales por Rol (no polimórficas)

En tablas como `mensaje` y `notificacion`, las columnas de origen son separadas:

```sql
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

Esto mantiene integridad referencial a diferencia del patrón polimórfico (tipo+id).

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

| Módulo | Estado |
|--------|--------|
| `notifications/` | Modelo y schemas listos. Router sin endpoints funcionales. |
| `clients/` | Router stub (solo health check). |
| `mechanics/` | Router stub (solo health check). |
| WebSocket (`core/websocket.py`) | Archivo vacío. |

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

El archivo `router/index.js` implementa un guardia `beforeEach` que:

1. Permite acceso público a `/tracker/:id` y páginas de login/registro
2. Redirige al login si no hay token y la ruta requiere autenticación
3. Verifica que el rol del usuario coincida con el `meta.rol` de la ruta
4. Redirige a la página principal del rol si el usuario ya está autenticado e intenta acceder al login

---

## 6. Base de Datos — Tablas y Relaciones

### 6.1 Tablas

| Tabla | Descripción | FK |
|-------|-------------|----|
| `admin` | Administradores del sistema | — |
| `cliente` | Clientes del taller | — |
| `mecanico` | Mecánicos del taller | — |
| `catalogo_moto` | Catálogo maestro de modelos de motos | — |
| `moto_cliente` | Motos registradas de cada cliente | `catalogo_moto_id`, `cliente_id` |
| `orden_servicio` | Órdenes de servicio/reparación | `cliente_id`, `mecanico_id`, `moto_cliente_id` |
| `evidencia` | Evidencias (fotos) de órdenes | `orden_servicio_id`, `mensaje_id` |
| `mensaje` | Mensajes del chat | `orden_servicio_id`, `admin_id?`, `cliente_id?`, `mecanico_id?` |
| `notificacion` | Notificaciones del sistema | `orden_servicio_id`, `admin_id?`, `cliente_id?`, `mecanico_id?` |
| `historial_mantenimiento` | Historial de mantenimiento completado | `moto_cliente_id`, `orden_servicio_id`, `mecanico_id` |

### 6.2 Estados de Orden de Servicio

```
pendiente → en_proceso → completada
                      ↘ cancelada
```

### 6.3 Vista `historial_moto`

Es una **VIEW** de SQL (no tabla física) que combina `orden_servicio` + `moto_cliente` + `cliente` + `mecanico` + `catalogo_moto`.

---

## 7. Pull Requests (Historial Completo)

| PR # | Rama | Fecha | Descripción |
|------|------|-------|-------------|
| #1 | `chore/project-setup` | 2026-05-17 | Estructura inicial del proyecto y configuración base |
| #2 | `chore/project-setup` | 2026-05-17 | Configuración del frontend Vue.js |
| #3 | `chore/project-setup` | 2026-05-20 | Corrección de configuración ESLint |
| #4 | `chore/project-setup` | 2026-05-24 | Configuración final del proyecto e inicialización del CHANGELOG |
| #5 | `feature/auth-module` | 2026-05-24 | Módulo de autenticación: login, JWT, registro de clientes |
| #6 | `feature/auth-module` | 2026-06-09 | Refactorización: separación de modelos de usuario por rol, vistas de login independientes, route guards |
| #7 | `feature/motorcycles-module` | 2026-06-09 | CRUD de catálogo de motos con vista frontend |
| #8 | `feature/users-module` | 2026-06-12 | CRUD de usuarios (clientes y mecánicos) con campo activo |
| #9 | `feature/service-orders-module` | 2026-06-12 | Órdenes de servicio completo: CRUD, QR, selección de color del catálogo, historial de mantenimiento |
| #10 | `feature/auth-module` | 2026-06-12 | Merge final del módulo auth con actualizaciones menores |
| #11 | `feature/motorcycles-module` | 2026-06-12 | Merge final del módulo motorcycles |
| #12 | `feature/users-module` | 2026-06-12 | Merge final del módulo users |
| #13 | `chore/project-setup` | 2026-06-12 | Resolución de conflictos en .gitignore y configuración de scripts/ |
| #14 | `feature/chat-module` | 2026-06-21 | Módulo de chat completo: mensajería, evidencias, edición, modal WhatsApp-style, Cloudinary |

---

## 8. Flujo de Negocio Completo

```
1. Admin precarga motos en catalogo_moto (CRUD en /admin/catalog)
2. Cliente se registra (público en /register/cliente)
3. Cliente inicia sesión (/loginCliente)
4. Admin crea moto_cliente con datos de placa, año, color y referencia al catálogo
5. Admin crea orden_servicio (POST /service-orders)
   - Estado inicial: pendiente
   - Se asigna mecánico
   - Se especifica moto del cliente (existente o nueva)
6. Mecánico cambia estado a en_proceso (PATCH /service-orders/{id}/status)
7. Durante el trabajo:
   - Chat habilitado (solo en estado en_proceso)
   - Mensajes entre cliente, mecánico y admin
   - Evidencias (fotos) subidas a Cloudinary
   - Mensajes editables dentro de 10 minutos
8. Mecánico/Admin completa la orden:
   - Estado: completada
   - Se registra fecha_cierre
   - Se genera QR con el ID de la orden
   - Se inserta registro en historial_mantenimiento
9. Cliente escanea el QR →
   - Ve tracker público con la orden y su estado
   - Puede ver todo su historial de mantenimiento
```

---

## 9. API — Endpoints Principales

### Autenticación (`/auth`)
| Método | Ruta | Acceso |
|--------|------|--------|
| POST | `/auth/register/cliente` | Público |
| POST | `/auth/login` | Público (Admin) |
| POST | `/auth/loginMecanico` | Público |
| POST | `/auth/loginCliente` | Público |
| POST | `/auth/refresh` | Público (token requerido) |
| GET | `/auth/me` | Autenticado |
| PUT | `/auth/me` | Autenticado |

### Usuarios (`/users`)
| Método | Ruta | Acceso |
|--------|------|--------|
| POST | `/users/mechanics` | Admin |
| GET | `/users/clients` | Admin |
| GET | `/users/clients/{id}` | Admin |
| PATCH | `/users/clients/{id}` | Admin |
| PATCH | `/users/clients/{id}/deactivate` | Admin |
| GET | `/users/mechanics` | Admin |
| GET | `/users/mechanics/{id}` | Admin |
| PATCH | `/users/mechanics/{id}` | Admin |
| PATCH | `/users/mechanics/{id}/deactivate` | Admin |

### Órdenes de Servicio (`/service-orders`)
| Método | Ruta | Acceso |
|--------|------|--------|
| POST | `/service-orders` | Admin |
| GET | `/service-orders` | Autenticado (filtrado por rol) |
| GET | `/service-orders/{id}` | Autenticado |
| PATCH | `/service-orders/{id}/status` | Mecánico/Admin |
| PATCH | `/service-orders/{id}/mechanic` | Admin |
| GET | `/service-orders/{id}/tracker` | Público |

### Chat (`/chat`)
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/chat/{orden_id}` | Participantes de la orden |
| POST | `/chat/{orden_id}` | Participantes de la orden |
| GET | `/chat/{orden_id}/evidencias` | Participantes de la orden |
| POST | `/chat/{orden_id}/evidencias` | Participantes de la orden (solo en_proceso) |
| PUT | `/chat/{orden_id}/{mensaje_id}` | Remitente del mensaje |
| DELETE | `/chat/{orden_id}/evidencias/{evidencia_id}` | Participantes de la orden |

### Catálogo de Motos (`/motorcycles`)
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/motorcycles/catalog` | Autenticado |
| GET | `/motorcycles/catalog/{id}` | Autenticado |
| POST | `/motorcycles/catalog` | Admin |
| PUT | `/motorcycles/catalog/{id}` | Admin |
| DELETE | `/motorcycles/catalog/{id}` | Admin |

### Reportes (`/reports`)
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/reports/mecanicos/mas-servicios` | Admin |
| GET | `/reports/motos/mas-atendidas` | Admin |
| GET | `/reports/clientes/recurrentes` | Admin |
| GET | `/reports/tiempo-promedio-reparacion` | Admin |
| GET | `/reports/mecanicos/rendimiento` | Admin |

### Dashboard (`/admin`)
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/admin/dashboard` | Admin |

---

## 10. Convenciones de Código

### Backend (Python)
- **Nombres de tablas y columnas**: en español (`orden_servicio`, `moto_cliente`, `fecha_creacion`)
- **Nombres de código**: en inglés (`class OrdenServicioDAO`, `def create_order`)
- **Arquitectura**: Router → Service → DAO → DB (Data Mapper)
- **Autenticación**: dependencias de FastAPI para cada rol

### Frontend (Vue.js)
- **Idioma de UI**: español (etiquetas, mensajes, estados)
- **Nombres de componentes/variables**: en inglés
- **Estado global**: Pinia store (`useAuthStore`)
- **Peticiones HTTP**: Axios con interceptors JWT

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

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Admin | `admin@todomotortaller.com` | `Admintaller$` |
| Cliente | `josepalma@gmail.com` | (registrado por usuario) |
| Mecánico 1 | `prueba@gmail.com` | (asignado por admin) |
| Mecánico 2 | `test@test.com` | `test123` |
