<template>
  <div class="reports-page">
    <div class="reports-header">
      <h1>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;"><path d="M4 20h16"/><path d="M4 20V4"/><path d="M8 14V8"/><path d="M12 14v-4"/><path d="M16 14v-6"/><path d="M20 14V6"/></svg>
        Reportes y Estadísticas
      </h1>
      <div class="reports-filters">
        <label class="filter-group">
          <span>Desde</span>
          <input type="date" v-model="fechaInicio" @change="fetchAll" class="filter-date" />
        </label>
        <label class="filter-group">
          <span>Hasta</span>
          <input type="date" v-model="fechaFin" @change="fetchAll" class="filter-date" />
        </label>
        <button v-if="fechaInicio || fechaFin" class="btn-clear" @click="clearFilters">Limpiar filtros</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Cargando reportes...</div>

    <template v-else>
      <!-- Tiempo Promedio -->
      <div class="report-card highlight-card">
        <div class="highlight-value">{{ avgMinutes }} min</div>
        <div class="highlight-label">Tiempo Promedio de Reparación</div>
      </div>

      <div class="reports-grid">
        <!-- Mecánicos con más servicios -->
        <div class="report-card">
          <div class="report-card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M9 14l2 2 4-4"/></svg>
            <h3>Top Mecánicos</h3>
          </div>
          <div class="report-list">
            <div v-for="(m, i) in topMecanicos" :key="m.id" class="report-item">
              <span class="report-rank">#{{ i + 1 }}</span>
              <span class="report-name">{{ m.nombre }}</span>
              <span class="report-value">{{ m.total_servicios }} servicios</span>
            </div>
            <div v-if="topMecanicos.length === 0" class="report-empty">Sin datos</div>
          </div>
        </div>

        <!-- Motos más atendidas -->
        <div class="report-card">
          <div class="report-card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="14" r="4"/><circle cx="18" cy="14" r="4"/><path d="M6 14h12"/><path d="M16 4h-4l-3 5h7l2 3"/><path d="M3 10h3l1-2"/></svg>
            <h3>Top Motos Atendidas</h3>
          </div>
          <div class="report-list">
            <div v-for="(m, i) in topMotos" :key="i" class="report-item">
              <span class="report-rank">#{{ i + 1 }}</span>
              <span class="report-name">{{ m.marca }} {{ m.modelo }}</span>
              <span class="report-value">{{ m.total_ordenes }} {{ m.total_ordenes === 1 ? 'orden' : 'órdenes' }}</span>
            </div>
            <div v-if="topMotos.length === 0" class="report-empty">Sin datos</div>
          </div>
        </div>

        <!-- Servicios más realizados -->
        <div class="report-card">
          <div class="report-card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
            <h3>Top Servicios Realizados</h3>
          </div>
          <div class="report-list">
            <div v-for="(s, i) in topServicios" :key="i" class="report-item">
              <span class="report-rank">#{{ i + 1 }}</span>
              <span class="report-name">{{ s.descripcion }}</span>
              <span class="report-value">{{ s.total }} {{ s.total === 1 ? 'vez' : 'veces' }}</span>
            </div>
            <div v-if="topServicios.length === 0" class="report-empty">Sin datos</div>
          </div>
        </div>

        <!-- Días con más clientes -->
        <div class="report-card">
          <div class="report-card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <h3>Días con más clientes</h3>
          </div>
          <div class="report-list">
            <div v-for="d in diasSemana" :key="d.dia" class="report-item">
              <span class="report-name">{{ d.dia }}</span>
              <span class="report-value">{{ d.total }} órdenes</span>
            </div>
            <div v-if="diasSemana.length === 0" class="report-empty">Sin datos</div>
          </div>
        </div>

        <!-- Clientes recurrentes -->
        <div class="report-card">
          <div class="report-card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
            <h3>Clientes Recurrentes</h3>
          </div>
          <div class="report-list">
            <div v-for="(c, i) in topClientes" :key="c.id" class="report-item">
              <span class="report-rank">#{{ i + 1 }}</span>
              <span class="report-name">{{ c.nombre }}</span>
              <span class="report-value">{{ c.total_ordenes }} órdenes</span>
            </div>
            <div v-if="topClientes.length === 0" class="report-empty">Sin datos</div>
          </div>
        </div>

        <!-- Rendimiento por mecánico -->
        <div class="report-card">
          <div class="report-card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20v-6"/><path d="M12 10V4"/><path d="M6 20v-4"/><path d="M6 12V4"/><path d="M18 20v-8"/><path d="M18 8V4"/></svg>
            <h3>Rendimiento por Mecánico</h3>
          </div>
          <div class="report-list">
            <div v-for="m in rendimientoMecanicos" :key="m.id" class="report-item">
              <span class="report-name">{{ m.nombre }}</span>
              <span class="report-value">{{ m.total_ordenes }} ord · {{ m.minutos_promedio.toFixed(1) }} min prom</span>
            </div>
            <div v-if="rendimientoMecanicos.length === 0" class="report-empty">Sin datos</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "AdminReports",
  data() {
    return {
      loading: true,
      avgMinutes: 0,
      topMecanicos: [],
      topMotos: [],
      topServicios: [],
      topClientes: [],
      rendimientoMecanicos: [],
      diasSemana: [],
      fechaInicio: "",
      fechaFin: "",
    };
  },
  mounted() {
    this.fetchAll();
  },
  methods: {
    dateParams() {
      const params = {};
      if (this.fechaInicio) params.fecha_inicio = this.fechaInicio + "T00:00:00";
      if (this.fechaFin) params.fecha_fin = this.fechaFin + "T23:59:59";
      return params;
    },
    async fetchAll() {
      this.loading = true;
      try {
        const dp = this.dateParams();
        const [avgRes, mecRes, motoRes, servRes, diasRes, cliRes, rendRes] = await Promise.all([
          api.get("/reports/tiempo-promedio-reparacion", { params: dp }),
          api.get("/reports/mecanicos/mas-servicios", { params: dp }),
          api.get("/reports/motos/mas-atendidas", { params: dp }),
          api.get("/reports/servicios/top-descripciones", { params: dp }),
          api.get("/reports/ordenes/por-dia-semana"),
          api.get("/reports/clientes/recurrentes", { params: dp }),
          api.get("/reports/mecanicos/rendimiento", { params: dp }),
        ]);
        this.avgMinutes = avgRes.data.minutos_promedio;
        this.topMecanicos = mecRes.data;
        this.topMotos = motoRes.data;
        this.topServicios = servRes.data;
        this.diasSemana = diasRes.data;
        this.topClientes = cliRes.data;
        this.rendimientoMecanicos = rendRes.data;
      } catch (err) {
        console.error("Error al cargar reportes", err);
      } finally {
        this.loading = false;
      }
    },
    clearFilters() {
      this.fechaInicio = "";
      this.fechaFin = "";
      this.fetchAll();
    },
  },
};
</script>

