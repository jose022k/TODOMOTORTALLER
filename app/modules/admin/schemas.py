from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_clientes: int
    total_clientes_activos: int
    total_mecanicos: int
    total_mecanicos_activos: int
    total_ordenes_pendientes: int
    total_ordenes_en_proceso: int
    total_ordenes_completadas: int
    total_ordenes_canceladas: int
