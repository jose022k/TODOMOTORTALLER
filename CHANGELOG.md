# Changelog

## Proyecto: 2026-T303-G03

Todas las modificaciones siguen el estándar de versión semántica (https://semver.org/).

---

## [1.9.0] - 2026-08-02

### Added

- Reporte "Órdenes Completadas vs Canceladas": cantidad y proporción de órdenes completadas y canceladas, con endpoint `GET /reports/ordenes/completadas-canceladas`, gráfico de dona y tabla impresa
- Montos de pago en órdenes de servicio: columnas `monto`, `moneda` (BS/USD), `tasa_bcv` y `monto_usd` en `OrdenServicio`, con migración automática
- Notificaciones instantáneas en la web: toasts estilo Windows en la esquina inferior derecha al llegar una notificación, vía WebSocket (`notificacion_creada`) y componente `NotificationToasts.vue`; si la pestaña está en segundo plano o el navegador está minimizado se muestra además la notificación nativa del sistema operativo
- Logo de la marca (el del login) como favicon de la página y como imagen (icon/badge) en las notificaciones del navegador, con versiones cuadradas `logo-192.png` y `logo-512.png`
- Validaciones en el formulario de registro de clientes: campo Nombre solo acepta letras (sin números ni símbolos) con la primera letra de cada palabra en mayúscula automática; correo solo con dominio `@gmail.com`, `@outlook.com` o `@hotmail.com`; teléfono solo números con máximo 10 dígitos

### Changed

- Card "Rendimiento por Mecánico": ahora grafica solo el tiempo promedio por orden (minutos), sin la columna de cantidad de órdenes
- Montos de pago en órdenes de servicio: columnas `monto`, `moneda` (BS/USD), `tasa_bcv` y `monto_usd` en `OrdenServicio`, con migración automática
- Conversión Bs → USD con tasa de referencia del BCV en `create_order` (el monto es obligatorio)
- Tabla `configuracion` (con `ensure_schema_updates`) para persistir la tasa manual del admin
- Módulo `app/modules/bcv/` con endpoints `GET /bcv/tasa` y `PUT /bcv/tasa-manual`
- Tarjeta "Ganancias" en `AdminReportsView`: suma de órdenes completadas de los últimos 7 días, gráfico de línea semanal (eje Y 15–300), tabla impresa en el PDF y chip editable de tasa BCV
- Buscador de clientes en el modal "Nueva Orden" para seleccionar por nombre o cédula
- Spinners modernos tipo aro (conic-gradient + máscara) en `LoadingOverlay.vue` y botones (`.btn-spinner`)

### Changed

- Tasa de referencia consultada directamente desde `bcv.org.ve` (scraping del bloque `#dolar`) en lugar de DolarApi; `BCV_API_URL` → `BCV_URL` en `app/core/config.py`
- Subtítulos descriptivos de vistas admin alineados con el catálogo (`.page-subtitle` global con `margin-left: 48px`)
- Spinner de rueda de moto reemplazado por aro moderno en overlay y botones

---

## [1.8.0] - 2026-07-25

### Added

- WebSocket para actualizaciones en tiempo real de órdenes de servicio
- `ConnectionManager` en backend con broadcast por roles (admin, cliente, mecánico)
- Endpoint `GET /ws/orders?token=<jwt>` autenticado
- `orderSocket.js` — cliente WebSocket singleton con reconexión automática
- Proxy `/ws` en Vue dev server con `ws: true` para WebSocket same-origin
- Las 3 vistas (`AdminServiceOrdersView`, `MecanicoOrdersView`, `ClienteOrdersView`) escuchan eventos `order-updated` y actualizan lista + contador al instante

### Changed

- `app/main.py` — startup event para inicializar `ws_manager`
- `app/modules/service_orders/service.py` — broadcast en `create_order`, `update_order_status`, `assign_mechanic`
- `frontend/vue.config.js` — proxy `/ws` añadido con soporte WebSocket

---

## [1.8.1] - 2026-07-28

### Added

- Carrusel de imágenes en vista Taller (HomeView) con fotos taller1-4 subidas a Cloudinary
- Paginación (30/pág.) y búsqueda por prefijo en catálogo de motos
- Paginación (15/pág.) en tabla de usuarios (clientes y mecánicos)
- Subtítulos descriptivos debajo del título en vistas de admin
- Componente `LoadingOverlay` con animación de rueda de moto girando
- Componente `ConfirmModal` para confirmación de cierre de sesión
- Iconos SVG profesionales en navegación (Taller, Ubicación, Iniciar Sesión)

### Changed

- Vista Taller: nuevo carrusel con auto-slide, botones anterior/siguiente y puntos
- Vista Ubicación: mapa de Google Maps embebido + tarjeta de contacto flotante (WhatsApp y llamadas) + botón "Abrir en Maps"
- Navegación: "Home" → "Taller", "About" → "Ubicación"
- Cierre de sesión: ahora muestra modal de confirmación y overlay de carga de 3s
- Inicio de sesión: spinner reemplazado por overlay full-screen con rueda de moto
- Placa en órdenes de servicio: mayúsculas automáticas, solo alfanumérico, máx 7 caracteres

### Fixed

- Flash de enlaces Taller/Ubicación al cargar sesión de admin — corregida condición en App.vue
- Subtítulo "Visualiza y descarga reportes" aparecía en PDF — oculto con @media print

---

## [1.8.2] - 2026-07-28

### Fixed

- Chat: auto-scroll ya no baja cuando el usuario está leyendo mensajes antiguos
- Chat: mensajes y evidencias bloqueados cuando la orden está completada o cancelada
- Notificaciones: al hacer clic en una notificación de mensaje/evidencia de orden completada/cancelada, muestra aviso "La orden ya fue completada/cancelada"

---

## [1.7.0] - 2026-07-23

### Added

- Reportes: gráficos Chart.js con vue-chartjs (barras horizontales/verticales, paleta dorada) en AdminReportsView
- Reportes: filtros por rango de fechas (`fecha_inicio`/`fecha_fin`) en todos los endpoints excepto ordenes/por-dia-semana
- Reportes: selector de secciones con checkboxes para elegir qué incluir en el PDF
- Reportes: generación de PDF vía `window.print()` con tablas en lugar de gráficos, logo en esquina superior derecha, numeración secuencial (`Reporte N° 0000001`) y nombre de archivo `Reporte 000000X.pdf`
- Catálogo: modelo `Marca` (id, nombre único, logo_url) con migración automática desde marcas existentes
- Catálogo: endpoint `POST /motorcycles/brands` con subida de logo a Cloudinary (multipart: nombre + logo)
- Catálogo: botón "+ Nueva Marca" con modal drag & drop para subir logo PNG, vista previa y peso máximo 8 MB
- Utilidad `app/core/cloudinary.py` con función `upload_image()` para subir archivos a Cloudinary

### Changed

- Reportes: las 7 secciones (Top Mecánicos, Top Motos, etc.) se muestran siempre en pantalla; los checkboxes solo controlan qué aparece en el PDF
- Reportes: logo del PDF ahora se posiciona arriba a la derecha sin mover el contenido existente (flexbox en print-header)
- Reportes: dropdown de selección de secciones con checkboxes centrados y ancho fijo para alineación perfecta
- Catálogo: `GET /motorcycles/brands` ahora consulta la tabla `marca` en lugar de distinct de `catalogo_moto`
- Catálogo: modal de nueva marca mejorado con zona de arrastre, feedback visual y botón para quitar imagen

### Fixed

- Reportes: logo del PDF no aparecía — corregido con precarga vía JS y renderizado en pantalla (1×1px visibility:hidden) en lugar de display:none
- Reportes: nombre de archivo al guardar PDF ahora usa el título de página cambiado dinámicamente a "Reporte XXXXXXX"
- Catálogo: modal de nueva marca no se cerraba por guardia `saving` — corregido cerrando el modal antes de refrescar marcas
- Catálogo: migración de marcas existentes fallaba porque `create_all()` creaba la tabla vacía antes que `ensure_schema_updates()` — corregido moviendo la población fuera del bloque condicional

---

## [1.6.0] - 2026-06-30

### Added

- Web Push via `pywebpush` con VAPID: `PushSubscription`, Service Worker personalizado, notificaciones push funcionales
- Notificaciones automáticas al crear/cancelar órdenes, enviar mensajes y subir evidencias
- `NotificationsDropdown.vue` con badge de no leídos, polling cada 10s y navegación al hacer clic
- Sonido de notificación (`/sounds/notification.wav`) en el Service Worker
- Vista `AdminReportsView.vue` con 5 tarjetas de reportes y ruta `/admin/reports`
- Filtros de órdenes por cliente y mecánico en vista admin (RF-009)
- "Mis Motos" tab en `ClienteOrdersView` con historial y descarga de QR (CU-12/CU-13)
- Endpoint `GET /motorcycles/brands` con `logo_url` de todas las marcas
- Endpoint `GET /service-orders/moto/{id}/history` para historial de moto
- Descarga de QR con validación de propiedad
- Tarjeta "Órdenes de Servicio" y SVG icons en dashboard admin
- Redirección de ruta `/` a dashboard según rol
- `data-tooltip` en todos los nav-icon-btn (evita tooltip nativo superpuesto)
- Ojo amarillo (`#ffaa00`) para mostrar/ocultar contraseña en todos los campos password
- Vista unificada de login (`/login`) con detección de rol
- Modal de detalle de orden rediseñado: borde superior de color, grid de iconos, descripción en card, botones pill, blur overlay, reassign inline
- `open_chat=1` en notificaciones de mensajes/evidencias para abrir chat directamente
- Optimistic update en envío de mensajes (aparecen instantáneamente) y polling a 2s en ChatModal
- Refresco de chat al volver a la pestaña (`visibilitychange`)
- Envío en paralelo de texto y evidencias en chat

### Changed

- Namespace de routers con prefijo `/api/v1` en lugar de rutas planas
- Rendimiento: paginación en endpoints de clientes/mecánicos, endpoint ligero `clients/summary`, límite default 100 en catálogo, timeout axios 15000
- `OrdenServicioListResponse` enriquecido con `moto_anio`, `moto_color_especifico`, `moto_color`
- Modal de detalle se abre instantáneamente con datos de lista y detalle completo se fetchea en background
- Nombres capitalizados, cédula eliminada de modales
- Texto de navegación reemplazado por SVG icons con tooltips
- Estilos profesionales en login/register
- `NotificationsDropdown` usa `<a>` en lugar de `<button>` para renderizado correcto
- URLs de notificaciones incluyen `order_id` y `open_chat=1` según tipo
- Service Worker registrado también en desarrollo (sin guard `production`)
- SW `notificationclick` usa `matching.navigate(url)` + `matching.focus()`
- Proxy `/notifications` añadido en `vue.config.js` para desarrollo
- Notificaciones de evidencia notifican también al mecánico
- Notificaciones de chat notifican al admin cuando el cliente envía mensaje
- Login/Register: diseño moderno profesional con SVG icons
- `start_servers.bat` restaurado en `scripts/`

### Fixed

- Bug crítico: modal no se cerraba — causa raíz: `ensure_schema_updates()` duplicado + columnas incorrectas en `push_subscription`
- Tooltip nativo del browser aparecía encima del tooltip CSS; unificado con `data-tooltip`
- Al hacer clic en notificación de mensaje/evidencia, ya no abre el modal de detalle de orden, solo el chat
- Notificaciones de cliente con `open_chat` ahora redirigen a `/cliente/orders` (donde hay chat) en lugar de `/tracker` (sin chat)

### Documentation

- `DOCUMENTACION_TECNICA.md` con arquitectura completa, flujo de datos, descripción de módulos
- `SETUP.md` con guía de instalación paso a paso

---

## [1.5.0] - 2026-06-21

### Changed

- Migración de almacenamiento de evidencias de local (uploads/) a Cloudinary
- Eliminación de dependencia aiofiles y montaje estático de uploads
- URLs de evidencias actualizadas en base de datos a secure_url de Cloudinary
- .gitignore actualizado: uploads/ añadido

---

## [1.4.0] - 2026-06-21

### Added

- Módulo Chat: mensajería asociada a órdenes (solo en estado en_proceso)
- Envío de evidencias (fotos) con previsualización antes de subir
- Edición de mensajes dentro de 10 minutos con indicador editado
- Modal WhatsApp-style (ChatModal) con burbujas, etiquetas de remitente y lightbox
- Vista pública TrackerView para seguimiento de orden por ID
- Módulo Notifications: tabla notificacion con FKs reales por rol
- Módulo Reports: 5 endpoints de estadísticas (mecánico top, motos top, clientes recurrentes, tiempo promedio, rendimiento)
- Módulo Admin: dashboard con 8 contadores (clientes, mecánicos, órdenes por estado)
- Diagramas UML en uml/ (ER, casos de uso, estados, arquitectura)
- Documentación de requisitos funcionales (40 RFs)

### Changed

- Eliminación de módulo evidencias como módulo independiente (integrado en chat)

---

## [1.3.0] - 2026-06-14

### Added

- Módulo Service Orders: órdenes con estados pendiente/en_proceso/completada/cancelada
- Creación de órdenes con moto existente o nueva desde catálogo
- Selección de color del catálogo mediante chips
- Asignación y reasignación de mecánico
- Generación de QR al completar orden (almacenado como base64 en moto_cliente)
- HistorialMantenimiento al completar orden
- Vista frontend AdminServiceOrdersView, MecanicoOrdersView, ClienteOrdersView
- Redirección por rol al iniciar sesión

### Changed

- Optimizaciones en ClienteDAO con selectinload para motos
- Eliminación de campo gama_color del modal de creación de catálogo

---

## [1.2.0] - 2026-06-09

### Added

- Módulo Motorcycles: CRUD de catálogo de motos con 287 modelos
- Vista frontend CatalogoMotosView con grid, búsqueda reactiva y modal
- Logos de marcas desde Cloudinary en vista de catálogo

---

## [1.1.0] - 2026-06-01

### Added

- Módulo Users: CRUD de clientes y mecánicos con campo activo
- Desactivación lógica de usuarios (activo=False bloquea login)
- Módulo de autenticación: login para Admin, Cliente y Mecánico
- Modelos separados (Admin, Cliente, Mecánico) sin tabla única Usuario
- JWT con access token (15 min) y refresh token (7 días)
- Registro público de clientes
- Route guards y vistas de login independientes
- Pinia auth store y API service

---

## [1.0.0] - 2026-05-24

### Added

- Estructura inicial del proyecto (FastAPI + Vue.js)
- Conexión a base de datos PostgreSQL (Supabase)
- Configuración de Vue.js y variables de entorno
- Archivos .gitignore, .cursorrules y eslint config
