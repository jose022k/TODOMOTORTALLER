<template>
  <div class="catalog-container">
    <div class="catalog-header">
      <div class="header-content">
        <h1>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;"><path d="M3 4h8v16H3z"/><path d="M13 4h8v16H13z"/><path d="M11 4v16"/><line x1="4" y1="8" x2="10" y2="8"/><line x1="4" y1="11" x2="10" y2="11"/><line x1="4" y1="14" x2="10" y2="14"/><line x1="14" y1="8" x2="20" y2="8"/><line x1="14" y1="11" x2="20" y2="11"/><line x1="14" y1="14" x2="20" y2="14"/></svg>
          Catálogo de Motocicletas
        </h1>
        <p>Gestiona los modelos y marcas disponibles en el taller</p>
      </div>
      <div class="header-buttons">
        <button class="btn-primary btn-add" @click="openCreateModal">
          <span class="btn-icon">+</span> Nuevo Modelo
        </button>
        <button class="btn-secondary btn-add-brand" @click="openBrandModal">
          <span class="btn-icon">+</span> Nueva Marca
        </button>
      </div>
    </div>

    <!-- Barra de búsqueda y filtrado -->
    <div class="filter-bar">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Buscar por marca o modelo..." 
        class="search-input"
        @input="onSearchInput"
      />
    </div>

    <!-- Mensajes de Alerta -->
    <transition name="fade">
      <div v-if="alert.message" :class="['alert-banner', alert.type]">
        <span>{{ alert.message }}</span>
        <button class="btn-close-alert" @click="clearAlert">×</button>
      </div>
    </transition>

    <!-- Estado de Carga -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando catálogo...</p>
    </div>

    <!-- Catálogo Vacío -->
    <div v-else-if="catalog.length === 0" class="empty-state">
      <div class="empty-icon">🏍️</div>
      <h3>No se encontraron modelos</h3>
      <p>Prueba con otra búsqueda o agrega un nuevo modelo al catálogo.</p>
    </div>

    <!-- Lista de Catálogo en Grid -->
    <div v-else class="catalog-grid">
      <div 
        v-for="item in catalog" 
        :key="item.id" 
        class="catalog-card"
      >
        <div class="card-icon">
          <img v-if="item.logo_url" :src="item.logo_url" :alt="item.marca" class="card-logo" />
          <span v-else>🏍️</span>
        </div>
        <div class="card-body">
          <h2 class="card-title">{{ item.modelo }}</h2>
          <p class="card-subtitle">{{ item.marca }}</p>
        </div>
      
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="!loading && totalPages > 1" class="pagination">
      <button class="page-btn" :disabled="page <= 1" @click="goToPage(page - 1)">&#9664;</button>
      <span class="page-info">{{ page }} / {{ totalPages }}</span>
      <button class="page-btn" :disabled="page >= totalPages" @click="goToPage(page + 1)">&#9654;</button>
    </div>

    <!-- Modal Formulario (Crear / Editar) -->
    <transition name="fade">
      <div v-if="modal.show" class="modal-backdrop" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header">
            <h2>{{ modal.isEdit ? 'Editar Modelo' : 'Nuevo Modelo' }}</h2>
            <button class="btn-close" @click="closeModal">×</button>
          </div>
          <form @submit.prevent="saveModel">
            <div class="form-group">
              <label for="marca">Marca</label>
              <select
                id="marca"
                v-model="modal.form.marca"
                :disabled="modal.isEdit"
                required
              >
                <option value="" disabled>Selecciona una marca</option>
                <option v-for="b in brandNames" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div class="form-group">
              <label for="modelo">Modelo</label>
              <input 
                id="modelo" 
                v-model="modal.form.modelo" 
                type="text" 
                placeholder="Ej. GN 125, MT-09, V-Strom" 
                :disabled="modal.isEdit"
                required 
              />
            </div>

            <div v-if="modal.form.logo_url" class="form-group logo-auto-group">
              <label>Logo de {{ modal.form.marca }}</label>
              <div class="logo-preview-box">
                <img :src="modal.form.logo_url" :alt="'Logo ' + modal.form.marca" />
              </div>
            </div>
            
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal" :disabled="modal.saving">
                Cancelar
              </button>
              <button type="submit" class="btn-primary" :disabled="modal.saving">
                {{ modal.saving ? 'Guardando...' : 'Guardar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>

    <!-- Modal Nueva Marca -->
    <transition name="fade">
      <div v-if="brandModal.show" class="modal-backdrop" @click.self="closeBrandModal">
        <div class="modal-card">
          <div class="modal-header">
            <h2>Nueva Marca</h2>
            <button class="btn-close" @click="closeBrandModal">×</button>
          </div>
          <form @submit.prevent="saveBrand">
            <div class="form-group">
              <label for="brand-nombre">Nombre de la Marca</label>
              <input id="brand-nombre" v-model="brandModal.nombre" type="text" placeholder="Ej. Yamaha, Suzuki, Honda" required />
            </div>
            <div class="form-group">
              <label>Logo <span class="label-optional">(PNG recomendado)</span></label>
              <div
                class="brand-drop-zone"
                :class="{ 'brand-dragging': brandModal.dragging, 'brand-has-file': brandModal.preview }"
                @click="$refs.brandLogoInput.click()"
                @dragover.prevent="brandModal.dragging = true"
                @dragleave.prevent="brandModal.dragging = false"
                @drop.prevent="onBrandDrop"
              >
                <input ref="brandLogoInput" type="file" accept="image/png,image/jpeg,image/webp" @change="onBrandLogoChange" hidden />
                <div v-if="!brandModal.preview" class="brand-drop-content">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                  <p class="brand-drop-text">{{ brandModal.dragging ? 'Suelta la imagen aquí' : 'Haz clic o arrastra una imagen' }}</p>
                  <span class="brand-drop-hint">Peso máximo: 8 MB</span>
                </div>
                <div v-else class="brand-logo-preview">
                  <img :src="brandModal.preview" alt="Vista previa" />
                  <button type="button" class="brand-remove-btn" @click.stop="removeBrandLogo" title="Quitar imagen">×</button>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeBrandModal" :disabled="brandModal.saving">
                Cancelar
              </button>
              <button type="submit" class="btn-primary" :disabled="brandModal.saving || !brandModal.file">
                {{ brandModal.saving ? 'Agregando...' : 'Agregar Marca' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "CatalogoMotosView",
  data() {
    return {
      catalog: [],
      brands: [],
      searchQuery: "",
      loading: false,
      page: 1,
      pageSize: 30,
      totalItems: 0,
      totalPages: 0,
      searchTimer: null,
      alert: {
        message: "",
        type: "", // 'success' o 'error'
      },
      alertTimeout: null,
      modal: {
        show: false,
        isEdit: false,
        saving: false,
        form: {
          id: null,
          marca: "",
          modelo: "",
          gama_color: "",
          logo_url: "",
        },
      },
      brandModal: {
        show: false,
        saving: false,
        nombre: "",
        file: null,
        preview: "",
        dragging: false,
      },
    };
  },
  computed: {
    brandNames() {
      return this.brands.map((b) => b.marca).sort();
    },
  },
  mounted() {
    this.fetchCatalog();
    this.fetchCatalogCount();
    this.fetchBrands();
  },
  watch: {
    "modal.form.marca"(newMarca) {
      if (!newMarca) {
        this.modal.form.logo_url = "";
        return;
      }
      const found = this.brands.find((b) => b.marca === newMarca);
      this.modal.form.logo_url = found?.logo_url || "";
    },
  },
  methods: {
    async fetchCatalog() {
      this.loading = true;
      try {
        const params = { skip: (this.page - 1) * this.pageSize, limit: this.pageSize };
        const trimmed = this.searchQuery.trim();
        if (trimmed.length >= 2) params.search = trimmed;
        const { data } = await api.get("/motorcycles/catalog", { params });
        this.catalog = data;
      } catch (err) {
        this.showAlert(
          err.response?.data?.detail || "Error al cargar el catálogo de motos.",
          "error"
        );
      } finally {
        this.loading = false;
      }
    },
    async fetchCatalogCount() {
      try {
        const params = {};
        const trimmed = this.searchQuery.trim();
        if (trimmed.length >= 2) params.search = trimmed;
        const { data } = await api.get("/motorcycles/catalog/count", { params });
        this.totalItems = data.total;
        this.totalPages = Math.ceil(this.totalItems / this.pageSize) || 1;
      } catch (e) {
        console.error("Error fetching count", e);
      }
    },
    async goToPage(p) {
      this.page = p;
      await this.fetchCatalog();
    },
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.page = 1;
        this.fetchCatalog();
        this.fetchCatalogCount();
      }, 300);
    },
    async fetchBrands() {
      try {
        const { data } = await api.get("/motorcycles/brands");
        this.brands = data;
      } catch (err) {
        console.error("Error al cargar marcas:", err);
      }
    },
    showAlert(message, type = "success") {
      this.alert.message = message;
      this.alert.type = type;
      if (this.alertTimeout) clearTimeout(this.alertTimeout);
      this.alertTimeout = setTimeout(() => {
        this.clearAlert();
      }, 5000);
    },
    clearAlert() {
      this.alert.message = "";
      this.alert.type = "";
    },
    openCreateModal() {
      this.modal.isEdit = false;
      this.modal.form = { id: null, marca: "", modelo: "", gama_color: "", logo_url: "" };
      this.modal.show = true;
    },
    openEditModal(item) {
      this.modal.isEdit = true;
      this.modal.form = { ...item };
      this.modal.show = true;
    },
    closeModal() {
      if (this.modal.saving) return;
      this.modal.show = false;
    },
    openBrandModal() {
      this.brandModal.show = true;
      this.brandModal.nombre = "";
      this.brandModal.file = null;
      this.brandModal.preview = "";
      this.brandModal.saving = false;
      this.brandModal.dragging = false;
    },
    closeBrandModal() {
      this.brandModal.show = false;
    },
    setBrandFile(file) {
      if (!file) return;
      this.brandModal.file = file;
      const reader = new FileReader();
      reader.onload = (ev) => { this.brandModal.preview = ev.target.result; };
      reader.readAsDataURL(file);
    },
    onBrandLogoChange(e) {
      this.setBrandFile(e.target.files[0]);
    },
    onBrandDrop(e) {
      this.brandModal.dragging = false;
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        this.setBrandFile(file);
      }
    },
    removeBrandLogo() {
      this.brandModal.file = null;
      this.brandModal.preview = "";
      if (this.$refs.brandLogoInput) this.$refs.brandLogoInput.value = "";
    },
    async saveBrand() {
      this.brandModal.saving = true;
      this.clearAlert();
      try {
        const formData = new FormData();
        formData.append("nombre", this.brandModal.nombre);
        formData.append("logo", this.brandModal.file);
        await api.post("/motorcycles/brands", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        this.brandModal.show = false;
        await this.fetchBrands();
        this.showAlert("Marca agregada exitosamente.");
      } catch (err) {
        this.showAlert(
          err.response?.data?.detail || "Error al agregar la marca.",
          "error"
        );
      } finally {
        this.brandModal.saving = false;
      }
    },
    async saveModel() {
      this.modal.saving = true;
      this.clearAlert();
      try {
        const payload = {
          marca: this.modal.form.marca,
          modelo: this.modal.form.modelo,
          gama_color: this.modal.form.gama_color,
          logo_url: this.modal.form.logo_url || null,
        };

        if (this.modal.isEdit) {
          await api.put(
            `/motorcycles/catalog/${this.modal.form.id}`,
            payload
          );
          this.showAlert("Modelo actualizado correctamente.");
        } else {
          await api.post("/motorcycles/catalog", payload);
          this.showAlert("Modelo agregado al catálogo exitosamente.");
        }
        this.modal.show = false;
        this.page = 1;
        await this.fetchCatalog();
        await this.fetchCatalogCount();
      } catch (err) {
        this.showAlert(
          err.response?.data?.detail || "Error al guardar el modelo de moto.",
          "error"
        );
      } finally {
        this.modal.saving = false;
      }
    },
  },
  beforeUnmount() {
    if (this.alertTimeout) clearTimeout(this.alertTimeout);
    if (this.searchTimer) clearTimeout(this.searchTimer);
  },
};
</script>

