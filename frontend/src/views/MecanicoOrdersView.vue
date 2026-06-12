<template>
  <div class="mecanico-orders">
    <div class="header">
      <h1>Mis Órdenes de Servicio</h1>
    </div>

    <div v-if="alert.message" :class="['alert', 'alert-' + alert.type]">
      {{ alert.message }}
      <button class="alert-close" @click="alert.message = ''">×</button>
    </div>

    <div v-if="loading" class="loading-state">Cargando órdenes...</div>
    <div v-else-if="orders.length === 0" class="empty-state">No tienes órdenes asignadas.</div>
    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Cliente</th>
          <th>Moto</th>
          <th>Descripción</th>
          <th>Estado</th>
          <th>Fecha</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="o in orders" :key="o.id">
          <td>{{ o.id }}</td>
          <td>{{ o.cliente_nombre }}</td>
          <td>{{ o.moto_marca }} {{ o.moto_modelo }} ({{ o.moto_placa }})</td>
          <td class="desc-cell">{{ o.descripcion }}</td>
          <td><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></td>
          <td>{{ formatDate(o.fecha_creacion) }}</td>
          <td class="actions-cell">
            <button v-if="o.estado === 'pendiente'" class="btn-sm btn-start" @click="changeStatus(o.id, 'en_proceso')">Iniciar</button>
            <button v-if="o.estado === 'en_proceso'" class="btn-sm btn-complete" @click="changeStatus(o.id, 'completada')">Completar</button>
            <button v-if="o.estado === 'pendiente' || o.estado === 'en_proceso'" class="btn-sm btn-cancel-order" @click="changeStatus(o.id, 'cancelada')">Cancelar</button>
            <span v-if="o.estado === 'completada' || o.estado === 'cancelada'" class="text-muted">—</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "MecanicoOrders",
  data() {
    return {
      alert: { message: "", type: "success" },
      loading: false,
      orders: [],
    };
  },
  methods: {
    statusLabel(estado) {
      const map = { pendiente: "Pendiente", en_proceso: "En Proceso", completada: "Completada", cancelada: "Cancelada" };
      return map[estado] || estado;
    },
    formatDate(d) {
      if (!d) return "—";
      return new Date(d).toLocaleDateString("es-ES", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
    },
    showAlert(message, type = "success") {
      this.alert = { message, type };
      setTimeout(() => { this.alert.message = ""; }, 4000);
    },
    async fetchOrders() {
      this.loading = true;
      try {
        const { data } = await api.get("/service-orders/");
        this.orders = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar órdenes.", "error");
      } finally {
        this.loading = false;
      }
    },
    async changeStatus(orderId, newStatus) {
      const msgs = {
        en_proceso: "¿Está seguro de iniciar esta orden?",
        completada: "¿Está seguro de marcar esta orden como completada?",
        cancelada: "¿Está seguro de cancelar esta orden?",
      };
      if (!window.confirm(msgs[newStatus] || "¿Está seguro de cambiar el estado?")) return;
      try {
        await api.patch(`/service-orders/${orderId}/status`, { estado: newStatus });
        this.showAlert(`Orden #${orderId} actualizada a "${this.statusLabel(newStatus)}".`);
        await this.fetchOrders();
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cambiar estado.", "error");
      }
    },
  },
  mounted() {
    this.fetchOrders();
  },
};
</script>

<style scoped>
.mecanico-orders {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
.header { margin-bottom: 20px; }
.header h1 { font-size: 1.8rem; color: #1a1a1a; }
.loading-state, .empty-state {
  text-align: center; padding: 40px; color: #64748b; font-size: 1rem;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.data-table th {
  background: #f8fafc;
  padding: 12px 16px;
  text-align: left;
  font-weight: 700;
  font-size: 13px;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e2e8f0;
}
.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
}
.desc-cell { max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.actions-cell { display: flex; gap: 6px; }
.badge {
  display: inline-block; padding: 3px 10px; border-radius: 12px;
  font-size: 12px; font-weight: 600; text-transform: uppercase;
}
.badge-pendiente { background: #fef3c7; color: #92400e; }
.badge-en_proceso { background: #dbeafe; color: #1e40af; }
.badge-completada { background: #d1fae5; color: #065f46; }
.badge-cancelada { background: #fee2e2; color: #991b1b; }
.btn-sm {
  padding: 5px 12px; border: none; border-radius: 5px;
  cursor: pointer; font-size: 12px; font-weight: 600;
}
.btn-start { background: #dbeafe; color: #1e40af; }
.btn-start:hover { background: #bfdbfe; }
.btn-complete { background: #d1fae5; color: #065f46; }
.btn-complete:hover { background: #a7f3d0; }
.btn-cancel-order { background: #fee2e2; color: #991b1b; }
.btn-cancel-order:hover { background: #fecaca; }
.text-muted { color: #94a3b8; font-size: 13px; }
</style>
