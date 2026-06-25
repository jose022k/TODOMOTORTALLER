<template>
  <div class="admin-users">
    <div class="users-header">
      <h1>Gestión de Usuarios</h1>
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
        <input v-model="mechSearch" type="text" class="search-input" placeholder="Buscar por nombre o email..." />
        <button class="btn-primary" @click="openCreateMechModal">+ Nuevo Mecánico</button>
      </div>

      <div v-if="loading" class="loading-state">Cargando...</div>
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
          <tr v-for="m in filteredMechanics" :key="m.id">
            <td>{{ m.nombre }}</td>
            <td>{{ m.email }}</td>
            <td>
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
    </div>

    <!-- Tab: Clientes -->
    <div v-if="activeTab === 'clients'" class="tab-content">
      <div class="toolbar">
        <input v-model="clientSearch" type="text" class="search-input" placeholder="Buscar por nombre, email o cédula..." />
      </div>

      <div v-if="loading" class="loading-state">Cargando...</div>
      <div v-else-if="filteredClients.length === 0" class="empty-state">No se encontraron clientes.</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Cédula</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in filteredClients" :key="c.id">
            <td>{{ c.cedula }}</td>
            <td>{{ c.nombre }}</td>
            <td>{{ c.email }}</td>
            <td>{{ c.telefono || '-' }}</td>
            <td>
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
      showCreateMech: false,
      showEditMech: false,
      mechForm: { nombre: "", email: "", password: "" },
      mechEditForm: { id: null, nombre: "", email: "" },
      // Clients
      clients: [],
      clientSearch: "",
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
  margin-bottom: 20px;
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
  font-size: 1.5rem;
  cursor: pointer;
  color: #94a3b8;
  padding: 0 4px;
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
</style>
