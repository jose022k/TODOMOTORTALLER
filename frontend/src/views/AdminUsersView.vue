<template>
  <div class="admin-users">
    <div class="users-header">
      <div class="header-content">
        <h1>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Gestión de Usuarios
        </h1>
        <p class="page-subtitle">Administra los clientes y mecánicos registrados</p>
      </div>
    </div>

    <!-- Alert -->
    <div v-if="alert.message" :class="['alert', 'alert-' + alert.type]">
      {{ alert.message }}
      <button class="alert-close" @click="alert.message = ''">×</button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button :class="['tab', { active: activeTab === 'mechanics' }]" @click="activeTab = 'mechanics'">Mecánicos</button>
      <button :class="['tab', { active: activeTab === 'clients' }]" @click="activeTab = 'clients'">Clientes</button>
    </div>

    <!-- Tab: Mecánicos -->
    <div v-if="activeTab === 'mechanics'" class="tab-content">
      <div class="toolbar">
        <input v-model="mechSearch" type="text" class="search-input" placeholder="Buscar por nombre o email..." @input="onMechSearchInput" />
        <button class="btn-primary" @click="openCreateMechModal">+ Nuevo Mecánico</button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando mecánicos...</p>
      </div>
      <div v-else-if="filteredMechanics.length === 0" class="empty-state">No se encontraron mecánicos.</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in paginatedMechanics" :key="m.id">
            <td data-label="Nombre">{{ m.nombre }}</td>
            <td data-label="Email">{{ m.email }}</td>
            <td data-label="Estado">
              <span :class="['badge', m.activo ? 'badge-active' : 'badge-inactive']">
                {{ m.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="actions-cell">
              <button class="btn-sm btn-edit" @click="openEditMechModal(m)">Editar</button>
              <button :class="['btn-sm', m.activo ? 'btn-deactivate' : 'btn-activate']" @click="toggleMechActive(m)">
                {{ m.activo ? 'Desactivar' : 'Activar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="mechTotalPages > 1" class="pagination">
        <button class="page-btn" :disabled="mechPage <= 1" @click="goToMechPage(mechPage - 1)">&#9664;</button>
        <span class="page-info">{{ mechPage }} / {{ mechTotalPages }}</span>
        <button class="page-btn" :disabled="mechPage >= mechTotalPages" @click="goToMechPage(mechPage + 1)">&#9654;</button>
      </div>
    </div>

    <!-- Tab: Clientes -->
    <div v-if="activeTab === 'clients'" class="tab-content">
      <div class="toolbar">
        <input v-model="clientSearch" type="text" class="search-input" placeholder="Buscar por nombre, email o cédula..." @input="onClientSearchInput" />
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando clientes...</p>
      </div>
      <div v-else-if="filteredClients.length === 0" class="empty-state">No se encontraron clientes.</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Cédula</th>
            <th>Nombre y apellido</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in paginatedClients" :key="c.id">
            <td data-label="Cédula">{{ c.cedula }}</td>
            <td data-label="Nombre">{{ c.nombre }}</td>
            <td data-label="Email">{{ c.email }}</td>
            <td data-label="Teléfono">{{ c.telefono || '-' }}</td>
            <td data-label="Estado">
              <span :class="['badge', c.activo ? 'badge-active' : 'badge-inactive']">
                {{ c.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="actions-cell">
              <button class="btn-sm btn-view" @click="openDetailClientModal(c)">Ver</button>
              <button class="btn-sm btn-edit" @click="openEditClientModal(c)">Editar</button>
              <button :class="['btn-sm', c.activo ? 'btn-deactivate' : 'btn-activate']" @click="toggleClientActive(c)">
                {{ c.activo ? 'Desactivar' : 'Activar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="clientTotalPages > 1" class="pagination">
        <button class="page-btn" :disabled="clientPage <= 1" @click="goToClientPage(clientPage - 1)">&#9664;</button>
        <span class="page-info">{{ clientPage }} / {{ clientTotalPages }}</span>
        <button class="page-btn" :disabled="clientPage >= clientTotalPages" @click="goToClientPage(clientPage + 1)">&#9654;</button>
      </div>
    </div>

    <!-- Modal Nuevo Mecánico -->
    <div v-if="showCreateMech" class="modal-backdrop" @click.self="showCreateMech = false">
      <div class="modal-card">
        <div class="modal-header">
          <h2>Nuevo Mecánico</h2>
          <button class="btn-close" @click="showCreateMech = false">×</button>
        </div>
        <form @submit.prevent="createMechanic">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="mechForm.nombre" type="text" required placeholder="Nombre completo" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="mechForm.email" type="email" required placeholder="correo@ejemplo.com" />
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input v-model="mechForm.password" type="password" required placeholder="Contraseña" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="showCreateMech = false">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Guardando...' : 'Crear Mecánico' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Editar Mecánico -->
    <div v-if="showEditMech" class="modal-backdrop" @click.self="showEditMech = false">
      <div class="modal-card">
        <div class="modal-header">
          <h2>Editar Mecánico</h2>
          <button class="btn-close" @click="showEditMech = false">×</button>
        </div>
        <form @submit.prevent="editMechanic">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="mechEditForm.nombre" type="text" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="mechEditForm.email" type="email" required />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="showEditMech = false">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Editar Cliente -->
    <div v-if="showEditClient" class="modal-backdrop" @click.self="showEditClient = false">
      <div class="modal-card">
        <div class="modal-header">
          <h2>Editar Cliente</h2>
          <button class="btn-close" @click="showEditClient = false">×</button>
        </div>
        <form @submit.prevent="editClient">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="clientEditForm.nombre" type="text" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="clientEditForm.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Teléfono</label>
            <input v-model="clientEditForm.telefono" type="text" />
          </div>
          <div class="form-group">
            <label>Dirección</label>
            <input v-model="clientEditForm.direccion" type="text" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="showEditClient = false">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Detalle Cliente -->
    <div v-if="showDetailClient" class="modal-backdrop" @click.self="showDetailClient = false">
      <div class="modal-card modal-card-wide">
        <div class="modal-header">
          <h2>Detalle del Cliente</h2>
          <button class="btn-close" @click="showDetailClient = false">×</button>
        </div>
        <div v-if="clientDetail" class="client-detail">
          <div class="detail-grid">
            <div><strong>Cédula:</strong> {{ clientDetail.cedula }}</div>
            <div><strong>Nombre:</strong> {{ clientDetail.nombre }}</div>
            <div><strong>Email:</strong> {{ clientDetail.email }}</div>
            <div><strong>Teléfono:</strong> {{ clientDetail.telefono }}</div>
            <div><strong>Dirección:</strong> {{ clientDetail.direccion }}</div>
            <div>
              <strong>Estado:</strong>
              <span :class="['badge', clientDetail.activo ? 'badge-active' : 'badge-inactive']">
                {{ clientDetail.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
          </div>
          <h3 class="motos-title">Motos Asociadas</h3>
          <div v-if="clientDetail.motos && clientDetail.motos.length > 0">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Marca</th>
                  <th>Modelo</th>
                  <th>Año</th>
                  <th>Color</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="moto in clientDetail.motos" :key="moto.id">
                  <td>{{ moto.placa }}</td>
                  <td>{{ moto.marca }}</td>
                  <td>{{ moto.modelo }}</td>
                  <td>{{ moto.anio }}</td>
                  <td>
                    <span class="color-dot" :style="{ backgroundColor: getColorHex(moto.color) }"></span>
                    {{ moto.color }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-state">Este cliente no tiene motos registradas.</div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-secondary" @click="showDetailClient = false">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "AdminUsersView",
  data() {
    return {
      activeTab: "mechanics",
      loading: false,
      saving: false,
      alert: { message: "", type: "" },
      // Mechanics
      mechanics: [],
      mechSearch: "",
      mechPage: 1,
      mechPageSize: 15,
      mechSearchTimer: null,
      showCreateMech: false,
      showEditMech: false,
      mechForm: { nombre: "", email: "", password: "" },
      mechEditForm: { id: null, nombre: "", email: "" },
      // Clients
      clients: [],
      clientSearch: "",
      clientPage: 1,
      clientPageSize: 15,
      clientSearchTimer: null,
      showEditClient: false,
      showDetailClient: false,
      clientEditForm: { id: null, nombre: "", email: "", telefono: "", direccion: "" },
      clientDetail: null,
    };
  },
  computed: {
    filteredMechanics() {
      const q = this.mechSearch.toLowerCase().trim();
      if (!q) return this.mechanics;
      return this.mechanics.filter(
        (m) => m.nombre?.toLowerCase().includes(q) || m.email?.toLowerCase().includes(q)
      );
    },
    mechTotalPages() {
      return Math.ceil(this.filteredMechanics.length / this.mechPageSize) || 1;
    },
    filteredClients() {
      const q = this.clientSearch.toLowerCase().trim();
      if (!q) return this.clients;
      return this.clients.filter(
        (c) =>
          c.nombre?.toLowerCase().includes(q) ||
          c.email?.toLowerCase().includes(q) ||
          c.cedula?.toLowerCase().includes(q)
      );
    },
    clientTotalPages() {
      return Math.ceil(this.filteredClients.length / this.clientPageSize) || 1;
    },
    paginatedMechanics() {
      const start = (this.mechPage - 1) * this.mechPageSize;
      return this.filteredMechanics.slice(start, start + this.mechPageSize);
    },
    paginatedClients() {
      const start = (this.clientPage - 1) * this.clientPageSize;
      return this.filteredClients.slice(start, start + this.clientPageSize);
    },
  },
  mounted() {
    this.fetchMechanics();
    this.fetchClients();
  },
  methods: {
    showAlert(msg, type = "success") {
      this.alert = { message: msg, type };
      setTimeout(() => (this.alert.message = ""), 5000);
    },
    // --- Mechanics ---
    async fetchMechanics() {
      this.loading = true;
      try {
        const { data } = await api.get("/users/mechanics", { params: { skip: 0, limit: 200 } });
        this.mechanics = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar mecánicos.", "error");
      } finally {
        this.loading = false;
      }
    },
    async goToMechPage(p) {
      this.mechPage = p;
    },
    onMechSearchInput() {
      if (this.mechSearchTimer) clearTimeout(this.mechSearchTimer);
      this.mechSearchTimer = setTimeout(() => {
        this.mechPage = 1;
      }, 300);
    },
    openCreateMechModal() {
      this.mechForm = { nombre: "", email: "", password: "" };
      this.showCreateMech = true;
    },
    async createMechanic() {
      this.saving = true;
      try {
        const { data } = await api.post("/users/mechanics", this.mechForm);
        this.mechanics.push(data);
        this.showCreateMech = false;
        this.showAlert(`Mecánico "${data.nombre}" creado exitosamente.`);
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al crear mecánico.", "error");
      } finally {
        this.saving = false;
      }
    },
    openEditMechModal(m) {
      this.mechEditForm = { id: m.id, nombre: m.nombre, email: m.email };
      this.showEditMech = true;
    },
    async editMechanic() {
      this.saving = true;
      try {
        const payload = {};
        if (this.mechEditForm.nombre) payload.nombre = this.mechEditForm.nombre;
        if (this.mechEditForm.email) payload.email = this.mechEditForm.email;
        const { data } = await api.patch(`/users/mechanics/${this.mechEditForm.id}`, payload);
        const idx = this.mechanics.findIndex((m) => m.id === data.id);
        if (idx !== -1) this.mechanics.splice(idx, 1, data);
        this.showEditMech = false;
        this.showAlert("Mecánico actualizado correctamente.");
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al actualizar mecánico.", "error");
      } finally {
        this.saving = false;
      }
    },
    async toggleMechActive(m) {
      try {
        const { data } = await api.patch(`/users/mechanics/${m.id}/deactivate`);
        const idx = this.mechanics.findIndex((x) => x.id === data.id);
        if (idx !== -1) this.mechanics.splice(idx, 1, data);
        const tipo = data.activo ? "success" : "error";
        this.showAlert(`Mecánico ${data.activo ? "activado" : "desactivado"} correctamente.`, tipo);
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cambiar estado.", "error");
      }
    },
    // --- Clients ---
    async fetchClients() {
      this.loading = true;
      try {
        const { data } = await api.get("/users/clients", { params: { skip: 0, limit: 200 } });
        this.clients = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar clientes.", "error");
      } finally {
        this.loading = false;
      }
    },
    async goToClientPage(p) {
      this.clientPage = p;
    },
    onClientSearchInput() {
      if (this.clientSearchTimer) clearTimeout(this.clientSearchTimer);
      this.clientSearchTimer = setTimeout(() => {
        this.clientPage = 1;
      }, 300);
    },
    openEditClientModal(c) {
      this.clientEditForm = {
        id: c.id,
        nombre: c.nombre,
        email: c.email,
        telefono: c.telefono || "",
        direccion: c.direccion || "",
      };
      this.showEditClient = true;
    },
    async editClient() {
      this.saving = true;
      try {
        const payload = {};
        if (this.clientEditForm.nombre) payload.nombre = this.clientEditForm.nombre;
        if (this.clientEditForm.email) payload.email = this.clientEditForm.email;
        if (this.clientEditForm.telefono) payload.telefono = this.clientEditForm.telefono;
        if (this.clientEditForm.direccion) payload.direccion = this.clientEditForm.direccion;
        const { data } = await api.patch(`/users/clients/${this.clientEditForm.id}`, payload);
        const idx = this.clients.findIndex((c) => c.id === data.id);
        if (idx !== -1) this.clients.splice(idx, 1, data);
        this.showEditClient = false;
        this.showAlert("Cliente actualizado correctamente.");
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al actualizar cliente.", "error");
      } finally {
        this.saving = false;
      }
    },
    async toggleClientActive(c) {
      try {
        const { data } = await api.patch(`/users/clients/${c.id}/deactivate`);
        const idx = this.clients.findIndex((x) => x.id === data.id);
        if (idx !== -1) this.clients.splice(idx, 1, data);
        const tipo = data.activo ? "success" : "error";
        this.showAlert(`Cliente ${data.activo ? "activado" : "desactivado"} correctamente.`, tipo);
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cambiar estado.", "error");
      }
    },
    getColorHex(colorName) {
      const map = {
        'Negro': '#000000', 'Blanco': '#FFFFFF', 'Gris': '#808080',
        'Rojo': '#DC2626', 'Azul': '#2563EB', 'Verde': '#16A34A',
        'Amarillo': '#EAB308', 'Naranja': '#EA580C', 'Morado': '#7C3AED',
        'Rosa': '#EC4899', 'Vinotinto': '#7F1D1D', 'Marrón': '#8B4513',
        'Plateado': '#C0C0C0', 'Dorado': '#D4AF37', 'Beige': '#F5F5DC',
        'Café': '#6B4226', 'Crema': '#FFFDD0',
      };
      return map[colorName] || '#CBD5E1';
    },
    openDetailClientModal(c) {
      this.clientDetail = c;
      this.showDetailClient = true;
    },
  },
  beforeUnmount() {
    if (this.mechSearchTimer) clearTimeout(this.mechSearchTimer);
    if (this.clientSearchTimer) clearTimeout(this.clientSearchTimer);
  },
};
</script>

<style scoped>
.admin-users {
  max-width: 1100px;
  margin: 0 auto;
  padding: 30px 20px;
}
.users-header h1 {
  font-size: 1.8rem;
  color: #1a1a1a;
  font-weight: 800;
}
.page-subtitle {
  color: #666;
  margin-top: 5px;
  margin-left: 48px;
  font-size: 1.05rem;
}
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
.alert-close {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  color: inherit;
  padding: 0 4px;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 20px;
}
.tab {
  padding: 12px 28px;
  font-size: 0.95rem;
  font-weight: 700;
  border: none;
  background: none;
  cursor: pointer;
  color: #64748b;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}
.tab.active {
  color: #1a1a1a;
  border-bottom-color: #ffaa00;
}
.tab:hover {
  color: #1a1a1a;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}
.search-input {
  flex: 1;
  max-width: 360px;
  padding: 10px 14px;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
}
.search-input:focus {
  border-color: #ffaa00;
  outline: none;
  box-shadow: 0 0 0 3px rgba(255,170,0,0.15);
}

/* Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.data-table th {
  background: #f8fafc;
  text-align: left;
  padding: 12px 16px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}
.data-table td {
  padding: 12px 16px;
  font-size: 0.9rem;
  border-bottom: 1px solid #f1f5f9;
}
.data-table tr:hover td {
  background: #f8fafc;
}

/* Badge */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 0.78rem;
  font-weight: 700;
}
.badge-active {
  background: #dcfce7;
  color: #166534;
}
.badge-inactive {
  background: #f1f5f9;
  color: #64748b;
}

/* Buttons */
.btn-sm {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-sm + .btn-sm {
  margin-left: 6px;
}
.btn-view {
  background: #eff6ff;
  color: #2563eb;
}
.btn-view:hover {
  background: #dbeafe;
}
.btn-edit {
  background: #fffbeb;
  color: #b45309;
}
.btn-edit:hover {
  background: #fef3c7;
}
.btn-deactivate {
  background: #fef2f2;
  color: #dc2626;
}
.btn-deactivate:hover {
  background: #fee2e2;
}
.btn-activate {
  background: #dcfce7;
  color: #16a34a;
}
.btn-activate:hover {
  background: #bbf7d0;
}

.actions-cell {
  white-space: nowrap;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(15,23,42,0.4);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-card {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 460px;
  padding: 28px;
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
}
.modal-card-wide {
  max-width: 640px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.modal-header h2 {
  font-size: 1.3rem;
}
.btn-close {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  font-size: 1.5rem;
  cursor: pointer;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.btn-close:hover {
  background: #fee2e2;
  color: #dc2626;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 700;
  color: #475569;
  margin-bottom: 6px;
}
.form-group input {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  box-sizing: border-box;
}
.form-group input:focus {
  border-color: #ffaa00;
  outline: none;
  box-shadow: 0 0 0 3px rgba(255,170,0,0.15);
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
.btn-primary {
  padding: 10px 20px;
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255,170,0,0.3);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
.btn-secondary {
  padding: 10px 20px;
  background: #f1f5f9;
  color: #475569;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.btn-secondary:hover {
  background: #e2e8f0;
}

/* Detail */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}
.detail-grid div {
  font-size: 0.9rem;
}
.color-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid #cbd5e1;
  margin-right: 6px;
  vertical-align: middle;
}
.motos-title {
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #1a1a1a;
}
.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
  font-size: 0.95rem;
}

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
  .admin-users {
    padding: 12px 12px 80px;
  }
  .users-header h1 {
    font-size: 1.3rem;
  }
  .page-subtitle {
    margin-left: 0;
    font-size: 0.9rem;
  }
  .tabs {
    border-radius: 10px;
    overflow: hidden;
    background: #f1f5f9;
    border-bottom: none;
    padding: 3px;
    gap: 0;
  }
  .tab {
    flex: 1;
    padding: 12px 16px;
    font-size: 14px;
    border-bottom: none;
    margin-bottom: 0;
    border-radius: 8px;
    text-align: center;
  }
  .tab.active {
    background: #fff;
    color: #1a1a1a;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
  .toolbar {
    flex-direction: column;
    gap: 10px;
  }
  .search-input {
    max-width: 100%;
    width: 100%;
    padding: 14px;
    border-radius: 12px;
    font-size: 15px;
  }
  .btn-primary {
    width: 100%;
    padding: 14px;
    border-radius: 12px;
    font-size: 15px;
    text-align: center;
    justify-content: center;
  }
  .data-table {
    display: block;
    overflow-x: hidden;
    background: transparent;
    box-shadow: none;
  }
  .data-table thead { display: none; }
  .data-table tbody { display: flex; flex-direction: column; gap: 10px; }
  .data-table tr {
    display: flex;
    flex-direction: column;
    background: #fff;
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid #f1f5f9;
    gap: 6px;
  }
  .data-table td {
    padding: 2px 0;
    border-bottom: none;
    font-size: 13px;
  }
  .data-table td::before {
    content: attr(data-label);
    font-weight: 700;
    color: #94a3b8;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    display: block;
    margin-bottom: 2px;
  }
  .data-table td:last-child {
    padding-top: 8px;
    border-top: 1px solid #f1f5f9;
  }
  .actions-cell {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .btn-sm {
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
  }
  .modal-card {
    width: 95%;
    padding: 20px;
    border-radius: 16px;
  }
  .modal-header h2 {
    font-size: 1.2rem;
  }
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .pagination {
    padding: 8px 0 20px;
  }
}
html.dark .data-table tr {
  background: #1a1f2e;
  border-color: #1e293b;
}
html.dark .modal-card {
  background: #1a1f2e;
}
html.dark .users-header h1 {
  color: #e2e8f0;
}
html.dark .page-subtitle {
  color: #94a3b8;
}
html.dark .tabs {
  background: #1e293b;
}
html.dark .tab {
  color: #94a3b8;
}
html.dark .tab.active {
  background: #0d1117;
  color: #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
html.dark .tab:hover {
  color: #e2e8f0;
}
html.dark .search-input {
  background: #0d1117;
  border-color: #334155;
  color: #e2e8f0;
}
html.dark .data-table {
  background: transparent;
}
html.dark .data-table th {
  background: #1e293b;
  color: #94a3b8;
  border-bottom-color: #334155;
}
html.dark .data-table td {
  color: #cbd5e1;
  border-bottom-color: #1e293b;
}
html.dark .data-table td::before {
  color: #64748b;
}
html.dark .data-table td:last-child {
  border-top-color: #1e293b;
}
html.dark .btn-view {
  background: #1e3a5f;
  color: #60a5fa;
}
html.dark .btn-edit {
  background: #422006;
  color: #fbbf24;
}
html.dark .btn-deactivate {
  background: #450a0a;
  color: #f87171;
}
html.dark .btn-activate {
  background: #052e16;
  color: #4ade80;
}
html.dark .badge-active {
  background: #052e16;
  color: #4ade80;
}
html.dark .badge-inactive {
  background: #1e293b;
  color: #94a3b8;
}
html.dark .form-group label {
  color: #94a3b8;
}
html.dark .form-group input {
  background: #0d1117;
  border-color: #334155;
  color: #e2e8f0;
}
html.dark .btn-secondary {
  background: #1e293b;
  color: #94a3b8;
}
html.dark .btn-secondary:hover {
  background: #334155;
}
html.dark .page-btn {
  background: #0d1117;
  border-color: #334155;
  color: #94a3b8;
}
html.dark .page-info {
  color: #94a3b8;
}
html.dark .motos-title {
  color: #e2e8f0;
}
html.dark .detail-grid div {
  color: #cbd5e1;
}
html.dark .detail-grid strong {
  color: #94a3b8;
}
html.dark .empty-state,
html.dark .loading-state {
  color: #64748b;
}
html.dark .alert-success {
  background: #052e16;
  color: #4ade80;
  border-color: #166534;
}
html.dark .alert-error {
  background: #450a0a;
  color: #f87171;
  border-color: #991b1b;
}
</style>