<style scoped>
.catalog-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  animation: fadeIn 0.4s ease-out;
}

.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.header-content h1 {
  font-size: 2.2rem;
  color: var(--color-dark);
  font-weight: 800;
  letter-spacing: -0.5px;
}

.header-content p {
  color: #666;
  margin-top: 5px;
  margin-left: 48px;
  font-size: 1.05rem;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--color-primary);
  color: var(--color-dark);
  padding: 12px 24px;
  font-size: 1rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(255, 170, 0, 0.25);
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 170, 0, 0.4);
}

.header-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-add-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f1f5f9;
  color: #1a1a1a;
  padding: 12px 24px;
  font-size: 1rem;
  border-radius: 8px;
  border: 1.5px solid #d1d5db;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  cursor: pointer;
}

.btn-add-brand:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
  transform: translateY(-2px);
}

.brand-drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: #fafafa;
  min-height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-drop-zone:hover {
  border-color: #ffaa00;
  background: #fffcf5;
}

.brand-drop-zone.brand-dragging {
  border-color: #ffaa00;
  background: #fff7e6;
  border-style: solid;
  transform: scale(1.02);
}

.brand-drop-zone.brand-has-file {
  border-style: solid;
  border-color: #10b981;
  background: #f0fdf4;
  padding: 10px;
}

