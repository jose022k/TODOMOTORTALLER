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


class DailyStatsResponse(BaseModel):
    clientes_registrados_hoy: int
    motos_atendidas_hoy: int
    clientes_nuevos_hoy: int
    servicio_mas_realizado_hoy: str
    marca_mas_atendida_hoy: str
