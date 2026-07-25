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

    <!-- Paginación -->
    <div v-if="!loading && totalPages > 1" class="pagination">
      <button class="page-btn" :disabled="page <= 1" @click="goToPage(page - 1)" title="Página anterior">&#9664;</button>
      <span class="page-info">{{ page }} / {{ totalPages }}</span>
      <button class="page-btn" :disabled="page >= totalPages" @click="goToPage(page + 1)" title="Página siguiente">&#9654;</button>
    </div>

    <!-- Modal Detalle -->
    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal modal-lg" :class="'modal--' + detail?.estado">
        <div class="modal-topbar">
          <div class="topbar-left">
            <span :class="['badge', 'badge-' + detail?.estado]">{{ statusLabel(detail?.estado) }}</span>
            <span class="topbar-id">#{{ detail?.id }}</span>
          </div>
          <button class="modal-close" @click="showDetail = false">&times;</button>
        </div>
        <div class="modal-body" v-if="detail">
          <div class="detail-grid">
            <div class="detail-item">
              <div class="detail-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
              <div>
                <span class="detail-label">Cliente</span>
                <span class="detail-value">{{ capitalize(detail.cliente_nombre) }}</span>
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="14" r="4"/><circle cx="18" cy="14" r="4"/><path d="M6 14h12"/><path d="M16 4h-4l-3 5h7l2 3"/><path d="M3 10h3l1-2"/></svg>
              </div>
              <div>
                <span class="detail-label">Moto</span>
                <span class="detail-value moto-value"><span>{{ detail.moto_marca }} {{ detail.moto_modelo }}</span><span><span class="detail-sub">Placa:</span> {{ detail.moto_placa }}</span><span><span class="detail-sub">Año:</span> {{ detail.moto_anio }}</span></span>
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
              </div>
              <div>
                <span class="detail-label">Color</span>
                <span class="detail-value" v-if="detail.moto_color_especifico">
                  <span class="color-dot" :style="{ backgroundColor: colorHex(detail.moto_color_especifico) }"></span>
                  {{ detail.moto_color_especifico }}
                </span>
                <span class="detail-value" v-else>{{ detail.moto_color }}</span>
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              </div>
              <div>
                <span class="detail-label">Creada</span>
                <span class="detail-value">{{ formatDate(detail.fecha_creacion) }}</span>
              </div>
            </div>
            <div class="detail-item" v-if="detail.fecha_cierre">
              <div class="detail-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
              </div>
              <div>
                <span class="detail-label">Cerrada</span>
                <span class="detail-value">{{ formatDate(detail.fecha_cierre) }}</span>
              </div>
            </div>
          </div>

          <div class="detail-card">
            <div class="detail-card-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              <span>Descripción</span>
            </div>
            <p class="detail-card-body">{{ detail.descripcion }}</p>
          </div>

          <div class="detail-actions" v-if="detail.estado !== 'completada' && detail.estado !== 'cancelada'">
            <span class="actions-title">Acciones</span>
            <div class="actions-row" v-if="detail.estado === 'pendiente'">
              <button class="action-btn action-btn--start" @click="changeStatusFromDetail('en_proceso')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                Iniciar
              </button>
              <button class="action-btn action-btn--cancel" @click="changeStatusFromDetail('cancelada')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                Cancelar
              </button>
            </div>
            <div class="actions-row" v-else-if="detail.estado === 'en_proceso'">
              <button class="action-btn action-btn--complete" @click="changeStatusFromDetail('completada')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Completar
              </button>
              <button class="action-btn action-btn--cancel" @click="changeStatusFromDetail('cancelada')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                Cancelar
              </button>
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
import orderSocket from "@/services/orderSocket";

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
      page: 1,
      pageSize: 15,
      totalItems: 0,
      totalPages: 0,
      pollTimer: null,
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
        const skip = (this.page - 1) * this.pageSize;
        const { data } = await api.get("/service-orders/", { params: { skip, limit: this.pageSize } });
        this.orders = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar órdenes.", "error");
      } finally {
        this.loading = false;
      }
    },
    async fetchCount() {
      try {
        const { data } = await api.get("/service-orders/count");
        this.totalItems = data.total;
        this.totalPages = Math.ceil(this.totalItems / this.pageSize) || 1;
      } catch (e) {
        console.error("Error fetching count", e);
      }
    },
    async goToPage(p) {
      this.page = p;
      await this.fetchOrders();
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
      this.showDetail = false;
    },
    openOrderFromRoute() {
      const orderId = this.$route.query.order_id;
      if (!orderId) return;
      if (this.$route.query.open_chat === "1") {
        this.chatOrdenId = Number(orderId);
        this.showChatModal = true;
        return;
      }
      this.showDetail = true;
      api.get(`/service-orders/${orderId}`).then(({ data }) => {
        this.detail = data;
      }).catch(() => {});
    },
    onOrderUpdated() {
      this.fetchOrders();
      this.fetchCount();
    },
    colorHex(colorName) {
      const map = {
        Negro: "#1a1a1a", Azul: "#2563eb", Rojo: "#dc2626", Amarillo: "#eab308",
        Morado: "#7c3aed", Rosa: "#ec4899", Gris: "#94a3b8", Vinotinto: "#831843",
        Blanco: "#f8fafc", Verde: "#16a34a", Naranja: "#ea580c", Marrón: "#78350f",
        Plateado: "#d1d5db", Dorado: "#ca8a04",
      };
      return map[colorName] || "#e2e8f0";
    },
  },
  mounted() {
    this.fetchOrders();
    this.fetchCount();
    this.openOrderFromRoute();
    orderSocket.enable();
    window.addEventListener("order-updated", this.onOrderUpdated);
  },
  beforeUnmount() {
    window.removeEventListener("order-updated", this.onOrderUpdated);
  },
  watch: {
    $route() {
      if (this.$route.query.order_id) {
        this.openOrderFromRoute();
      }
    },
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
  overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  max-height: 90vh; overflow-y: auto;
}
.modal--pendiente { border-top: 4px solid #f59e0b; }
.modal--en_proceso { border-top: 4px solid #3b82f6; }
.modal-topbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 28px; border-bottom: 1px solid #f1f5f9;
}
.topbar-left { display: flex; align-items: center; gap: 10px; }
.topbar-left .badge { font-size: 13px; padding: 6px 16px; border-radius: 20px; }
.topbar-id { font-size: 14px; font-weight: 700; color: #94a3b8; letter-spacing: 0.3px; }
.modal-close {
  background: none; border: none; width: 36px; height: 36px; border-radius: 8px;
  cursor: pointer; color: #64748b; font-size: 24px; font-weight: 400; line-height: 1;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.modal-close:hover { background: #fee2e2; color: #dc2626; }
.modal-body { padding: 24px 28px 28px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.detail-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 12px; background: #f8fafc; border-radius: 10px;
}
.detail-icon {
  width: 32px; height: 32px; border-radius: 8px;
  background: #fff; color: #ffaa00;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.detail-label { display: block; font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 1px; }
.detail-value { font-size: 13px; font-weight: 600; color: #1a1a1a; display: flex; align-items: center; gap: 6px; }
.color-dot { display: inline-block; width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; border: 1px solid #d1d5db; }
.detail-value.moto-value { flex-direction: column; align-items: flex-start; gap: 4px; }
.detail-sub { font-weight: 700; color: #94a3b8; }
.detail-card {
  margin-bottom: 24px; padding: 16px; background: #f8fafc; border-radius: 12px;
}
.detail-card-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.detail-card-body { margin: 0; font-size: 14px; color: #475569; line-height: 1.6; }
.detail-actions { margin-top: 0; }
.detail-actions + .detail-actions { margin-top: 20px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
.actions-title {
  display: block; font-size: 12px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;
}
.actions-row { display: flex; gap: 10px; }
.action-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border: none; border-radius: 10px;
  font-size: 13px; font-weight: 700; cursor: pointer;
  transition: all 0.2s;
}
.action-btn svg { flex-shrink: 0; }
.action-btn--start { background: #dbeafe; color: #1e40af; }
.action-btn--start:hover { background: #bfdbfe; }
.action-btn--complete { background: #d1fae5; color: #065f46; }
.action-btn--complete:hover { background: #a7f3d0; }
.action-btn--cancel { background: #fef2f2; color: #991b1b; }
.action-btn--cancel:hover { background: #fecaca; }
.action-btn--assign { background: #ede9fe; color: #5b21b6; }
.action-btn--assign:hover { background: #ddd6fe; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.reassign-row { display: flex; gap: 10px; }
.form-control { padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 13px; flex: 1; background: #f8fafc; }
.form-control:focus { outline: none; border-color: #ffaa00; box-shadow: 0 0 0 3px rgba(255,170,0,0.1); background: #fff; }
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
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
  padding: 12px 0;
}
.page-btn {
  width: 36px;
  height: 36px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
  transition: all 0.15s;
}
.page-btn:hover:not(:disabled) {
  border-color: #ffaa00;
  color: #ffaa00;
}
.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.page-info {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  min-width: 60px;
  text-align: center;
}
</style>
