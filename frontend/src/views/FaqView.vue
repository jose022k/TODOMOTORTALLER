<template>
  <div class="faq-page">
    <div class="faq-header">
      <button class="btn-back" @click="goBack" title="Volver">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        <span>Volver</span>
      </button>
      <div class="header-titles">
        <h1>Preguntas Frecuentes</h1>
        <p class="subtitle">Tarifas de referencia y servicios del taller</p>
      </div>
    </div>

    <!-- Buscador -->
    <div class="faq-search-box">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar servicio o pregunta (ej: motor, TX, cadena...)"
        class="faq-search-input"
      />
      <button v-if="searchQuery" class="clear-search" @click="searchQuery = ''">&times;</button>
    </div>

    <!-- Indicador de Tasa BCV si está disponible -->
    <div v-if="tasaBcv" class="tasa-info-bar">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
      <span>Tasa de referencia oficial BCV: <strong>1 € = {{ tasaBcv.toFixed(2) }} Bs</strong></span>
    </div>

    <!-- Carga / Lista de FAQs -->
    <div v-if="loading" class="faq-loading">
      <div class="spinner"></div>
      <p>Cargando preguntas frecuentes...</p>
    </div>

    <div v-else-if="filteredFaqs.length === 0" class="faq-empty">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p>No se encontraron resultados para "{{ searchQuery }}"</p>
    </div>

    <div v-else class="faq-list">
      <div
        v-for="(item, index) in filteredFaqs"
        :key="item.id"
        class="faq-card"
        :class="{ expanded: expandedIndex === index }"
        @click="toggleExpand(index)"
      >
        <div class="faq-card-header">
          <div class="faq-card-title-group">
            <span class="faq-service-tag">{{ item.servicio }}</span>
            <h3 class="faq-question">{{ item.pregunta }}</h3>
          </div>
          <div class="faq-price-badge">
            <div class="price-euro">
              <span v-if="item.es_precio_minimo" class="min-label">Mínimo</span>
              <span class="price-num">{{ item.monto_euro }} €</span>
            </div>
            <span v-if="tasaBcv && item.monto_euro > 0" class="price-bs">
              ≈ {{ formatBs(item.monto_euro * tasaBcv) }} Bs
            </span>
          </div>
          <svg class="chevron-icon" :class="{ rotated: expandedIndex === index }" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
        </div>

        <transition name="accordion">
          <div v-if="expandedIndex === index" class="faq-card-body">
            <p class="faq-answer">{{ item.respuesta }}</p>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "FaqView",
  data() {
    return {
      faqs: [],
      loading: true,
      searchQuery: "",
      tasaBcv: null,
      expandedIndex: 0, // Abrir la primera por defecto
    };
  },
  computed: {
    filteredFaqs() {
      if (!this.searchQuery.trim()) return this.faqs;
      const q = this.searchQuery.toLowerCase();
      return this.faqs.filter(
        (f) =>
          f.servicio.toLowerCase().includes(q) ||
          f.pregunta.toLowerCase().includes(q) ||
          f.respuesta.toLowerCase().includes(q)
      );
    },
  },
  async created() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const [faqRes, tasaRes] = await Promise.all([
          api.get("/faq/"),
          api.get("/bcv/tasa").catch(() => ({ data: { tasa: null } })),
        ]);
        this.faqs = faqRes.data;
        this.tasaBcv = tasaRes.data?.tasa || null;
      } catch (err) {
        console.error("Error al cargar FAQs:", err);
      } finally {
        this.loading = false;
      }
    },
    toggleExpand(index) {
      this.expandedIndex = this.expandedIndex === index ? -1 : index;
    },
    goBack() {
      if (window.history.length > 1) {
        this.$router.back();
      } else {
        this.$router.push("/");
      }
    },
    formatBs(val) {
      if (val === null || val === undefined || isNaN(val)) return "0,00";
      return Number(val).toLocaleString("es-VE", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    },
  },
};
</script>

<style scoped>
.faq-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 16px;
}

.faq-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-back:hover {
  background: #ffaa00;
  color: #1a1a1a;
  border-color: #ffaa00;
}

