<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="modal modal-lg faq-admin-modal">
      <div class="modal-header">
        <div class="modal-title-group">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10h12"/><path d="M4 14h9"/><path d="M19 6a7.7 7.7 0 0 0-5.2-2A7.9 7.9 0 0 0 6 12a7.9 7.9 0 0 0 7.8 8 7.7 7.7 0 0 0 5.2-2"/></svg>
          <h2>Gestionar Preguntas Frecuentes y Precios (€)</h2>
        </div>
        <button class="modal-close" @click="close">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Barra superior de acciones -->
        <div class="faq-admin-actions">
          <div class="search-mini">
            <input
              v-model="search"
              type="text"
              placeholder="Buscar pregunta..."
              class="form-control form-control-sm"
            />
          </div>
          <button class="btn-primary btn-sm" @click="openAddForm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Nueva Pregunta
          </button>
        </div>

        <!-- Formulario Crear/Editar -->
        <div v-if="showForm" class="faq-form-card">
          <div class="form-card-header">
            <h3>{{ editingId ? "Editar Pregunta" : "Agregar Nueva Pregunta" }}</h3>
            <button class="btn-text-cancel" @click="cancelForm">Cancelar</button>
          </div>

          <div class="form-grid">
            <div class="form-group full-width">
              <label>Pregunta completa *</label>
              <input
                v-model="form.pregunta"
                type="text"
                class="form-control"
                placeholder="Ej: Costo de motor completo varillero 150 y 200 de cilindrada"
              />
            </div>

            <div class="form-group">
              <label>Precio en Euros (€) *</label>
              <div class="input-currency-row">
                <input
                  v-model.number="form.monto_euro"
                  type="number"
                  step="0.01"
                  min="0"
                  class="form-control"
                  placeholder="Ej: 100"
                />
                <span class="currency-tag">€</span>
              </div>
            </div>

            <div class="form-group">
              <label>Orden de aparición</label>
              <input
                v-model.number="form.orden"
                type="number"
                min="0"
                class="form-control"
                placeholder="0"
              />
            </div>

            <div class="form-group checkbox-group full-width">
              <label class="checkbox-label">
                <input type="checkbox" v-model="form.es_precio_minimo" />
                <span>Indicar como <strong>"Mínimo"</strong> (ej: mínimo 20€)</span>
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn-cancel" @click="cancelForm">Cancelar</button>
            <button class="btn-primary" @click="saveForm" :disabled="saving">
              {{ saving ? "Guardando..." : (editingId ? "Actualizar" : "Guardar Pregunta") }}
            </button>
          </div>
        </div>

        <!-- Tabla / Lista de Preguntas -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando preguntas...</p>
        </div>

        <div v-else-if="filteredFaqs.length === 0" class="empty-state">
          <p>No hay preguntas registradas.</p>
        </div>

        <div v-else class="faq-table-wrapper">
          <table class="faq-table">
            <thead>
              <tr>
                <th style="width: 50px;">#</th>
                <th>Pregunta Frecuente</th>
                <th style="width: 110px; text-align: right;">Monto (€)</th>
                <th style="width: 140px; text-align: center;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in filteredFaqs" :key="f.id" :class="{ 'editing-row': editingId === f.id }">
                <td class="text-center font-mono">{{ f.orden }}</td>
                <td>
                  <div class="faq-item-title">{{ f.pregunta }}</div>
                </td>
                <td class="text-right font-bold">
                  <span v-if="f.es_precio_minimo" class="min-tag">Mínimo </span>
                  <span class="euro-val">{{ f.monto_euro }} €</span>
                </td>
                <td class="text-center">
                  <div class="actions-cell">
                    <button class="btn-icon btn-edit" title="Editar" @click="editItem(f)">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    <button class="btn-icon btn-delete" title="Eliminar" @click="deleteItem(f)">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Confirmación de Eliminación -->
    <ConfirmModal
      :visible="showDeleteModal"
      title="Eliminar Pregunta Frecuente"
      :message="`¿Deseas eliminar la pregunta '${itemToDelete?.pregunta}'?`"
      confirmText="Eliminar"
      cancelText="Cancelar"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script>
import api from "@/services/api";
import ConfirmModal from "@/components/ConfirmModal.vue";

