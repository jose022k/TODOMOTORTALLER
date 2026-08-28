<template>
  <div class="admin-orders">
    <div class="orders-header">
      <div class="header-content">
        <h1>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M9 14l2 2 4-4"/></svg>
          Órdenes de Servicio
        </h1>
        <p class="page-subtitle">Gestiona las órdenes de servicio de los clientes</p>
      </div>
    </div>

    <!-- Alerta -->
    <div v-if="alert.message" :class="['alert', 'alert-' + alert.type]">
      {{ alert.message }}
      <button class="alert-close" @click="alert.message = ''">×</button>
    </div>

    <!-- Barra de herramientas -->
    <div class="toolbar">
      <div class="toolbar-search">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Buscar por cliente o ID..."
          @input="onSearch"
        />
        <button v-if="searchQuery" class="search-clear" @click="clearSearch" title="Limpiar búsqueda">×</button>
      </div>
      <button class="clear-filters-btn" @click="clearFilters" title="Limpiar filtros">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
        <span>Limpiar</span>
      </button>
      <button class="filters-toggle" @click="showFilters = !showFilters" :aria-expanded="showFilters">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
        <span>Filtros</span>
      </button>
      <div class="filters-group" :class="{ 'filters-open': showFilters }">
        <select v-model="filterEstado" class="filter-select" @change="onFilterChange">
          <option value="">Todos los estados</option>
          <option value="pendiente">Pendiente</option>
          <option value="en_proceso">En Proceso</option>
          <option value="completada">Completada</option>
          <option value="cancelada">Cancelada</option>
        </select>
        <select v-model="filterClienteId" class="filter-select" @change="onFilterChange">
          <option value="">Todos los clientes</option>
          <option v-for="c in clients" :key="c.id" :value="c.id">{{ capitalize(c.nombre) }}</option>
        </select>
        <select v-model="filterMecanicoId" class="filter-select" @change="onFilterChange">
          <option value="">Todos los mecánicos</option>
          <option v-for="m in mechanics" :key="m.id" :value="m.id">{{ capitalize(m.nombre) }}</option>
        </select>
      </div>
      <button class="btn-primary" @click="openCreateModal">+ Nueva Orden</button>
    </div>

    <!-- Tabla de órdenes -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando órdenes...</p>
    </div>
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
          <td data-label="ID">{{ o.id }}</td>
          <td data-label="Cliente">{{ capitalize(o.cliente_nombre) }}</td>
          <td data-label="Moto">{{ o.moto_marca }} {{ o.moto_modelo }} ({{ o.moto_placa }})</td>
          <td data-label="Mecánico">{{ capitalize(o.mecanico_nombre) }}</td>
          <td data-label="Estado"><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></td>
          <td data-label="Fecha">{{ formatDate(o.fecha_creacion) }}</td>
          <td class="actions-cell">
            <button class="btn-sm btn-view" @click="openDetailModal(o)">Ver detalles</button>
            <button v-if="o.estado === 'en_proceso'" class="btn-sm btn-chat" @click="openChat(o)">Chat</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Mobile cards: ALWAYS in DOM, shown only on mobile via global CSS -->
    <div class="admin-mobile-cards">
      <div v-for="o in orders" :key="'m-' + o.id" class="admin-mobile-card">
        <div class="admin-mobile-row"><span class="admin-mobile-lbl">ID:</span> <span class="admin-mobile-val">{{ o.id }}</span></div>
        <div class="admin-mobile-row"><span class="admin-mobile-lbl">Cliente:</span> <span class="admin-mobile-val">{{ capitalize(o.cliente_nombre) }}</span></div>
        <div class="admin-mobile-row"><span class="admin-mobile-lbl">Moto:</span> <span class="admin-mobile-val">{{ o.moto_marca }} {{ o.moto_modelo }} ({{ o.moto_placa }})</span></div>
        <div class="admin-mobile-row"><span class="admin-mobile-lbl">Mecánico:</span> <span class="admin-mobile-val">{{ capitalize(o.mecanico_nombre) }}</span></div>
        <div class="admin-mobile-row"><span class="admin-mobile-lbl">Estado:</span> <span class="admin-mobile-val"><span :class="['badge', 'badge-' + o.estado]">{{ statusLabel(o.estado) }}</span></span></div>
        <div class="admin-mobile-row"><span class="admin-mobile-lbl">Fecha:</span> <span class="admin-mobile-val">{{ formatDate(o.fecha_creacion) }}</span></div>
        <div class="admin-mobile-row admin-mobile-actions">
          <button class="btn-sm btn-view" @click="openDetailModal(o)">Ver detalles</button>
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
            <div v-if="!form.cliente_id" class="client-search">
              <input
                v-model="clienteBusqueda"
                type="text"
                class="form-control"
                placeholder="Buscar cliente por nombre o cédula..."
                @focus="clienteDropdownOpen = true"
                @blur="closeClienteDropdown"
              />
              <div v-if="clienteDropdownOpen" class="client-search-dropdown">
                <div v-if="clientsFiltrados.length === 0" class="client-search-empty">No se encontraron clientes.</div>
                <button
                  v-for="c in clientsFiltrados"
                  :key="c.id"
                  type="button"
                  class="client-search-item"
                  @mousedown.prevent="selectCliente(c)"
                >
                  <span class="client-search-name">{{ c.nombre }}</span>
                  <span class="client-search-cedula">C.I. {{ c.cedula }}</span>
                </button>
              </div>
            </div>
            <div v-else class="client-selected">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <span class="client-selected-name">{{ selectedCliente.nombre }}</span>
              <span class="client-selected-cedula">C.I. {{ selectedCliente.cedula }}</span>
              <button type="button" class="client-selected-clear" @click="clearCliente" title="Cambiar cliente">×</button>
            </div>
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
              <select v-model="form.catalogoModelo" @change="onModeloChange" class="form-control">
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
                <input v-model="form.placa" type="text" class="form-control" placeholder="ABC-123" maxlength="7" @input="filterPlaca" />
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

          <div class="form-group">
            <label>Monto</label>
            <div class="monto-toggle">
              <button :class="['toggle-btn', { active: form.moneda === 'BS' }]" type="button" @click="form.moneda = 'BS'">Bs</button>
              <button :class="['toggle-btn', { active: form.moneda === 'USD' }]" type="button" @click="form.moneda = 'USD'">$</button>
            </div>
            <div class="monto-input-row">
              <input
                v-model="form.monto"
                type="number"
                step="0.01"
                min="0"
                class="form-control"
                :placeholder="form.moneda === 'BS' ? 'Ej: 5000' : 'Ej: 50'"
                @input="filterMonto"
              />
              <span class="monto-currency">{{ form.moneda === 'BS' ? 'Bs' : '$' }}</span>
            </div>
            <p v-if="form.moneda === 'BS' && montoUsdPreview" class="monto-preview">
              ≈ ${{ montoUsdPreview }}
            </p>
            <p v-else-if="form.moneda === 'USD' && tasaBcv && form.monto > 0" class="monto-preview">
              ≈ {{ formatBs(form.monto * tasaBcv) }} Bs
            </p>
            <p v-if="tasaBcv" class="monto-tasa">Tasa BCV: {{ tasaBcv.toFixed(2) }} Bs/$</p>
            <p v-else class="monto-tasa warn">Tasa no disponible. Configúrala en Reportes y Estadísticas.</p>
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
            <div class="detail-item" v-if="detail.monto">
              <div class="detail-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
              </div>
              <div>
                <span class="detail-label">Monto</span>
                <span class="detail-value">
                  <span class="monto-original">{{ detail.moneda === 'USD' ? '$' : 'Bs' }} {{ detail.moneda === 'USD' ? detail.monto : formatBs(detail.monto) }}</span>
                  <span v-if="detail.monto_usd" class="detail-sub">≈ ${{ Number(detail.monto_usd).toFixed(2) }}</span>
                </span>
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
                <span class="reassign-label">Reasignar mecánico</span>
                <div class="reassign-controls">
                  <select v-model="reassignMecanicoId" class="form-control">
                    <option value="">Seleccionar mecánico...</option>
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
import orderSocket from "@/services/orderSocket";

