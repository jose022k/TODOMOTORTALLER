# Requisitos Funcionales - Todomotortaller

## Módulo: Autenticación (Auth)
| ID | Descripción | Actor |
|---|---|---|
| RF-001 | El sistema debe permitir el registro público de clientes con nombre, cédula, email, contraseña, teléfono y dirección | Cliente |
| RF-002 | El sistema debe permitir el inicio de sesión con email, contraseña y rol, validando que el rol coincida con la tabla correspondiente | Admin, Cliente, Mecánico |
| RF-003 | El sistema debe emitir un token JWT de acceso (15 min) y un refresh token (7 días) al iniciar sesión | Admin, Cliente, Mecánico |
| RF-004 | El sistema debe permitir renovar el token de acceso mediante el refresh token | Admin, Cliente, Mecánico |
| RF-005 | El sistema debe permitir al admin crear mecánicos (protegido con token de admin) | Admin |
| RF-006 | El sistema debe permitir al admin gestionar clientes: consultar, actualizar datos y desactivar cuenta | Admin |
| RF-007 | El sistema debe permitir al usuario autenticado actualizar sus propios datos (nombre, email, contraseña) | Admin, Cliente, Mecánico |
| RF-039 | El sistema debe bloquear el inicio de sesión de clientes y mecánicos desactivados (activo=False) | Sistema |
| RF-040 | El sistema debe permitir al admin desactivar clientes y mecánicos sin eliminar sus registros | Admin |

## Módulo: Catálogo de Motos (Motorcycles)
| ID | Descripción | Actor |
|---|---|---|
| RF-008 | El sistema debe permitir al admin agregar modelos de motos al catálogo (marca, modelo, gama de color) | Admin |
| RF-009 | El sistema debe permitir al admin editar y eliminar modelos del catálogo | Admin |
| RF-010 | El sistema debe permitir registrar una moto asociada a un cliente (placa, año, referencia al catálogo) al momento de crear una orden | Admin |
| RF-011 | El sistema debe generar un código QR único para la moto al completarse la primera orden de servicio | Sistema |

## Módulo: Órdenes de Servicio (Service Orders)
| ID | Descripción | Actor |
|---|---|---|
| RF-012 | El sistema debe permitir al admin crear una orden de servicio con descripción, estado inicial "pendiente", cliente, mecánico asignado y moto del cliente | Admin |
| RF-013 | El sistema debe permitir al mecánico cambiar el estado de una orden asignada: pendiente → en_proceso → completada | Mecánico |
| RF-014 | El sistema debe permitir al admin cambiar el estado de cualquier orden a "cancelada" | Admin |
| RF-015 | El sistema debe registrar la fecha de creación al crear la orden y la fecha de cierre al completarla | Sistema |
| RF-016 | El sistema debe mostrar al cliente el estado actual de su orden; si no existe orden, mostrar "En proceso de crear orden de servicio" | Cliente |
| RF-017 | El sistema debe insertar un registro en historial_mantenimiento al completarse cada orden de servicio | Sistema |

## Módulo: Chat
| ID | Descripción | Actor |
|---|---|---|
| RF-018 | El sistema debe permitir enviar y recibir mensajes asociados a una orden de servicio | Admin, Cliente, Mecánico |
| RF-019 | El sistema debe identificar al remitente del mensaje según su rol (admin, cliente o mecánico) | Sistema |
| RF-020 | El sistema debe permitir enviar y recibir evidencias (fotos) asociadas a una orden de servicio | Admin, Mecánico, Cliente |
| RF-021 | El sistema debe almacenar las imágenes en Cloudinary y guardar la URL en la tabla evidencia | Sistema |
| RF-022 | El sistema debe permitir opcionalmente asociar una evidencia a un mensaje específico | Admin, Mecánico |

## Módulo: Notificaciones
| ID | Descripción | Actor |
|---|---|---|
| RF-024 | El sistema debe notificar al cliente, admin y mecánico cuando se cree una orden de servicio | Sistema |
| RF-025 | El sistema debe notificar al cliente y admin cuando la orden pase a "en_proceso" | Sistema |
| RF-026 | El sistema debe notificar al cliente y admin cuando la orden se complete | Sistema |
| RF-027 | El sistema debe notificar al destinatario cuando reciba un mensaje en el chat | Sistema |
| RF-028 | El sistema debe notificar al cliente cuando se envíen evidencias de su orden | Sistema |
| RF-029 | El sistema debe notificar al cliente cuando el admin actualice sus datos | Sistema |
| RF-030 | El sistema debe notificar al mecánico cuando el admin actualice sus datos | Sistema |

## Módulo: Reportes (Reports)
| ID | Descripción | Actor |
|---|---|---|
| RF-031 | El sistema debe mostrar el Top N de mecánicos con más servicios completados | Admin |
| RF-032 | El sistema debe mostrar el Top N de motos (marca/modelo) más atendidas | Admin |
| RF-033 | El sistema debe mostrar el Top N de clientes recurrentes (con más órdenes) | Admin |
| RF-034 | El sistema debe mostrar el tiempo promedio de reparación (horas entre creación y cierre) | Admin |
| RF-035 | El sistema debe mostrar el rendimiento individual de cada mecánico (total órdenes + tiempo promedio) | Admin |

## Módulo: Historial y QR
| ID | Descripción | Actor |
|---|---|---|
| RF-036 | El sistema debe permitir al admin consultar el historial completo de órdenes mediante la vista historial_moto | Admin |
| RF-037 | El sistema debe permitir al cliente escanear el QR de su moto para ver todo el historial de mantenimiento | Cliente |
| RF-038 | El sistema debe permitir al cliente descargar/visualizar el QR de su moto desde su perfil | Cliente |