export default {
  name: "AdminFaqModal",
  components: { ConfirmModal },
  props: {
    visible: { type: Boolean, default: false },
  },
  emits: ["close", "updated"],
  data() {
    return {
      faqs: [],
      loading: false,
      search: "",
      showForm: false,
      editingId: null,
      saving: false,
      form: {
        servicio: "",
        pregunta: "",
        respuesta: "",
        monto_euro: 0,
        es_precio_minimo: false,
        orden: 0,
      },
      showDeleteModal: false,
      itemToDelete: null,
    };
  },
  watch: {
    visible(val) {
      if (val) {
        this.fetchFaqs();
      }
    },
  },
  computed: {
    filteredFaqs() {
      if (!this.search.trim()) return this.faqs;
      const q = this.search.toLowerCase();
      return this.faqs.filter(
        (f) =>
          (f.pregunta && f.pregunta.toLowerCase().includes(q)) ||
          (f.respuesta && f.respuesta.toLowerCase().includes(q)) ||
          (f.servicio && f.servicio.toLowerCase().includes(q))
      );
    },
  },
  methods: {
    close() {
      this.cancelForm();
      this.$emit("close");
    },
    async fetchFaqs() {
      this.loading = true;
      try {
        const res = await api.get("/faq/admin/all");
        this.faqs = res.data;
      } catch (err) {
        console.error("Error al cargar FAQs admin:", err);
      } finally {
        this.loading = false;
      }
    },
    openAddForm() {
      this.editingId = null;
      this.form = {
        servicio: "",
        pregunta: "",
        respuesta: "",
        monto_euro: 0,
        es_precio_minimo: false,
        orden: this.faqs.length + 1,
      };
      this.showForm = true;
    },
    editItem(f) {
      this.editingId = f.id;
      this.form = {
        servicio: f.servicio || f.pregunta,
        pregunta: f.pregunta,
        respuesta: f.respuesta,
        monto_euro: f.monto_euro,
        es_precio_minimo: f.es_precio_minimo,
        orden: f.orden,
      };
      this.showForm = true;
    },
    cancelForm() {
      this.showForm = false;
      this.editingId = null;
    },
    async saveForm() {
      this.form.servicio = this.form.pregunta;
      this.form.respuesta = "";
      if (!this.form.pregunta.trim()) {
        alert("Por favor ingresa la pregunta completa.");
        return;
      }
      this.saving = true;
      try {
        if (this.editingId) {
          await api.put(`/faq/${this.editingId}`, this.form);
        } else {
          await api.post("/faq/", this.form);
        }
        this.showForm = false;
        this.editingId = null;
        await this.fetchFaqs();
        this.$emit("updated");
      } catch (err) {
        alert("Error al guardar la pregunta frecuente.");
      } finally {
        this.saving = false;
      }
    },
    deleteItem(f) {
      this.itemToDelete = f;
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (!this.itemToDelete) return;
      try {
        await api.delete(`/faq/${this.itemToDelete.id}`);
        this.showDeleteModal = false;
        this.itemToDelete = null;
        await this.fetchFaqs();
        this.$emit("updated");
      } catch (err) {
        alert("Error al eliminar la pregunta.");
      }
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1200;
  padding: 16px;
}

.modal-lg {
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  background: #ffffff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

html.dark .modal-lg {
  background: #1e293b;
  color: #f8fafc;
}

.modal-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}

html.dark .modal-header {
  border-bottom-color: #334155;
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #ffaa00;
}

.modal-title-group h2 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #1a1a1a;
}

html.dark .modal-title-group h2 {
  color: #f8fafc;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

/* Acciones */
.faq-admin-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.search-mini {
  flex: 1;
  max-width: 300px;
}

.btn-sm {
  padding: 8px 14px;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Form Card */
.faq-form-card {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

html.dark .faq-form-card {
  background: #0f172a;
  border-color: #334155;
}

.form-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.form-card-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

html.dark .form-card-header h3 {
  color: #f1f5f9;
}

.btn-text-cancel {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.full-width {
  grid-column: span 2;
}

.form-group label {
  display: block;
  font-size: 12.5px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 5px;
}

html.dark .form-group label {
  color: #cbd5e1;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 13.5px;
  background: #ffffff;
  color: #1a1a1a;
  outline: none;
}

html.dark .form-control {
  background: #1e293b;
  border-color: #334155;
  color: #f8fafc;
}

.form-control:focus {
  border-color: #ffaa00;
}

.input-currency-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.currency-tag {
  font-weight: 800;
  font-size: 16px;
  color: #ffaa00;
}

.checkbox-group {
  margin-top: 4px;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
}

.checkbox-label input {
  accent-color: #ffaa00;
  width: 16px;
  height: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}

.btn-primary {
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-cancel {
  background: transparent;
  border: 1px solid #cbd5e1;
  color: #475569;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

html.dark .btn-cancel {
  border-color: #334155;
  color: #cbd5e1;
}

/* Tabla */
.faq-table-wrapper {
  overflow-x: auto;
}

.faq-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}

.faq-table th {
  background: #f1f5f9;
  color: #475569;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.5px;
  padding: 10px 12px;
  border-bottom: 2px solid #e2e8f0;
}

html.dark .faq-table th {
  background: #0f172a;
  color: #94a3b8;
  border-bottom-color: #334155;
}

.faq-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: middle;
}

html.dark .faq-table td {
  border-bottom-color: #334155;
}

.editing-row {
  background: rgba(255, 170, 0, 0.08);
}

.faq-item-title {
  font-weight: 700;
  color: #0f172a;
}

html.dark .faq-item-title {
  color: #f1f5f9;
}

.faq-item-sub {
  font-size: 12px;
  color: #64748b;
}

html.dark .faq-item-sub {
  color: #94a3b8;
}

.min-tag {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
}

.euro-val {
  color: #166534;
}

html.dark .euro-val {
  color: #4ade80;
}

.actions-cell {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #475569;
  transition: all 0.15s;
}

html.dark .btn-icon {
  border-color: #334155;
  color: #cbd5e1;
}

.btn-edit:hover {
  background: #ffaa00;
  color: #1a1a1a;
  border-color: #ffaa00;
}

.btn-delete:hover {
  background: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
}

.text-center { text-align: center; }
.text-right { text-align: right; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 700; }

@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .full-width {
    grid-column: span 1;
  }
}
</style>
