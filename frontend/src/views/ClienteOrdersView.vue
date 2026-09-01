<template>
  <div class="cliente-orders">
    <div class="header">
      <h1>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        Mi Panel
      </h1>
      <div class="nav-tabs">
        <button :class="['nav-tab', { active: activeTab === 'ordenes' }]" @click="activeTab = 'ordenes'">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 14l2 2 4-4"/></svg>
          Órdenes
        </button>
        <button :class="['nav-tab', { active: activeTab === 'motos' }]" @click="switchToMotos">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="14" r="4"/><circle cx="18" cy="14" r="4"/><path d="M6 14h12"/><path d="M16 4h-4l-3 5h7l2 3"/><path d="M3 10h3l1-2"/></svg>
          Mis Motos
        </button>
      </div>
    </div>

    <div v-if="alert.message" :class="['alert', 'alert-' + alert.type]">
      {{ alert.message }}
      <button class="alert-close" @click="alert.message = ''">×</button>
    </div>

    <div v-if="activeTab === 'ordenes'">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando órdenes...</p>
      </div>
      <div v-else-if="orders.length === 0" class="empty-state">No tienes órdenes de servicio registradas.</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Moto</th>
            <th>Mecánico</th>
            <th>Descripción</th>
            <th>Estado</th>
            <th>Fecha Creación</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in orders" :key="o.id">
            <td data-label="ID">{{ o.id }}</td>
            <td data-label="Moto">{{ o.moto_marca }} {{ o.moto_modelo }} ({{ o.moto_placa }})</td>
            <td data-label="Mecánico">{{ o.mecanico_nombre }}</td>
            <td data-label="Descripción" class="desc-cell">{{ o.descripcion }}</td>
            <td data-label="Estado"><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></td>
            <td data-label="Fecha">{{ formatDate(o.fecha_creacion) }}</td>
            <td class="actions-cell">
              <button class="btn-sm btn-view" @click="openDetail(o)">Ver</button>
              <button v-if="o.estado === 'en_proceso'" class="btn-sm btn-chat" @click="openChat(o)">Chat</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Mobile cards -->
      <div class="cliente-mobile-cards">
        <div v-for="o in orders" :key="'m-' + o.id" class="cliente-mobile-card">
          <div class="cliente-mobile-row"><span class="cliente-mobile-lbl">ID:</span> <span class="cliente-mobile-val">{{ o.id }}</span></div>
          <div class="cliente-mobile-row"><span class="cliente-mobile-lbl">Moto:</span> <span class="cliente-mobile-val">{{ o.moto_marca }} {{ o.moto_modelo }} ({{ o.moto_placa }})</span></div>
          <div class="cliente-mobile-row"><span class="cliente-mobile-lbl">Mecánico:</span> <span class="cliente-mobile-val">{{ o.mecanico_nombre }}</span></div>
          <div class="cliente-mobile-row"><span class="cliente-mobile-lbl">Descripción:</span> <span class="cliente-mobile-val">{{ o.descripcion }}</span></div>
          <div class="cliente-mobile-row"><span class="cliente-mobile-lbl">Estado:</span> <span class="cliente-mobile-val"><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></span></div>
          <div class="cliente-mobile-row"><span class="cliente-mobile-lbl">Fecha:</span> <span class="cliente-mobile-val">{{ formatDate(o.fecha_creacion) }}</span></div>
          <div class="cliente-mobile-row cliente-mobile-actions">
            <button class="btn-sm btn-view" @click="openDetail(o)">Ver</button>
            <button v-if="o.estado === 'en_proceso'" class="btn-sm btn-chat" @click="openChat(o)">Chat</button>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="!loading && totalPages > 1" class="pagination">
        <button class="page-btn" :disabled="page <= 1" @click="goToPage(page - 1)" title="Página anterior">&#9664;</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="page >= totalPages" @click="goToPage(page + 1)" title="Página siguiente">&#9654;</button>
      </div>
    </div>

    <div v-if="activeTab === 'motos'">
      <div v-if="motosLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando motos...</p>
      </div>
      <div v-else-if="motos.length === 0" class="empty-state">No tienes motos registradas.</div>
      <div v-else class="motos-grid">
        <div v-for="m in motos" :key="m.id" class="moto-card">
          <div class="moto-card-header">
            <span class="moto-marca">{{ m.marca }}</span>
            <span class="moto-modelo">{{ m.modelo }}</span>
          </div>
          <div class="moto-card-body">
            <div class="moto-detail"><span class="moto-label">Placa:</span> {{ m.placa }}</div>
            <div class="moto-detail"><span class="moto-label">Año:</span> {{ m.anio }}</div>
            <div class="moto-detail"><span class="moto-label">Color:</span> <span v-if="m.color" class="color-dot" :style="{ backgroundColor: colorHex(m.color) }"></span> {{ m.color || m.gama_color }}</div>
          </div>
          <div class="moto-card-actions">
            <button v-if="m.codigo_qr" class="btn-sm btn-view" @click="showMotoQR(m)">Ver QR</button>
            <button v-if="m.codigo_qr" class="btn-sm btn-download" @click="downloadQR(m.id)">Descargar QR</button>
            <button class="btn-sm btn-history" @click="showMotoHistory(m)">Historial</button>
          </div>
        </div>
      </div>
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
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="14" r="4"/><circle cx="18" cy="14" r="4"/><path d="M6 14h12"/><path d="M16 4h-4l-3 5h7l2 3"/><path d="M3 10h3l1-2"/></svg>
              </div>
              <div>
                <span class="detail-label">Moto</span>
                <span class="detail-value moto-value"><span>{{ detail.moto_marca }} {{ detail.moto_modelo }}</span><span><span class="detail-sub">Placa:</span> {{ detail.moto_placa }}</span><span><span class="detail-sub">Año:</span> {{ detail.moto_anio }}</span></span>
              </div>
            </div>
            <div class="detail-item" v-if="detail.moto_color_especifico || detail.moto_color">
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
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              </div>
              <div>
                <span class="detail-label">Mecánico</span>
                <span class="detail-value">{{ detail.mecanico_nombre }}</span>
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

          <!-- Progress Tracker -->
          <div class="detail-section">
            <h3>Progreso del Servicio</h3>
            <div class="progress-tracker">
              <div class="progress-step" :class="{ completed: pasoCompletado('pendiente'), active: detail.estado === 'pendiente', cancelled: detail.estado === 'cancelada' }">
                <div class="step-icon">1</div>
                <div class="step-label">Recibida</div>
              </div>
              <div class="progress-line" :class="{ completed: pasoCompletado('en_proceso'), cancelled: detail.estado === 'cancelada' }"></div>
              <div class="progress-step" :class="{ completed: pasoCompletado('en_proceso'), active: detail.estado === 'en_proceso', cancelled: detail.estado === 'cancelada' }">
                <div class="step-icon">2</div>
                <div class="step-label">En Proceso</div>
              </div>
              <div class="progress-line" :class="{ completed: detail.estado === 'completada', cancelled: detail.estado === 'cancelada' }"></div>
              <div class="progress-step" :class="{ completed: detail.estado === 'completada', cancelled: detail.estado === 'cancelada' }">
                <div class="step-icon" v-if="detail.estado !== 'cancelada'">3</div>
                <div class="step-icon cancelled-icon" v-else>✕</div>
                <div class="step-label">{{ detail.estado === 'cancelada' ? 'Cancelada' : 'Completada' }}</div>
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
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showDetail = false">Cerrar</button>
        </div>
      </div>
    </div>

    <!-- Chat Modal -->
    <ChatModal
      v-if="showChatModal"
      :orden-id="chatOrdenId"
      :my-role="clienteUser.rol"
      :my-id="clienteUser.id"
      :can-chat="true"
      @close="showChatModal = false"
    />

    <!-- Modal QR -->
    <div v-if="showQRModal" class="modal-overlay" @click.self="showQRModal = false">
      <div class="modal modal-sm">
        <div class="modal-topbar">
          <div class="topbar-left">
            <span class="topbar-id">QR de {{ qrMoto.marca }} {{ qrMoto.modelo }}</span>
          </div>
          <button class="modal-close" @click="showQRModal = false">&times;</button>
        </div>
        <div class="modal-body qr-body">
          <img :src="qrMoto.codigo_qr" alt="QR" class="qr-image" />
          <p class="qr-placa">Placa: {{ qrMoto.placa }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showQRModal = false">Cerrar</button>
        </div>
      </div>
    </div>

    <!-- Modal Historial -->
    <div v-if="showHistoryModal" class="modal-overlay" @click.self="showHistoryModal = false">
      <div class="modal modal-lg">
        <div class="modal-topbar">
          <div class="topbar-left">
            <span class="topbar-id">Historial — {{ historyMoto.marca }} {{ historyMoto.modelo }} ({{ historyMoto.placa }})</span>
          </div>
          <button class="modal-close" @click="showHistoryModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="historyLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Cargando historial...</p>
          </div>
          <div v-else-if="motoHistory.length === 0" class="empty-state">Esta moto no tiene órdenes de servicio.</div>
          <div v-else class="history-list">
            <div v-for="h in motoHistory" :key="h.id" class="history-item" :class="'history-' + h.estado">
              <div class="history-icon">
                <span v-if="h.estado === 'completada'">✓</span>
                <span v-else-if="h.estado === 'cancelada'">✕</span>
                <span v-else>●</span>
              </div>
              <div class="history-info">
                <div class="history-header">
                  <span class="history-id">Orden #{{ h.id }}</span>
                  <span :class="['badge', 'badge-' + h.estado]">{{ statusLabel(h.estado) }}</span>
                </div>
                <div class="history-meta">{{ h.mecanico_nombre }} — {{ formatDate(h.fecha_creacion) }}</div>
                <div class="history-desc">{{ h.descripcion }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showHistoryModal = false">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import ChatModal from "@/components/ChatModal.vue";
import orderSocket from "@/services/orderSocket";

export default {
  name: "ClienteOrders",
  components: { ChatModal },
  data() {
    return {
      alert: { message: "", type: "success" },
      activeTab: "ordenes",
      loading: false,
      orders: [],
      showDetail: false,
      detail: null,
      showChatModal: false,
      chatOrdenId: null,
      motos: [],
      motosLoading: false,
      showQRModal: false,
      qrMoto: null,
      showHistoryModal: false,
      historyMoto: null,
      motoHistory: [],
      historyLoading: false,
      page: 1,
      pageSize: 15,
      totalItems: 0,
      totalPages: 0,
    };
  },
  computed: {
    clienteUser() {
      return useAuthStore().user || { id: 0, rol: "cliente" };
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
    switchToMotos() {
      this.activeTab = "motos";
      if (this.motos.length === 0) this.fetchMotos();
    },
    async fetchMotos() {
      this.motosLoading = true;
      try {
        const { data } = await api.get("/users/clients/me/motos");
        this.motos = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar motos.", "error");
      } finally {
        this.motosLoading = false;
      }
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
    openChat(order) {
      this.chatOrdenId = order.id;
      this.showChatModal = true;
    },
    async openDetail(o) {
      try {
        const { data } = await api.get(`/service-orders/${o.id}`);
        this.detail = data;
        this.showDetail = true;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar detalle.", "error");
      }
    },
    pasoCompletado(estado) {
      const orden = ["pendiente", "en_proceso", "completada"];
      return orden.indexOf(this.detail.estado) > orden.indexOf(estado);
    },
    showMotoQR(moto) {
      this.qrMoto = moto;
      this.showQRModal = true;
    },
    async showMotoHistory(moto) {
      this.historyMoto = moto;
      this.showHistoryModal = true;
      this.historyLoading = true;
      this.motoHistory = [];
      try {
        const { data } = await api.get(`/service-orders/moto/${moto.id}/history`);
        this.motoHistory = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar historial.", "error");
      } finally {
        this.historyLoading = false;
      }
    },
    async downloadQR(motoClienteId) {
      try {
        const { data } = await api.get(`/users/clients/motos/${motoClienteId}/qr/download`, { responseType: "blob" });
        const url = window.URL.createObjectURL(new Blob([data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `QR_moto_${motoClienteId}.png`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al descargar QR", "error");
      }
    },
    openOrderFromRoute() {
      const orderId = this.$route.query.order_id;
      if (!orderId) return;
      if (this.$route.query.open_chat === "1") {
        this.chatOrdenId = Number(orderId);
        this.showChatModal = true;
        this.clearOrderRouteQuery();
        return;
      }
      api.get(`/service-orders/${orderId}`).then(({ data }) => {
        this.detail = data;
        this.showDetail = true;
      }).catch(() => {});
      this.clearOrderRouteQuery();
    },
    clearOrderRouteQuery() {
      if (this.$route.query.order_id || this.$route.query.open_chat) {
        this.$router.replace({ path: this.$route.path, query: {} });
      }
    },
    onOrderUpdated(event) {
      this.fetchOrders();
      this.fetchCount();
      if (event && event.detail) {
        const orderId = event.detail.orden_servicio_id;
        const newStatus = event.detail.estado;
        if (this.showChatModal && this.chatOrdenId === orderId && newStatus && newStatus !== "en_proceso") {
          this.showChatModal = false;
          this.showAlert(`El chat se ha cerrado porque la orden ha sido ${newStatus === "completada" ? "completada" : "cancelada"}.`, "info");
        }
        if (this.detail && this.detail.id === orderId && newStatus) {
          this.detail.estado = newStatus;
        }
      }
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
.cliente-orders {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.header h1 { font-size: 1.8rem; color: #1a1a1a; }
.nav-tabs { display: flex; gap: 4px; background: #f1f5f9; border-radius: 10px; padding: 3px; }
.nav-tab { display: flex; align-items: center; gap: 6px; padding: 8px 16px; border: none; border-radius: 8px; background: transparent; font-size: 0.85rem; font-weight: 600; color: #64748b; cursor: pointer; transition: all 0.2s; }
.nav-tab.active { background: #fff; color: #1a1a1a; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.nav-tab svg { flex-shrink: 0; }
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
.actions-cell { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.cliente-mobile-actions { display: flex; align-items: center; gap: 8px; margin-top: 8px; border-top: 1px solid #f1f5f9; padding-top: 8px; }
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
.btn-sm + .btn-sm { margin-left: 8px; }
.btn-view { background: #eff6ff; color: #2563eb; }
.btn-view:hover { background: #dbeafe; }
.btn-chat { background: #075e54; color: #fff; }
.btn-chat:hover { background: #054d44; }
.btn-download { background: #ffaa00; color: #1a1a1a; }
.btn-download:hover { background: #e69900; }
.btn-history { background: #f3e8ff; color: #7c3aed; }
.btn-history:hover { background: #e9d5ff; }
.btn-qr { padding: 10px 20px; background: #ffaa00; color: #1a1a1a; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; }
.btn-qr:hover { background: #e69900; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15,23,42,0.4); backdrop-filter: blur(8px);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal {
  background: #fff; border-radius: 20px; width: 90%; max-width: 640px;
  overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
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
.modal-close { background: none; border: none; width: 36px; height: 36px; border-radius: 8px; cursor: pointer; color: #64748b; font-size: 24px; font-weight: 400; line-height: 1; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
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
.detail-section { margin-top: 20px; }
.detail-section h3 { font-size: 1rem; margin-bottom: 8px; color: #1a1a1a; }
.progress-tracker {
  display: flex; align-items: center; justify-content: center; margin: 16px 0;
}
.progress-step { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.step-icon {
  width: 36px; height: 36px; border-radius: 50%;
  background: #e2e8f0; color: #94a3b8;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 0.9rem; transition: all 0.3s;
}
.progress-step.active .step-icon { background: #ffaa00; color: #1a1a1a; box-shadow: 0 0 0 4px rgba(255,170,0,0.2); }
.progress-step.completed .step-icon { background: #16a34a; color: #fff; }
.progress-step.cancelled .step-icon { background: #ef4444; color: #fff; }
.cancelled-icon { font-size: 1rem; }
.step-label { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.progress-step.active .step-label { color: #ffaa00; }
.progress-step.completed .step-label { color: #16a34a; }
.progress-step.cancelled .step-label { color: #ef4444; }
.progress-line {
  width: 50px; height: 3px; background: #e2e8f0;
  margin: 0 6px; margin-bottom: 22px; border-radius: 2px; transition: background 0.3s;
}
.progress-line.completed { background: #16a34a; }
.progress-line.cancelled { background: #ef4444; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 28px; border-top: 1px solid #f1f5f9; }
.btn-cancel { padding: 10px 20px; background: #f1f5f9; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
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

/* Motos Grid */
.motos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.moto-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.moto-card-header { background: #f8fafc; padding: 14px 16px; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; gap: 8px; }
.moto-marca { font-weight: 800; font-size: 0.85rem; color: #1a1a1a; text-transform: uppercase; }
.moto-modelo { font-size: 0.85rem; color: #64748b; }
.moto-card-body { padding: 14px 16px; }
.moto-detail { font-size: 0.85rem; color: #334155; margin-bottom: 4px; }
.color-dot { display: inline-block; width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; border: 1px solid #d1d5db; vertical-align: middle; margin-right: 3px; }
.moto-label { color: #94a3b8; font-weight: 600; }
.moto-card-actions { padding: 10px 16px; border-top: 1px solid #f1f5f9; display: flex; gap: 8px; }

/* QR Modal */
.modal-sm { max-width: 420px; text-align: center; }
.qr-body { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 16px 0; }
.qr-image { width: 280px; height: 280px; border-radius: 12px; border: 2px solid #f1f5f9; }
.qr-placa { font-size: 1.1rem; font-weight: 700; color: #1a1a1a; }

/* History List in Modal */
.history-list { display: flex; flex-direction: column; }
.history-item { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f8fafc; }
.history-item:last-child { border-bottom: none; }
.history-icon { width: 32px; height: 32px; border-radius: 50%; background: #e2e8f0; color: #94a3b8; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; margin-top: 2px; }
.history-completada .history-icon { background: #d1fae5; color: #065f46; }
.history-cancelada .history-icon { background: #fee2e2; color: #991b1b; }
.history-pendiente .history-icon { background: #fef3c7; color: #92400e; }
.history-en_proceso .history-icon { background: #dbeafe; color: #1e40af; }
.history-info { flex: 1; min-width: 0; }
.history-header { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.history-id { font-weight: 700; font-size: 0.85rem; color: #1a1a1a; }
.history-meta { font-size: 0.78rem; color: #94a3b8; margin-bottom: 4px; }
.history-desc { font-size: 0.82rem; color: #475569; line-height: 1.4; }
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
/* ===== MOBILE / PWA native feel ===== */
@media (max-width: 768px) {
  .cliente-orders {
    padding: 12px 12px 80px;
  }
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .header h1 {
    font-size: 1.2rem;
  }
  .nav-tabs {
    width: 100%;
    display: flex;
  }
  .nav-tab {
    flex: 1;
    justify-content: center;
    padding: 10px 12px;
    font-size: 13px;
    border-radius: 8px;
  }
  .btn-sm {
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
  }
  .modal {
    width: 95%;
    border-radius: 16px;
    max-height: 80vh;
  }
  .modal-body { padding: 16px; }
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .progress-tracker {
    transform: scale(0.85);
  }
  .progress-line {
    width: 30px;
  }
  .motos-grid {
    grid-template-columns: 1fr;
  }
  .pagination {
    padding: 8px 0 20px;
  }
}
html.dark .data-table tr {
  background: #1a1f2e;
  border-color: #1e293b;
}
html.dark .moto-card {
  background: #1a1f2e;
  border-color: #1e293b;
}
html.dark .header h1 { color: #f1f5f9 !important; }
html.dark .nav-tabs { background: var(--bg-muted) !important; }
html.dark .nav-tab { color: var(--text-muted) !important; }
html.dark .nav-tab.active { background: var(--bg-card) !important; color: var(--color-primary) !important; }
html.dark .data-table { background: transparent !important; }
html.dark .data-table th { background: var(--bg-muted) !important; color: var(--text-secondary) !important; border-bottom-color: var(--border-default) !important; }
html.dark .data-table td { color: var(--text-default) !important; border-bottom-color: var(--border-light) !important; }
html.dark .btn-view { background: #1e3a5f !important; color: #93c5fd !important; }
html.dark .btn-chat { background: #064e3b !important; color: #6ee7b7 !important; }
html.dark .btn-download { background: #78350f !important; color: #fde68a !important; }
html.dark .btn-history { background: #2e1065 !important; color: #c4b5fd !important; }
html.dark .btn-qr { background: #78350f !important; color: #fde68a !important; }
html.dark .cliente-mobile-card { background: var(--bg-card) !important; border-color: var(--border-default) !important; box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important; }
html.dark .cliente-mobile-val { color: var(--text-default) !important; }
html.dark .cliente-mobile-actions { border-top-color: var(--border-light) !important; }
html.dark .moto-card { background: var(--bg-card) !important; border-color: var(--border-default) !important; }
html.dark .moto-card-header { background: var(--bg-muted) !important; }
html.dark .moto-marca { color: var(--text-default) !important; }
html.dark .moto-modelo { color: var(--text-muted) !important; }
html.dark .moto-detail { color: var(--text-secondary) !important; }
html.dark .moto-label { color: var(--text-muted) !important; }
html.dark .moto-card-actions { border-top-color: var(--border-light) !important; }
html.dark .page-btn { background: var(--bg-card) !important; border-color: var(--border-default) !important; color: var(--text-secondary) !important; }
html.dark .btn-cancel { background: #334155 !important; color: #cbd5e1 !important; }
</style>