<style scoped>
.reports-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.reports-header h1 { font-size: 1.8rem; color: #1a1a1a; font-weight: 800; }
.reports-filters {
  display: flex;
  align-items: center;
  gap: 12px;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}
.filter-date {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  color: #1a1a1a;
}
.filter-date:focus {
  outline: none;
  border-color: #ffaa00;
  box-shadow: 0 0 0 3px rgba(255,170,0,0.1);
}
.btn-clear {
  background: #f1f5f9;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}
.btn-clear:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
}
.loading-state { text-align: center; padding: 60px; color: #64748b; font-size: 1rem; }

/* Highlight card */
.highlight-card {
  text-align: center;
  padding: 32px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #fff7e6, #fff3d6);
  border: 1.5px solid #ffaa00;
}
.highlight-value {
  font-size: 3rem;
  font-weight: 800;
  color: #1a1a1a;
}
.highlight-label {
  font-size: 1rem;
  color: #64748b;
  margin-top: 4px;
  font-weight: 600;
}

/* Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
.report-card {
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.report-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #ffaa00;
}
.report-card-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
}
.report-list { display: flex; flex-direction: column; gap: 8px; }
.report-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 0.85rem;
}
.report-rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ffaa00;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.report-name { flex: 1; font-weight: 600; color: #1a1a1a; }
.report-value { font-size: 0.8rem; color: #64748b; white-space: nowrap; }
.report-empty { text-align: center; padding: 16px; color: #94a3b8; font-size: 0.85rem; }
</style>
