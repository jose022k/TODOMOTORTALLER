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
            <td>{{ o.id }}</td>
            <td>{{ o.moto_marca }} {{ o.moto_modelo }} ({{ o.moto_placa }})</td>
            <td>{{ o.mecanico_nombre }}</td>
            <td class="desc-cell">{{ o.descripcion }}</td>
            <td><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></td>
            <td>{{ formatDate(o.fecha_creacion) }}</td>
            <td>
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
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>Orden #{{ detail.id }}</h2>
          <button class="modal-close" @click="showDetail = false">×</button>
        </div>
        <div class="modal-body" v-if="detail">
          <div class="detail-grid">
            <div class="detail-field">
              <span class="detail-label">Estado</span>
              <span :class="['badge', 'badge-' + detail.estado]">{{ statusLabel(detail.estado) }}</span>
            </div>
            <div class="detail-field">
              <span class="detail-label">Moto</span>
              <span class="moto-info">{{ detail.moto_marca }} {{ detail.moto_modelo }}<br>Placa: {{ detail.moto_placa }}<br>Año: {{ detail.moto_anio }}</span>
            </div>
            <div class="detail-field" v-if="detail.moto_color_especifico">
              <span class="detail-label">Color</span>
              <span><span class="color-dot" :style="{ backgroundColor: colorHex(detail.moto_color_especifico) }"></span> {{ detail.moto_color_especifico }}</span>
            </div>
            <div class="detail-field" v-else-if="detail.moto_color">
              <span class="detail-label">Color</span>
              <span>{{ detail.moto_color }}</span>
            </div>
            <div class="detail-field">
              <span class="detail-label">Mecánico</span>
              <span>{{ detail.mecanico_nombre }}</span>
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

          <div class="detail-section">
            <h3>Descripción</h3>
            <p>{{ detail.descripcion }}</p>
          </div>
        </div>
        <div class="modal-footer"></div>
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
        <div class="modal-header">
          <h2>QR de {{ qrMoto.marca }} {{ qrMoto.modelo }}</h2>
          <button class="modal-close" @click="showQRModal = false">×</button>
        </div>
        <div class="modal-body qr-body">
          <img :src="qrMoto.codigo_qr" alt="QR" class="qr-image" />
          <p class="qr-placa">Placa: {{ qrMoto.placa }}</p>
        </div>
        <div class="modal-footer"></div>
      </div>
    </div>

    <!-- Modal Historial -->
    <div v-if="showHistoryModal" class="modal-overlay" @click.self="showHistoryModal = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>Historial — {{ historyMoto.marca }} {{ historyMoto.modelo }} ({{ historyMoto.placa }})</h2>
          <button class="modal-close" @click="showHistoryModal = false">×</button>
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
        return;
      }
      api.get(`/service-orders/${orderId}`).then(({ data }) => {
        this.detail = data;
        this.showDetail = true;
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
  padding: 28px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
  max-height: 90vh; overflow-y: auto;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.modal-header h2 { font-size: 1.3rem; }
.modal-close { background: none; border: none; width: 36px; height: 36px; border-radius: 8px; font-size: 1.5rem; cursor: pointer; color: #94a3b8; display: inline-flex; align-items: center; justify-content: center; transition: all 0.2s; }
.modal-close:hover { background: #fee2e2; color: #dc2626; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.detail-field { font-size: 0.9rem; }
.detail-label { display: block; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 2px; }
.moto-info { line-height: 1.6; }
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
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
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
</style>
