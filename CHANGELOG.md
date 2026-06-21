# Changelog
## Proyecto: 2026-T303-G03
Todas las modificaciones siguen el estándar de versión semántica (https://semver.org/).

---

## [1.5.0] - 2026-06-21
### Changed
- Migración de almacenamiento de evidencias de local (uploads/) a Cloudinary
- Eliminación de dependencia aiofiles y montaje estático de uploads
- URLs de evidencias actualizadas en base de datos a secure_url de Cloudinary
- .gitignore actualizado: uploads/ añadido

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

## [1.2.0] - 2026-06-09
### Added
- Módulo Motorcycles: CRUD de catálogo de motos con 287 modelos
- Vista frontend CatalogoMotosView con grid, búsqueda reactiva y modal
- Logos de marcas desde Cloudinary en vista de catálogo

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

## [1.0.0] - 2026-05-24
### Added
- Estructura inicial del proyecto (FastAPI + Vue.js)
- Conexión a base de datos PostgreSQL (Supabase)
- Configuración de Vue.js y variables de entorno
- Archivos .gitignore, .cursorrules y eslint config