.brand-drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.brand-drop-text {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin: 0;
}

.brand-drop-hint {
  font-size: 11px;
  color: #94a3b8;
}

.brand-logo-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 100%;
}

.brand-logo-preview img {
  max-height: 65px;
  max-width: 100%;
  object-fit: contain;
}

.brand-remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ef4444;
  color: #fff;
  border: 2px solid #fff;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.brand-remove-btn:hover {
  background: #dc2626;
}

.btn-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.filter-bar {
  margin-bottom: 30px;
}

.search-input {
  width: 100%;
  max-width: 500px;
  padding: 14px 20px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: #f8fafc;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
}

.search-input:focus {
  border-color: var(--color-primary);
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(255, 170, 0, 0.08);
}

/* Alert Banner */
.alert-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: 10px;
  margin-bottom: 24px;
  font-weight: 500;
  font-size: 0.95rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.alert-banner.success {
  background-color: #ecfdf5;
  color: #065f46;
  border-left: 5px solid #10b981;
}

.alert-banner.error {
  background-color: #fef2f2;
  color: #991b1b;
  border-left: 5px solid #ef4444;
}

.btn-close-alert {
  background: transparent;
  color: inherit;
  font-size: 1.3rem;
  padding: 0;
  line-height: 1;
  border: none;
}