html.dark .btn-back {
  background: #1e293b;
  border-color: #334155;
  color: #cbd5e1;
}

html.dark .btn-back:hover {
  background: #ffaa00;
  color: #1a1a1a;
  border-color: #ffaa00;
}

.header-titles h1 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1.2;
}

html.dark .header-titles h1 {
  color: #f8fafc;
}

.subtitle {
  font-size: 0.95rem;
  color: #64748b;
  margin-top: 2px;
}

html.dark .subtitle {
  color: #94a3b8;
}

/* Buscador */
.faq-search-box {
  position: relative;
  margin-bottom: 20px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.faq-search-input {
  width: 100%;
  padding: 12px 40px 12px 42px;
  border: 1.5px solid #cbd5e1;
  border-radius: 12px;
  font-size: 15px;
  background: #ffffff;
  color: #1a1a1a;
  outline: none;
  transition: border-color 0.2s;
}

.faq-search-input:focus {
  border-color: #ffaa00;
  box-shadow: 0 0 0 3px rgba(255, 170, 0, 0.15);
}

html.dark .faq-search-input {
  background: #1e293b;
  border-color: #334155;
  color: #f8fafc;
}

.clear-search {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 20px;
  color: #94a3b8;
  cursor: pointer;
}

/* Tasa Info Bar */
.tasa-info-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff8eb;
  border: 1px solid #ffe3b3;
  color: #92400e;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13.5px;
  margin-bottom: 24px;
}

html.dark .tasa-info-bar {
  background: #2a2215;
  border-color: #523a13;
  color: #fde68a;
}

/* Spinner / Vacío */
.faq-loading,
.faq-empty {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #cbd5e1;
  border-top-color: #ffaa00;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* FAQs List */
.faq-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.faq-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 18px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.faq-card:hover {
  border-color: #ffaa00;
  box-shadow: 0 4px 16px rgba(255, 170, 0, 0.12);
}

html.dark .faq-card {
  background: #1e293b;
  border-color: #334155;
  box-shadow: none;
}

html.dark .faq-card:hover {
  border-color: #ffaa00;
}

.faq-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.faq-card-title-group {
  flex: 1;
}

.faq-service-tag {
  display: inline-block;
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #b45309;
  background: #fef3c7;
  padding: 3px 8px;
  border-radius: 6px;
  margin-bottom: 6px;
}

html.dark .faq-service-tag {
  color: #fbbf24;
  background: #451a03;
}

.faq-question {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.35;
}

html.dark .faq-question {
  color: #f1f5f9;
}

.faq-price-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  min-width: 90px;
  text-align: right;
}

.price-euro {
  display: flex;
  align-items: center;
  gap: 4px;
}

.min-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  text-transform: lowercase;
}

.price-num {
  font-size: 1.25rem;
  font-weight: 900;
  color: #166534;
}

html.dark .price-num {
  color: #4ade80;
}

.price-bs {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  margin-top: 1px;
}

html.dark .price-bs {
  color: #94a3b8;
}

.chevron-icon {
  color: #94a3b8;
  transition: transform 0.25s ease;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
  color: #ffaa00;
}

.faq-card-body {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed #e2e8f0;
}

html.dark .faq-card-body {
  border-top-color: #334155;
}

.faq-answer {
  font-size: 0.95rem;
  color: #334155;
  line-height: 1.5;
  white-space: pre-line;
}

html.dark .faq-answer {
  color: #cbd5e1;
}

/* Transición acordeón */
.accordion-enter-active,
.accordion-leave-active {
  transition: all 0.25s ease-out;
  max-height: 200px;
  opacity: 1;
  overflow: hidden;
}

.accordion-enter-from,
.accordion-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  padding-top: 0;
}

@media (max-width: 640px) {
  .faq-card-header {
    flex-wrap: wrap;
  }
  .faq-price-badge {
    align-items: flex-start;
    text-align: left;
    width: 100%;
    margin-top: 4px;
    flex-direction: row;
    gap: 8px;
  }
}
</style>
