from sqlalchemy.orm import Session
from app.modules.auth.dao import ClienteDAO, MecanicoDAO
from app.modules.service_orders.models import OrdenServicio

cliente_dao = ClienteDAO()
mecanico_dao = MecanicoDAO()


def get_dashboard(db: Session) -> dict:
    clientes = cliente_dao.get_all(db)
    mecanicos = mecanico_dao.get_all(db)
    ordenes = db.query(OrdenServicio).all()

    total_ordenes_pendientes = sum(1 for o in ordenes if o.estado == "pendiente")
    total_ordenes_en_proceso = sum(1 for o in ordenes if o.estado == "en_proceso")
    total_ordenes_completadas = sum(1 for o in ordenes if o.estado == "completada")
    total_ordenes_canceladas = sum(1 for o in ordenes if o.estado == "cancelada")

    return {
        "total_clientes": len(clientes),
        "total_clientes_activos": sum(1 for c in clientes if c.activo),
        "total_mecanicos": len(mecanicos),
        "total_mecanicos_activos": sum(1 for m in mecanicos if m.activo),
        "total_ordenes_pendientes": total_ordenes_pendientes,
        "total_ordenes_en_proceso": total_ordenes_en_proceso,
        "total_ordenes_completadas": total_ordenes_completadas,
        "total_ordenes_canceladas": total_ordenes_canceladas,
    }
