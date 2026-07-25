# Changelog

## Proyecto: 2026-T303-G03

Todas las modificaciones siguen el estándar de versión semántica (https://semver.org/).

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

## [1.0.0] - 2026-05-24

### Initial Release

- Initial project structure setup.
