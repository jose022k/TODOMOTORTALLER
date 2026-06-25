<template>
  <div class="admin-orders">
    <div class="orders-header">
      <h1>Órdenes de Servicio</h1>
    </div>

    <!-- Alerta -->
    <div v-if="alert.message" :class="['alert', 'alert-' + alert.type]">
      {{ alert.message }}
      <button class="alert-close" @click="alert.message = ''">×</button>
    </div>

    <!-- Barra de herramientas -->
    <div class="toolbar">
      <select v-model="filterEstado" class="filter-select" @change="fetchOrders">
        <option value="">Todos los estados</option>
        <option value="pendiente">Pendiente</option>
        <option value="en_proceso">En Proceso</option>
        <option value="completada">Completada</option>
        <option value="cancelada">Cancelada</option>
      </select>
      <button class="btn-primary" @click="openCreateModal">+ Nueva Orden</button>
    </div>

    <!-- Tabla de órdenes -->
    <div v-if="loading" class="loading-state">Cargando órdenes...</div>
    <div v-else-if="orders.length === 0" class="empty-state">No se encontraron órdenes de servicio.</div>
    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Cliente</th>
          <th>Moto</th>
          <th>Mecánico</th>
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
          <td>{{ capitalize(o.mecanico_nombre) }}</td>
          <td><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></td>
          <td>{{ formatDate(o.fecha_creacion) }}</td>
          <td class="actions-cell">
            <button class="btn-sm btn-view" @click="openDetailModal(o)">Ver</button>
            <button v-if="o.estado === 'en_proceso'" class="btn-sm btn-chat" @click="openChat(o)">Chat</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Modal Crear Orden -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>Nueva Orden de Servicio</h2>
          <button class="modal-close" @click="showCreateModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Cliente</label>
            <select v-model="form.cliente_id" @change="onClientChange" class="form-control">
              <option value="">Seleccionar cliente...</option>
              <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.nombre }} ({{ c.cedula }})</option>
            </select>
          </div>

          <!-- Toggle: tipo de moto -->
          <div class="moto-toggle" v-if="form.cliente_id">
            <button :class="['toggle-btn', { active: motoMode === 'existente' }]" @click="motoMode = 'existente'; resetMotoForm()">Moto existente</button>
            <button :class="['toggle-btn', { active: motoMode === 'nueva' }]" @click="motoMode = 'nueva'; resetMotoForm()">Nueva moto del catálogo</button>
          </div>

          <!-- Moto existente -->
          <div v-if="motoMode === 'existente' && form.cliente_id" class="form-group">
            <label>Seleccionar moto del cliente</label>
            <select v-model="form.moto_cliente_id" class="form-control">
              <option value="">Seleccionar moto...</option>
              <option v-for="m in clientMotos" :key="m.id" :value="m.id">
                {{ m.marca }} {{ m.modelo }} — {{ m.placa }} ({{ m.anio }})
              </option>
            </select>
          </div>

          <!-- Nueva moto desde catálogo -->
          <div v-if="motoMode === 'nueva' && form.cliente_id" class="new-moto-section">
            <div class="form-group">
              <label>Marca</label>
              <select v-model="form.catalogoMarca" @change="onMarcaChange" class="form-control">
                <option value="">Seleccionar marca...</option>
                <option v-for="marca in marcas" :key="marca" :value="marca">{{ marca }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Modelo</label>
              <select v-model="form.catalogoModelo" @change="onModeloChange" class="form-control" :disabled="!form.catalogoMarca">
                <option value="">Seleccionar modelo...</option>
                <option v-for="m in modelosFiltrados" :key="m.id" :value="m.modelo">{{ m.modelo }}</option>
              </select>
            </div>
            <div class="form-group" v-if="modeloSeleccionado">
              <label>Color</label>
              <div v-if="!form.color" class="color-chips">
                <button
                  v-for="c in coloresDisponibles"
                  :key="c"
                  class="color-chip"
                  @click="form.color = c"
                  :style="{ backgroundColor: colorHex(c) }"
                >
                  {{ c }}
                </button>
              </div>
              <div v-else class="color-selected">
                <span class="color-chip selected" :style="{ backgroundColor: colorHex(form.color), borderColor: colorHex(form.color) }">
                  {{ form.color }}
                </span>
                <button class="btn-recolor" @click="form.color = ''">Seleccionar color nuevamente</button>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group half">
                <label>Placa</label>
                <input v-model="form.placa" type="text" class="form-control" placeholder="ABC-123" maxlength="20" />
              </div>
              <div class="form-group half">
                <label>Año</label>
                <input v-model="form.anio" type="number" class="form-control" placeholder="2026" min="1900" :max="new Date().getFullYear() + 1" />
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Mecánico Asignado</label>
            <select v-model="form.mecanico_id" class="form-control">
              <option value="">Seleccionar mecánico...</option>
              <option v-for="m in mechanics" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Descripción del servicio</label>
            <textarea v-model="form.descripcion" class="form-control" rows="4" placeholder="Describe el trabajo a realizar..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showCreateModal = false">Cancelar</button>
          <button class="btn-primary" @click="handleCreate" :disabled="!canCreate">Crear Orden</button>
        </div>
      </div>
    </div>

    <!-- Modal Detalle -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="showDetailModal = false">
      <div class="modal modal-lg" :class="'modal--' + detail?.estado">
        <div class="modal-topbar">
          <div class="topbar-left">
            <span :class="['badge', 'badge-' + detail?.estado]">{{ statusLabel(detail?.estado) }}</span>
            <span class="topbar-id">#{{ detail?.id }}</span>
          </div>
          <button class="modal-close" @click="showDetailModal = false">&times;</button>
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
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5Z"/><circle cx="9" cy="9" r="1"/><path d="m5 15 4-4 2 2 4-4 4 4"/></svg>
              </div>
              <div>
                <span class="detail-label">Moto</span>
                <span class="detail-value">{{ detail.moto_marca }} {{ detail.moto_modelo }} ({{ detail.moto_placa }})<template v-if="detail.moto_anio"> · {{ detail.moto_anio }}</template></span>
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"/></svg>
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
                <span class="detail-value">{{ capitalize(detail.mecanico_nombre) }}</span>
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

          <div class="detail-actions" v-if="canChangeStatus || (detail.estado !== 'completada' && detail.estado !== 'cancelada')">
            <span class="actions-title">Acciones</span>
            <div class="actions-bar">
              <div class="actions-row" v-if="detail.estado === 'pendiente'">
                <button class="action-btn action-btn--start" @click="changeStatus('en_proceso')">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                  Iniciar
                </button>
                <button class="action-btn action-btn--cancel" @click="changeStatus('cancelada')">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  Cancelar
                </button>
              </div>
              <div class="actions-row" v-else-if="detail.estado === 'en_proceso'">
                <button class="action-btn action-btn--complete" @click="changeStatus('completada')">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Completar
                </button>
                <button class="action-btn action-btn--cancel" @click="changeStatus('cancelada')">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  Cancelar
                </button>
              </div>
              <div class="reassign-inline" v-if="detail.estado !== 'completada' && detail.estado !== 'cancelada'">
                <select v-model="reassignMecanicoId" class="form-control">
                  <option value="">Reasignar mecánico...</option>
                  <option v-for="m in mechanics" :key="m.id" :value="m.id">{{ m.nombre }}</option>
                </select>
                <button class="action-btn action-btn--assign" @click="handleReassign" :disabled="!reassignMecanicoId">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>
                  Reasignar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Modal -->
    <ChatModal
      v-if="showChatModal"
      :orden-id="chatOrdenId"
      :my-role="adminUser.rol"
      :my-id="adminUser.id"
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
  name: "AdminServiceOrders",
  components: { ChatModal },
  data() {
    return {
      alert: { message: "", type: "success" },
      loading: false,
      orders: [],
      filterEstado: "",
      showCreateModal: false,
      showDetailModal: false,
      clients: [],
      mechanics: [],
      clientMotos: [],
      catalog: [],          // todos los items del catálogo
      motoMode: "existente", // "existente" | "nueva"
      form: {
        cliente_id: "",
        moto_cliente_id: "",
        catalogoMarca: "",
        catalogoModelo: "",
        placa: "",
        anio: "",
        mecanico_id: "",
        descripcion: "",
      },
      detail: null,
      reassignMecanicoId: "",
      showChatModal: false,
      chatOrdenId: null,
    };
  },
  computed: {
    marcas() {
      const set = new Set(this.catalog.map((m) => m.marca));
      return [...set].sort();
    },
    modelosFiltrados() {
      if (!this.form.catalogoMarca) return [];
      return this.catalog.filter((m) => m.marca === this.form.catalogoMarca);
    },
    modeloSeleccionado() {
      return this.catalog.find(
        (m) => m.marca === this.form.catalogoMarca && m.modelo === this.form.catalogoModelo
      );
    },
    coloresDisponibles() {
      if (!this.modeloSeleccionado) return [];
      return this.modeloSeleccionado.gama_color.split(",").map((c) => c.trim()).filter(Boolean);
    },
    canCreate() {
      if (!this.form.cliente_id || !this.form.mecanico_id || !this.form.descripcion.trim()) return false;
      if (this.motoMode === "existente") return !!this.form.moto_cliente_id;
      return !!(this.form.catalogoMarca && this.form.catalogoModelo && this.form.color && this.form.placa && this.form.anio);
    },
    canChangeStatus() {
      return this.detail && this.detail.estado !== "completada" && this.detail.estado !== "cancelada";
    },
    adminUser() {
      return useAuthStore().user || { id: 0, rol: "admin" };
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
    resetMotoForm() {
      this.form.moto_cliente_id = "";
      this.form.catalogoMarca = "";
      this.form.catalogoModelo = "";
      this.form.color = "";
      this.form.placa = "";
      this.form.anio = "";
    },
    async fetchOrders() {
      this.loading = true;
      try {
        const params = {};
        if (this.filterEstado) params.estado = this.filterEstado;
        const { data } = await api.get("/service-orders/", { params });
        this.orders = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar órdenes.", "error");
      } finally {
        this.loading = false;
      }
    },
    async fetchClients() {
      try {
        const { data } = await api.get("/users/clients/summary");
        this.clients = data;
      } catch (err) {
        console.error("Error loading clients", err);
      }
    },
    async fetchMechanics() {
      try {
        const { data } = await api.get("/users/mechanics");
        this.mechanics = data;
      } catch (err) {
        console.error("Error loading mechanics", err);
      }
    },
    async fetchCatalog() {
      try {
        const { data } = await api.get("/motorcycles/catalog");
        this.catalog = data;
      } catch (err) {
        console.error("Error loading catalog", err);
      }
    },
    async onClientChange() {
      this.resetMotoForm();
      this.clientMotos = [];
      if (!this.form.cliente_id) return;
      try {
        const { data } = await api.get(`/users/clients/${this.form.cliente_id}`);
        this.clientMotos = data.motos || [];
      } catch (err) {
        console.error("Error loading client motos", err);
      }
    },
    onMarcaChange() {
      this.form.catalogoModelo = "";
      this.form.color = "";
    },
    onModeloChange() {
      this.form.color = "";
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
    openCreateModal() {
      this.form = {
        cliente_id: "", moto_cliente_id: "", catalogoMarca: "", catalogoModelo: "",
        color: "", placa: "", anio: "", mecanico_id: "", descripcion: "",
      };
      this.clientMotos = [];
      this.motoMode = "existente";
      this.showCreateModal = true;
    },
    async handleCreate() {
      if (!window.confirm("¿Está seguro de crear esta orden de servicio?")) return;
      try {
        const payload = {
          descripcion: this.form.descripcion,
          cliente_id: Number(this.form.cliente_id),
          mecanico_id: Number(this.form.mecanico_id),
        };
        if (this.motoMode === "existente") {
          payload.moto_cliente_id = Number(this.form.moto_cliente_id);
        } else {
          const sel = this.modeloSeleccionado;
          payload.catalogo_moto_id = sel.id;
          payload.placa = this.form.placa.toUpperCase();
          payload.anio = Number(this.form.anio);
          payload.color = this.form.color;
        }
        await api.post("/service-orders/", payload);
        this.showCreateModal = false;
        this.showAlert("Orden de servicio creada correctamente.");
        await this.fetchOrders();
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al crear la orden.", "error");
      }
    },
    capitalize(s) {
      if (!s) return "";
      return s.replace(/\b\w/g, c => c.toUpperCase());
    },
    openDetailModal(order) {
      this.detail = { ...order };
      this.reassignMecanicoId = "";
      this.showDetailModal = true;
      api.get(`/service-orders/${order.id}`).then(({ data }) => {
        this.detail = data;
      }).catch(() => {});
    },
    async changeStatus(newStatus) {
      const msgs = {
        en_proceso: "¿Está seguro de iniciar esta orden?",
        completada: "¿Está seguro de marcar esta orden como completada?",
        cancelada: "¿Está seguro de cancelar esta orden?",
      };
      if (!window.confirm(msgs[newStatus] || "¿Está seguro de cambiar el estado?")) return;
      try {
        await api.patch(`/service-orders/${this.detail.id}/status`, { estado: newStatus });
        this.showAlert(`Orden actualizada a "${this.statusLabel(newStatus)}".`, newStatus === "cancelada" ? "error" : undefined);
        this.showDetailModal = false;
        await this.fetchOrders();
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cambiar estado.", "error");
      }
    },
    openChat(order) {
      this.chatOrdenId = order.id;
      this.showChatModal = true;
    },
    async handleReassign() {
      if (!window.confirm("¿Está seguro de reasignar el mecánico?")) return;
      try {
        await api.patch(`/service-orders/${this.detail.id}/mechanic`, {
          mecanico_id: Number(this.reassignMecanicoId),
        });
        this.showAlert("Mecánico reasignado correctamente.");
        this.showDetailModal = false;
        await this.fetchOrders();
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al reasignar mecánico.", "error");
      }
    },
  },
  mounted() {
    this.fetchOrders();
    this.fetchClients();
    this.fetchMechanics();
    this.fetchCatalog();
  },
};
</script>

<style scoped>
.admin-orders {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.orders-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.orders-header h1 {
  font-size: 1.8rem;
  color: #1a1a1a;
}
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}
.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-width: 200px;
  background: #fff;
}
.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
  font-size: 1rem;
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
.actions-cell {
  display: flex;
  gap: 6px;
}
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}
.badge-pendiente { background: #fef3c7; color: #92400e; }
.badge-en_proceso { background: #dbeafe; color: #1e40af; }
.badge-completada { background: #d1fae5; color: #065f46; }
.badge-cancelada { background: #fee2e2; color: #991b1b; }
.btn-sm {
  padding: 5px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}
.btn-view { background: #f1f5f9; color: #334155; }
.btn-view:hover { background: #e2e8f0; }
.btn-chat { background: #075e54; color: #fff; }
.btn-chat:hover { background: #054d44; }
.btn-start { background: #dbeafe; color: #1e40af; }
.btn-start:hover { background: #bfdbfe; }
.btn-complete { background: #d1fae5; color: #065f46; }
.btn-complete:hover { background: #a7f3d0; }
.btn-cancel-order { background: #fee2e2; color: #991b1b; }
.btn-cancel-order:hover { background: #fecaca; }
.btn-assign { background: #ede9fe; color: #5b21b6; }
.btn-assign:hover { background: #ddd6fe; }
.btn-primary {
  background: #ffaa00;
  color: #1a1a1a;
  padding: 9px 18px;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}
.btn-primary:hover { background: #e69900; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancel {
  background: #f1f5f9;
  color: #475569;
  padding: 9px 18px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}
.btn-cancel:hover { background: #e2e8f0; }
/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15,23,42,0.5);
  backdrop-filter: blur(6px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  max-height: 85vh;
  overflow-y: auto;
}
.modal-lg { max-width: 680px; }
.modal--pendiente { border-top: 4px solid #f59e0b; }
.modal--en_proceso { border-top: 4px solid #3b82f6; }
.modal-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  border-bottom: 1px solid #f1f5f9;
}
.topbar-left { display: flex; align-items: center; gap: 10px; }
.topbar-left .badge { font-size: 13px; padding: 6px 16px; border-radius: 20px; }
.topbar-id { font-size: 14px; font-weight: 700; color: #94a3b8; letter-spacing: 0.3px; }
.modal-close {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  font-size: 24px;
  font-weight: 400;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.modal-close:hover {
  background: #fee2e2;
  color: #dc2626;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  border-bottom: 1px solid #f1f5f9;
}
.modal-header h2 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.3px;
}
.modal-body { padding: 24px 28px 28px; }
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}
.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}
.detail-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #fff;
  color: #ffaa00;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.detail-label { display: block; font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 1px; }
.detail-value { font-size: 13px; font-weight: 600; color: #1a1a1a; display: flex; align-items: center; gap: 6px; }
.detail-card {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}
.detail-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.detail-card-body { margin: 0; font-size: 14px; color: #475569; line-height: 1.6; }
.detail-actions { margin-top: 0; }
.detail-actions + .detail-actions { margin-top: 20px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
.actions-title {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}
.actions-row { display: flex; gap: 10px; }
.actions-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}
.reassign-inline {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-left: auto;
}
.reassign-inline .form-control { width: auto; min-width: 180px; }
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
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
.form-control { padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 13px; flex: 1; background: #f8fafc; }
.form-control:focus { outline: none; border-color: #ffaa00; box-shadow: 0 0 0 3px rgba(255,170,0,0.1); background: #fff; }
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-weight: 600;
  font-size: 13px;
  color: #475569;
  margin-bottom: 5px;
}
.form-control {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-control:disabled {
  background: #f8fafc;
  color: #94a3b8;
}
textarea.form-control {
  resize: vertical;
  font-family: inherit;
}
/* Toggle */
.moto-toggle {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
}
.toggle-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: #f8fafc;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.toggle-btn.active {
  background: #ffaa00;
  color: #1a1a1a;
}
.toggle-btn:not(.active):hover {
  background: #e2e8f0;
}
/* New moto section */
.new-moto-section {
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 8px;
}
.form-row {
  display: flex;
  gap: 12px;
}
.form-row .half {
  flex: 1;
}
.color-display {
  display: flex;
  align-items: center;
  gap: 6px;
}
.color-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid #d1d5db;
}
.color-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
  animation: fadeIn 0.25s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}
.color-chip {
  padding: 5px 14px;
  border: 2px solid #d1d5db;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  color: #1a1a1a;
  text-shadow: 0 0 3px rgba(255,255,255,0.6);
}
.color-chip:hover {
  border-color: #ffaa00;
  transform: scale(1.08);
}
.color-selected {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes popIn {
  from { opacity: 0; transform: scale(0.7); }
  to { opacity: 1; transform: scale(1); }
}
.color-selected .color-chip {
  border-color: #1a1a1a;
  box-shadow: 0 0 0 2px #ffaa00;
  cursor: default;
  font-size: 14px;
  padding: 6px 18px;
}
.btn-recolor {
  background: none;
  border: 1px solid #94a3b8;
  border-radius: 16px;
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-recolor:hover {
  border-color: #ffaa00;
  color: #1a1a1a;
  background: #fff8e6;
}
/* Detail */
.status-badge-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
.status-badge-wrap .badge {
  font-size: 13px;
  padding: 6px 16px;
  border-radius: 20px;
}
.order-id-label {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.detail-field {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.detail-label {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}
.detail-field > span:last-child {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}
.detail-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;
}
.detail-section h3 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 10px;
}
.detail-section p {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
}
.status-actions {
  display: flex;
  gap: 10px;
}
.reassign-row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.reassign-row .form-control { max-width: 300px; }
.text-muted { color: #94a3b8; font-size: 13px; font-style: italic; }
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