export default {
  name: "AdminServiceOrders",
  components: { ChatModal },
  data() {
    return {
      alert: { message: "", type: "success" },
      loading: false,
      orders: [],
      filterEstado: "",
      filterClienteId: "",
      filterMecanicoId: "",
      searchQuery: "",
      showFilters: false,
      showCreateModal: false,
      showDetailModal: false,
      clients: [],
      mechanics: [],
      clienteBusqueda: "",
      clienteDropdownOpen: false,
      tasaBcv: null,
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
      page: 1,
      pageSize: 15,
      totalItems: 0,
      totalPages: 0,
      pollTimer: null,
    };
  },
  computed: {
    clientsFiltrados() {
      const q = this.clienteBusqueda.trim().toLowerCase();
      if (!q) return this.clients;
      return this.clients.filter((c) =>
        (c.nombre || "").toLowerCase().includes(q) ||
        String(c.cedula || "").toLowerCase().includes(q)
      );
    },
    selectedCliente() {
      return this.clients.find((c) => c.id === this.form.cliente_id) || null;
    },
    montoUsdPreview() {
      if (this.form.moneda !== 'BS' || !this.tasaBcv || !(this.form.monto > 0)) return "";
      return (this.form.monto / this.tasaBcv).toFixed(2);
    },
    marcas() {
      const set = new Set(this.catalog.map((m) => m.marca));
      return [...set].sort();
    },
    modelosFiltrados() {
      const seen = new Set();
      return this.catalog.filter((m) => {
        if (this.form.catalogoMarca && m.marca !== this.form.catalogoMarca) return false;
        if (seen.has(m.modelo)) return false;
        seen.add(m.modelo);
        return true;
      });
    },
    coloresPorModelo() {
      if (!this.form.catalogoModelo) return [];
      const colores = new Set();
      this.catalog
        .filter((m) => {
          if (this.form.catalogoMarca && m.marca !== this.form.catalogoMarca) return false;
          return m.modelo === this.form.catalogoModelo;
        })
        .forEach((m) => {
          (m.gama_color || "").split(",").map((c) => c.trim()).filter(Boolean).forEach((c) => colores.add(c));
        });
      return [...colores];
    },
    modeloSeleccionado() {
      return this.catalog.find((m) => {
        if (this.form.catalogoMarca && m.marca !== this.form.catalogoMarca) return false;
        return m.modelo === this.form.catalogoModelo;
      });
    },
    coloresDisponibles() {
      return this.coloresPorModelo;
    },
    canCreate() {
      if (!this.form.cliente_id || !this.form.mecanico_id || !this.form.descripcion.trim()) return false;
      if (!(this.form.monto > 0) || !this.form.moneda) return false;
      if (this.motoMode === "existente") return !!this.form.moto_cliente_id;
      return !!(this.form.catalogoModelo && this.modeloSeleccionado && this.form.color && this.form.placa && this.form.anio);
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
        const params = { skip: (this.page - 1) * this.pageSize, limit: this.pageSize };
        if (this.filterEstado) params.estado = this.filterEstado;
        if (this.filterClienteId) params.cliente_id = this.filterClienteId;
        if (this.filterMecanicoId) params.mecanico_id = this.filterMecanicoId;
        if (this.searchQuery && this.searchQuery.trim()) params.q = this.searchQuery.trim();
        const { data } = await api.get("/service-orders/", { params });
        this.orders = data;
      } catch (err) {
        this.showAlert(err.response?.data?.detail || "Error al cargar órdenes.", "error");
      } finally {
        this.loading = false;
      }
    },
    async fetchCount() {
      try {
        const params = {};
        if (this.filterEstado) params.estado = this.filterEstado;
        if (this.filterClienteId) params.cliente_id = this.filterClienteId;
        if (this.filterMecanicoId) params.mecanico_id = this.filterMecanicoId;
        if (this.searchQuery && this.searchQuery.trim()) params.q = this.searchQuery.trim();
        const { data } = await api.get("/service-orders/count", { params });
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
    filterPlaca() {
      this.form.placa = this.form.placa.replace(/[^a-zA-Z0-9]/g, "").toUpperCase().slice(0, 7);
    },
    onFilterChange() {
      this.page = 1;
      this.fetchOrders();
      this.fetchCount();
    },
    onSearch() {
      this.page = 1;
      if (this._searchTimer) clearTimeout(this._searchTimer);
      this._searchTimer = setTimeout(() => {
        this.fetchOrders();
        this.fetchCount();
      }, 300);
    },
    clearSearch() {
      this.searchQuery = "";
      this.page = 1;
      this.fetchOrders();
      this.fetchCount();
    },
    clearFilters() {
      this.filterEstado = "";
      this.filterClienteId = "";
      this.filterMecanicoId = "";
      this.searchQuery = "";
      this.page = 1;
      this.fetchOrders();
      this.fetchCount();
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
        const { data } = await api.get("/motorcycles/catalog", { params: { limit: 9999 } });
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
    selectCliente(c) {
      this.form.cliente_id = c.id;
      this.clienteBusqueda = "";
      this.clienteDropdownOpen = false;
      this.onClientChange();
    },
    clearCliente() {
      this.form.cliente_id = "";
      this.clienteBusqueda = "";
      this.clienteDropdownOpen = false;
      this.clientMotos = [];
      this.motoMode = "existente";
      this.resetMotoForm();
    },
    closeClienteDropdown() {
      setTimeout(() => { this.clienteDropdownOpen = false; }, 150);
    },
    async fetchTasa() {
      try {
        const { data } = await api.get("/bcv/tasa");
        this.tasaBcv = data.tasa;
      } catch (err) {
        this.tasaBcv = null;
      }
    },
    filterMonto() {
      const val = parseFloat(this.form.monto);
      this.form.monto = isNaN(val) || val < 0 ? "" : val;
    },
    formatBs(val) {
      return Number(val).toLocaleString("es-VE", { maximumFractionDigits: 2 });
    },
    onMarcaChange() {
      this.form.catalogoModelo = "";
      this.form.color = "";
    },
    onModeloChange() {
      this.form.color = "";
      if (!this.form.catalogoMarca) {
        const match = this.catalog.find((m) => m.modelo === this.form.catalogoModelo);
        if (match) this.form.catalogoMarca = match.marca;
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
    openCreateModal() {
      this.form = {
        cliente_id: "", moto_cliente_id: "", catalogoMarca: "", catalogoModelo: "",
        color: "", placa: "", anio: "", mecanico_id: "", descripcion: "",
        monto: "", moneda: "USD",
      };
      this.clientMotos = [];
      this.motoMode = "existente";
      this.fetchTasa();
      this.showCreateModal = true;
    },
    async handleCreate() {
      if (!window.confirm("¿Está seguro de crear esta orden de servicio?")) return;
      try {
        const payload = {
          descripcion: this.form.descripcion,
          cliente_id: Number(this.form.cliente_id),
          mecanico_id: Number(this.form.mecanico_id),
          monto: Number(this.form.monto),
          moneda: this.form.moneda,
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
    openOrderFromRoute() {
      const orderId = this.$route.query.order_id;
      if (!orderId) return;
      if (this.$route.query.open_chat === "1") {
        this.chatOrdenId = Number(orderId);
        this.showChatModal = true;
        return;
      }
      this.reassignMecanicoId = "";
      this.showDetailModal = true;
      api.get(`/service-orders/${orderId}`).then(({ data }) => {
        this.detail = data;
      }).catch(() => {});
    },
    onOrderUpdated() {
      this.fetchOrders();
      this.fetchCount();
    },
  },
  mounted() {
    this.fetchOrders();
    this.fetchCount();
    this.fetchClients();
    this.fetchMechanics();
    this.fetchCatalog();
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
  font-weight: 800;
}
.page-subtitle {
  color: #666;
  margin-top: 5px;
  margin-left: 48px;
  font-size: 1.05rem;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}
.toolbar-search {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1 1 240px;
  min-width: 200px;
}
.toolbar-search .search-icon {
  position: absolute;
  left: 12px;
  color: #94a3b8;
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 9px 34px 9px 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  box-sizing: border-box;
}
.search-input:focus {
  outline: none;
  border-color: #ffaa00;
  box-shadow: 0 0 0 3px rgba(255,170,0,0.1);
}
.search-clear {
  position: absolute;
  right: 8px;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: #e2e8f0;
  color: #475569;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.search-clear:hover { background: #ffaa00; color: #1a1a1a; }
.clear-filters-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.clear-filters-btn:hover {
  border-color: #ffaa00;
  color: #1a1a1a;
  background: #fff8e6;
}
.filters-toggle {
  display: none;
  align-items: center;
  gap: 6px;
  padding: 9px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.filters-toggle:hover { border-color: #ffaa00; color: #1a1a1a; }
.filters-group {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
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
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 28px;
  border-top: 1px solid #f1f5f9;
}
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
.detail-value.moto-value { flex-direction: column; align-items: flex-start; gap: 4px; }
.detail-sub { font-weight: 700; color: #94a3b8; }
.monto-original { color: #166534; font-weight: 700; }
html.dark .monto-original { color: #4ade80; }
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
  flex-direction: column;
  gap: 8px;
  margin-top: 14px;
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}
.reassign-label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.reassign-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}
.reassign-controls .form-control { flex: 1; min-width: 0; }
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
.form-control {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-control:focus {
  outline: none;
  border-color: #ffaa00;
  box-shadow: 0 0 0 3px rgba(255,170,0,0.1);
  background: #fff;
}
.form-control:disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}
textarea.form-control {
  resize: vertical;
  font-family: inherit;
}
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
/* Cliente search */
.client-search {
  position: relative;
}
.client-search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  max-height: 240px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 30;
}
.client-search-empty {
  padding: 12px 14px;
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
}
.client-search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 10px 14px;
  border: none;
  border-bottom: 1px solid #f1f5f9;
  background: none;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  font-size: 14px;
  color: #1a1a1a;
  transition: background 0.12s;
}
.client-search-item:last-child { border-bottom: none; }
.client-search-item:hover { background: #f8fafc; }
.client-search-name { font-weight: 600; }
.client-search-cedula { color: #64748b; font-size: 13px; white-space: nowrap; }
.client-selected {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #f8fafc;
  color: #1a1a1a;
  font-size: 14px;
}
.client-selected svg { color: #ffaa00; flex-shrink: 0; }
.client-selected-name { font-weight: 600; }
.client-selected-cedula { color: #64748b; font-size: 13px; }
.client-selected-clear {
  margin-left: auto;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: #e2e8f0;
  color: #475569;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.12s, color 0.12s;
}
.client-selected-clear:hover { background: #ffaa00; color: #1a1a1a; }
html.dark .client-search-dropdown { background: var(--bg-card); border-color: var(--border-input); }
html.dark .client-search-item { color: var(--text-default); border-bottom-color: var(--bg-muted); }
html.dark .client-search-item:hover { background: var(--bg-hover); }
html.dark .client-search-cedula { color: var(--text-muted); }
html.dark .client-search-empty { color: var(--text-muted); }
html.dark .client-selected { background: var(--bg-input); border-color: var(--border-input); color: var(--text-default); }
html.dark .client-selected-cedula { color: var(--text-muted); }
html.dark .client-selected-clear { background: var(--bg-muted); color: var(--text-secondary); }
html.dark .client-selected-clear:hover { background: var(--color-primary); color: #1a1a1a; }
/* Monto */
.monto-toggle {
  display: flex;
  gap: 0;
  margin-bottom: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
  max-width: 200px;
}
.monto-toggle .toggle-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: #f8fafc;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}
.monto-toggle .toggle-btn.active {
  background: #ffaa00;
  color: #1a1a1a;
}
.monto-input-row {
  position: relative;
  max-width: 260px;
}
.monto-input-row input {
  padding-right: 46px;
}
.monto-currency {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: 700;
  font-size: 14px;
  color: #475569;
  pointer-events: none;
}
.monto-preview {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #166534;
}
.monto-tasa {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}
.monto-tasa.warn {
  color: #b45309;
  font-weight: 600;
}
html.dark .monto-toggle { border-color: var(--border-input); }
html.dark .monto-toggle .toggle-btn { background: var(--bg-muted); color: var(--text-muted); }
html.dark .monto-toggle .toggle-btn.active { background: var(--color-primary); color: #1a1a1a; }
html.dark .monto-currency { color: var(--text-secondary); }
html.dark .monto-preview { color: #4ade80; }
html.dark .monto-tasa { color: var(--text-muted); }
html.dark .monto-tasa.warn { color: #fbbf24; }
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
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-recolor:hover {
  border-color: #ffaa00;
  color: #1a1a1a;
  background: #fff8e6;
}
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
/* ===== MOBILE / PWA native feel ===== */
@media (max-width: 768px) {
  .admin-orders {
    padding: 12px 12px 80px;
  }
  .orders-header h1 {
    font-size: 1.3rem;
  }
  .page-subtitle {
    margin-left: 0;
    font-size: 0.9rem;
  }
  .orders-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .toolbar {
    flex-direction: column;
    gap: 8px;
  }
  .toolbar-search {
    flex: 1 1 100%;
    min-width: 100%;
  }
  .search-input {
    padding: 12px 38px 12px 40px;
    border-radius: 10px;
    font-size: 15px;
  }
  .toolbar-search .search-icon {
    left: 14px;
  }
  .clear-filters-btn {
    width: 100%;
    justify-content: center;
    padding: 12px;
    border-radius: 10px;
    font-size: 15px;
  }
  .filters-toggle {
    display: flex;
    width: 100%;
    justify-content: center;
    padding: 12px;
    border-radius: 10px;
    font-size: 15px;
  }
  .filters-group {
    display: none;
    flex-direction: column;
    gap: 8px;
    width: 100%;
  }
  .filters-group.filters-open {
    display: flex;
  }
  .filter-select {
    min-width: 100%;
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    font-size: 14px;
  }
  .btn-primary {
    width: 100%;
    padding: 14px;
    border-radius: 12px;
    font-size: 15px;
    text-align: center;
    justify-content: center;
  }
  .modal {
    width: 95%;
    max-width: none;
    border-radius: 16px;
    max-height: 80vh;
  }
  .modal-body {
    padding: 16px;
  }
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .detail-item {
    padding: 10px;
  }
  .actions-row {
    flex-direction: column;
    gap: 8px;
  }
  .action-btn {
    width: 100%;
    justify-content: center;
    padding: 14px;
    border-radius: 12px;
    font-size: 14px;
  }
  .reassign-inline {
    margin-top: 12px;
    padding: 12px;
  }
  .reassign-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .reassign-controls .form-control {
    width: 100%;
  }
  .pagination {
    padding: 8px 0 20px;
  }
}
html.dark .data-table tr {
  background: #1a1f2e;
  border-color: #1e293b;
}
html.dark .data-table td {
  color: #e2e8f0;
}
html.dark .search-input {
  background: var(--bg-input, #1a1f2e);
  border-color: var(--border-input, #334155);
  color: var(--text-default, #e2e8f0);
}
html.dark .search-input:focus { border-color: var(--color-primary, #ffaa00); }
html.dark .toolbar-search .search-icon { color: var(--text-muted, #94a3b8); }
html.dark .search-clear { background: var(--bg-muted, #334155); color: var(--text-secondary, #cbd5e1); }
html.dark .search-clear:hover { background: var(--color-primary, #ffaa00); color: #1a1a1a; }
html.dark .clear-filters-btn {
  background: var(--bg-input, #1a1f2e);
  border-color: var(--border-input, #334155);
  color: var(--text-secondary, #cbd5e1);
}
html.dark .clear-filters-btn:hover { color: var(--text-default, #e2e8f0); background: var(--bg-hover, #232b3d); }
html.dark .filters-toggle {
  background: var(--bg-input, #1a1f2e);
  border-color: var(--border-input, #334155);
  color: var(--text-secondary, #cbd5e1);
}
html.dark .filters-toggle:hover { color: var(--text-default, #e2e8f0); }
html.dark .reassign-inline {
  background: var(--bg-input, #1a1f2e);
  border-color: var(--border-input, #334155);
}
html.dark .reassign-label { color: var(--text-muted, #94a3b8); }
</style>
