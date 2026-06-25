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
          <td>{{ capitalize(o.cliente_nombre) }}</td>
          <td>{{ o.moto_marca }} {{ o.moto_modelo }} ({{ o.moto_placa }})</td>
          <td class="desc-cell">{{ o.descripcion }}</td>
          <td><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></td>
          <td>{{ formatDate(o.fecha_creacion) }}</td>
          <td class="actions-cell">
            <button class="btn-sm btn-view" @click="openDetail(o)">Ver</button>
            <button v-if="o.estado === 'en_proceso'" class="btn-sm btn-chat" @click="openChat(o)">Chat</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Modal Detalle -->
    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <button class="modal-close" @click="showDetail = false">×</button>
        </div>
        <div class="modal-body" v-if="detail">
          <div class="status-badge-wrap">
            <span :class="['badge', 'badge-' + detail.estado]">{{ statusLabel(detail.estado) }}</span>
            <span class="order-id-label">Orden #{{ detail.id }}</span>
          </div>
          <div class="detail-grid">
            <div class="detail-field">
              <span class="detail-label">Estado</span>
              <span :class="['badge', 'badge-' + detail.estado]">{{ statusLabel(detail.estado) }}</span>
            </div>
            <div class="detail-field">
              <span class="detail-label">Cliente</span>
              <span>{{ capitalize(detail.cliente_nombre) }}</span>
            </div>
            <div class="detail-field">
              <span class="detail-label">Moto</span>
              <span>{{ detail.moto_marca }} {{ detail.moto_modelo }} ({{ detail.moto_placa }})<template v-if="detail.moto_anio"> - {{ detail.moto_anio }}</template></span>
            </div>
            <div class="detail-field">
              <span class="detail-label">Color</span>
              <span>{{ detail.moto_color_especifico || detail.moto_color }}</span>
            </div>
            <div class="detail-field">
              <span class="detail-label">Fecha de Creación</span>
              <span>{{ formatDate(detail.fecha_creacion) }}</span>
            </div>
            <div class="detail-field" v-if="detail.fecha_cierre">
              <span class="detail-label">Fecha de Cierre</span>
              <span>{{ formatDate(detail.fecha_cierre) }}</span>
            </div>
          </div>
          <div class="detail-section">
            <h3>Descripción</h3>
            <p>{{ detail.descripcion }}</p>
          </div>

          <!-- Cambiar estado -->
          <div class="detail-section" v-if="detail.estado !== 'completada' && detail.estado !== 'cancelada'">
            <h3>Cambiar Estado</h3>
            <div class="status-actions" v-if="detail.estado === 'pendiente'">
              <button class="btn-sm btn-start" @click="changeStatusFromDetail('en_proceso')">Iniciar</button>
              <button class="btn-sm btn-cancel-order" @click="changeStatusFromDetail('cancelada')">Cancelar</button>
            </div>
            <div class="status-actions" v-else-if="detail.estado === 'en_proceso'">
              <button class="btn-sm btn-complete" @click="changeStatusFromDetail('completada')">Completar</button>
              <button class="btn-sm btn-cancel-order" @click="changeStatusFromDetail('cancelada')">Cancelar</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Modal -->
    <ChatModal
      v-if="showChatModal"
      :orden-id="chatOrdenId"
      :my-role="mecanicoUser.rol"
      :my-id="mecanicoUser.id"
      :can-chat="true"
      @close="showChatModal = false"
    />
  </div>
</template>

<script>
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import ChatModal from "@/components/ChatModal.vue";

export default {
  name: "MecanicoOrders",
  components: { ChatModal },
  data() {
    return {
      alert: { message: "", type: "success" },
      loading: false,
      orders: [],
      showDetail: false,
      detail: null,
      showChatModal: false,
      chatOrdenId: null,
    };
  },
  computed: {
    mecanicoUser() {
      return useAuthStore().user || { id: 0, rol: "mecanico" };
    },
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
    capitalize(s) {
      if (!s) return "";
      return s.replace(/\b\w/g, c => c.toUpperCase());
    },
    openChat(order) {
      this.chatOrdenId = order.id;
      this.showChatModal = true;
    },
    openDetail(o) {
      this.detail = { ...o };
      this.showDetail = true;
      api.get(`/service-orders/${o.id}`).then(({ data }) => {
        this.detail = data;
      }).catch(() => {});
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
        this.showAlert(`Orden #${orderId} actualizada a "${this.statusLabel(newStatus)}".`, newStatus === "cancelada" ? "error" : undefined);
        await this.fetchOrders();
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cambiar estado.", "error");
      }
    },
    async changeStatusFromDetail(newStatus) {
      if (!this.detail) return;
      await this.changeStatus(this.detail.id, newStatus);
      if (this.detail) this.detail.estado = newStatus;
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
.actions-cell { display: flex; gap: 6px; flex-wrap: wrap; }
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
.btn-view { background: #eff6ff; color: #2563eb; }
.btn-view:hover { background: #dbeafe; }
.btn-chat { background: #075e54; color: #fff; }
.btn-chat:hover { background: #054d44; }
.btn-start { background: #dbeafe; color: #1e40af; }
.btn-start:hover { background: #bfdbfe; }
.btn-complete { background: #d1fae5; color: #065f46; }
.btn-complete:hover { background: #a7f3d0; }
.btn-cancel-order { background: #fee2e2; color: #991b1b; }
.btn-cancel-order:hover { background: #fecaca; }
.text-muted { color: #94a3b8; font-size: 13px; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15,23,42,0.5); backdrop-filter: blur(6px);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal {
  background: #fff; border-radius: 20px; width: 90%; max-width: 640px;
  padding: 28px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  max-height: 90vh; overflow-y: auto;
}
.modal-header {
  display: flex; justify-content: flex-end; align-items: center; margin-bottom: 20px;
}
.modal-header h2 { font-size: 1.35rem; font-weight: 800; color: #1a1a1a; letter-spacing: -0.3px; }
.modal-close {
  background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 8px;
  font-size: 18px; cursor: pointer; color: #64748b;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.modal-close:hover { background: #e2e8f0; color: #1a1a1a; }
.status-badge-wrap {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 20px; padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
.status-badge-wrap .badge { font-size: 13px; padding: 6px 16px; border-radius: 20px; }
.order-id-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.detail-field { display: flex; flex-direction: column; gap: 3px; }
.detail-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.6px; }
.detail-field > span:last-child { font-size: 14px; font-weight: 600; color: #1a1a1a; }
.detail-section { margin-top: 20px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
.detail-section h3 { font-size: 0.95rem; font-weight: 700; color: #1a1a1a; margin-bottom: 10px; }
.status-actions { display: flex; gap: 10px; }
.reassign-row { display: flex; gap: 8px; }
.form-control { padding: 8px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 0.9rem; flex: 1; }
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}
.alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.alert-close { background: none; border: none; font-size: 1.3rem; cursor: pointer; color: inherit; padding: 0 4px; }
</style>