/* Catalog Grid */
.catalog-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.catalog-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.catalog-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(255, 170, 0, 0.3);
}

.card-icon {
  font-size: 2.2rem;
  background: #fff8eb;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  margin-bottom: 20px;
  border: 1px solid #ffe8cc;
  overflow: hidden;
}

.card-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 6px;
}

.card-body {
  flex-grow: 1;
}

.card-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--color-dark);
  margin-bottom: 4px;
}

.card-subtitle {
  color: #64748b;
  font-size: 0.95rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Pagination */
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

/* Modals */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.25s ease-out;
}

.modal-card {
  background: #ffffff;
  border-radius: 20px;
  width: 90%;
  max-width: 480px;
  padding: 30px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: scale(1);
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-dark);
}

.btn-close {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
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
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  color: #475569;
  margin-bottom: 8px;
}

.form-group input,
.form-group select {
  padding: 12px 16px;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  font-size: 0.95rem;
  width: 100%;
  box-sizing: border-box;
}

.form-group select:disabled {
  background: #f1f5f9;
  color: #64748b;
  cursor: not-allowed;
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(255, 170, 0, 0.15);
  outline: none;
}

.label-optional {
  font-weight: 400;
  color: #94a3b8;
  font-size: 0.82rem;
  margin-left: 4px;
}

.logo-auto-group {
  margin-top: 12px;
}

.logo-preview-box {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px;
  height: 90px;
}

.logo-preview-box img {
  max-height: 65px;
  max-width: 100%;
  object-fit: contain;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

.modal-footer button {
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  border: none;
}
.modal-footer .btn-primary {
  background: #ffaa00;
  color: #1a1a1a;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.modal-footer .btn-primary:hover {
  background: #e69900;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 170, 0, 0.3);
}
.modal-footer .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
.modal-footer .btn-secondary {
  background: #f1f5f9;
  color: #475569;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.modal-footer .btn-secondary:hover {
  background: #e2e8f0;
}
.modal-footer .btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Spinner */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #64748b;
}

.spinner {
  width: 45px;
  height: 45px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

/* Estado Vacío */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #f8fafc;
  border-radius: 20px;
  border: 2px dashed #e2e8f0;
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 16px;
  opacity: 0.8;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: var(--color-dark);
  margin-bottom: 6px;
}

.empty-state p {
  color: #64748b;
}

/* Responsive */
@media (max-width: 900px) {
  .catalog-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .catalog-grid {
    grid-template-columns: 1fr;
  }
}

/* Animaciones */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Vue Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
