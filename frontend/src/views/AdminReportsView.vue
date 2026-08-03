<template>
  <div class="reports-page">
    <div class="reports-header">
      <div class="header-content">
        <h1>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; vertical-align: middle;"><path d="M4 20h16"/><path d="M4 20V4"/><path d="M8 14V8"/><path d="M12 14v-4"/><path d="M16 14v-6"/><path d="M20 14V6"/></svg>
          Reportes y Estadísticas
        </h1>
        <p class="page-subtitle">Visualiza y descarga reportes detallados del taller</p>
      </div>
      <div class="print-header">
        <div class="print-header-spacer"></div>
        <div class="print-title-text">
          <div class="print-title">Reporte N° {{ pdfNumber }}</div>
          <div class="print-company">Todomotortaller 1703, C.A.</div>
        </div>
        <img src="https://res.cloudinary.com/dorj3mvvr/image/upload/v1783609693/logos/logotaller01.png" alt="" class="print-logo" />
      </div>
      <div class="reports-toolbar no-print">
        <label class="filter-group">
          <span>Desde</span>
          <input type="date" v-model="fechaInicio" @change="fetchAll" class="filter-date" />
        </label>
        <label class="filter-group">
          <span>Hasta</span>
          <input type="date" v-model="fechaFin" @change="fetchAll" class="filter-date" />
        </label>
        <button v-if="fechaInicio || fechaFin" class="btn-clear" @click="clearFilters">Limpiar filtros</button>
        <div class="tasa-chip" @click="editTasa = true" title="Editar tasa BCV">
          <span class="tasa-chip-label">Tasa BCV</span>
          <span class="tasa-chip-value">{{ tasaBcv ? tasaBcv.toFixed(2) + ' Bs/$' : 'N/D' }}</span>
          <svg v-if="editTasa" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-left:4px;"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-left:4px;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </div>
        <div v-if="editTasa" class="tasa-editor">
          <input v-model="tasaInput" type="number" step="0.01" min="0" class="filter-date" placeholder="Tasa del día" />
          <button class="btn-clear" @click="saveTasa">Guardar</button>
          <button class="btn-clear" @click="editTasa = false">Cancelar</button>
        </div>
        <div class="pdf-dropdown">
          <button class="btn-pdf" @click="showPdfMenu = !showPdfMenu">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            Generar PDF
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="margin-left:2px;"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div v-if="showPdfMenu" class="pdf-dropdown-content">
            <div class="pdf-dropdown-header">Seleccionar secciones</div>
            <label class="pdf-check" v-for="s in printSections" :key="s.key">
              <input type="checkbox" v-model="s.checked" />
              <span>{{ s.label }}</span>
            </label>
            <div class="pdf-dropdown-actions">
              <button class="btn-pdf-generate" @click="printReport">Generar PDF</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state no-print">
      <div class="spinner"></div>
      <p>Cargando reportes...</p>
    </div>

    <template v-else>
      <div class="report-card highlight-card no-print">
        <div class="highlight-value">{{ avgMinutes }} min</div>
        <div class="highlight-label">Tiempo Promedio de Reparación</div>
      </div>

      <div class="reports-grid" id="reports-dashboard">
        <div v-for="s in visibleSections" :key="s.key" class="report-card chart-card" :class="{ 'print-hidden': !s.checked }">
          <div class="report-card-header">
            <span v-html="s.icon"></span>
            <h3>{{ s.label }}</h3>
          </div>
          <div v-if="s.data.length === 0" class="report-empty">Sin datos</div>
          <div v-else class="chart-wrapper screen-only">
            <Line v-if="s.key === 'ganancias'" :data="s.chartData" :options="s.chartOptions" />
            <Doughnut v-else-if="s.key === 'estados_ordenes'" :data="s.chartData" :options="s.chartOptions" />
            <Bar v-else :data="s.chartData" :options="s.chartOptions" />
          </div>
          <div v-if="s.data.length > 0" class="print-table-wrapper">
            <table class="print-table">
              <thead>
                <tr>
                  <th v-for="col in s.columns" :key="col.key">{{ col.label }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in s.data" :key="i">
                  <td v-for="col in s.columns" :key="col.key">
                    <template v-if="col.key === '_rank'">#{{ i + 1 }}</template>
                    <template v-else-if="col.key === 'total_servicios'">{{ row.total_servicios }} {{ row.total_servicios === 1 ? 'servicio' : 'servicios' }}</template>
                    <template v-else-if="col.key === 'total_ordenes'">{{ row.total_ordenes }} {{ row.total_ordenes === 1 ? 'orden' : 'órdenes' }}</template>
                    <template v-else-if="col.key === 'total'">{{ row.total }} {{ row.total === 1 ? 'vez' : 'veces' }}</template>
                    <template v-else-if="col.key === 'minutos_promedio'">{{ Number(row.minutos_promedio).toFixed(1) }} min</template>
                    <template v-else-if="col.key === 'nombre' && s.key === 'clientes'">{{ capitalize(row.nombre) }}</template>
                    <template v-else-if="col.key === 'nombre'">{{ row.nombre }}</template>
                    <template v-else-if="col.key === 'moto'">{{ row.marca }} {{ row.modelo }}</template>
                    <template v-else-if="col.key === 'dia'">{{ row.dia }}</template>
                    <template v-else-if="col.key === 'total_dia'">{{ row.total }} órdenes</template>
                    <template v-else-if="col.key === 'total_usd'">$ {{ Number(row.total_usd).toFixed(2) }}</template>
                    <template v-else-if="col.key === 'porcentaje'">{{ Number(row.porcentaje).toFixed(1) }}%</template>
                    <template v-else-if="col.key === 'cantidad'">{{ row.cantidad }} {{ row.cantidad === 1 ? 'orden' : 'órdenes' }}</template>
                    <template v-else>{{ row[col.key] }}</template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { Bar, Line, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import api from "@/services/api";

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend);

const COLORS = [
  "#ffaa00", "#f59e0b", "#eab308", "#d97706",
  "#fbbf24", "#fcd34d", "#fde68a",
];

export default {
  name: "AdminReports",
  components: { Bar, Line, Doughnut },
  data() {
    return {
      loading: true,
      avgMinutes: 0,
      topMecanicos: [],
      topMotos: [],
      topServicios: [],
      topClientes: [],
      estadosOrdenes: [],
      rendimientoMecanicos: [],
      diasSemana: [],
      ganancias: [],
      tasaBcv: null,
      editTasa: false,
      tasaInput: "",
      fechaInicio: "",
      fechaFin: "",
      showPdfMenu: false,
      pdfCounter: parseInt(localStorage.getItem("pdfCounter") || "1", 10),
      printSections: [
        { key: "ganancias", label: "Ganancias", checked: true },
        { key: "mecanicos", label: "Top Mecánicos", checked: true },
        { key: "motos", label: "Top Motos Atendidas", checked: true },
        { key: "servicios", label: "Top Servicios Realizados", checked: true },
        { key: "dias", label: "Días con más clientes", checked: true },
        { key: "clientes", label: "Clientes Recurrentes", checked: true },
        { key: "estados_ordenes", label: "Órdenes Completadas vs Canceladas", checked: true },
        { key: "rendimiento", label: "Rendimiento por Mecánico", checked: true },
      ],
    };
  },
  computed: {
    pdfNumber() {
      return String(this.pdfCounter).padStart(7, "0");
    },
    visibleSections() {
      const icons = {
        ganancias: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
        mecanicos: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M9 14l2 2 4-4"/></svg>',
        motos: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="14" r="4"/><circle cx="18" cy="14" r="4"/><path d="M6 14h12"/><path d="M16 4h-4l-3 5h7l2 3"/><path d="M3 10h3l1-2"/></svg>',
        servicios: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
        dias: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        clientes: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>',
        estados_ordenes: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
        rendimiento: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20v-6"/><path d="M12 10V4"/><path d="M6 20v-4"/><path d="M6 12V4"/><path d="M18 20v-8"/><path d="M18 8V4"/></svg>',
      };
      const columns = {
        ganancias: [{ key: "dia", label: "Día" }, { key: "total_usd", label: "Monto" }],
        mecanicos: [{ key: "_rank", label: "#" }, { key: "nombre", label: "Nombre" }, { key: "total_servicios", label: "Servicios" }],
        motos: [{ key: "_rank", label: "#" }, { key: "moto", label: "Moto" }, { key: "total_ordenes", label: "Órdenes" }],
        servicios: [{ key: "_rank", label: "#" }, { key: "descripcion", label: "Servicio" }, { key: "total", label: "Veces" }],
        dias: [{ key: "dia", label: "Día" }, { key: "total_dia", label: "Órdenes" }],
        clientes: [{ key: "_rank", label: "#" }, { key: "nombre", label: "Cliente" }, { key: "total_ordenes", label: "Órdenes" }],
        estados_ordenes: [{ key: "tipo", label: "Estado" }, { key: "cantidad", label: "Órdenes" }, { key: "porcentaje", label: "% del total" }],
        rendimiento: [{ key: "nombre", label: "Mecánico" }, { key: "minutos_promedio", label: "Tiempo Promedio" }],
      };
      const dataMap = {
        ganancias: this.ganancias,
        mecanicos: this.topMecanicos,
        motos: this.topMotos,
        servicios: this.topServicios,
        dias: this.diasSemana,
        clientes: this.topClientes,
        estados_ordenes: this.estadosOrdenes,
        rendimiento: this.rendimientoMecanicos,
      };
      const chartBuilders = {
        ganancias: (d) => ({
          labels: d.map((g) => g.dia),
          datasets: [{
            label: "Ganancias ($)",
            data: d.map((g) => g.total_usd),
            borderColor: "#ffaa00",
            backgroundColor: "#ffaa00",
            pointBackgroundColor: "#ffaa00",
            pointBorderColor: "#1a1a1a",
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8,
            borderWidth: 3,
            tension: 0.3,
            fill: false,
          }],
        }),
        mecanicos: (d) => ({
          labels: d.map((m) => m.nombre),
          datasets: [{ label: "Servicios", data: d.map((m) => m.total_servicios), backgroundColor: COLORS.slice(0, d.length), borderRadius: 6 }],
        }),
        motos: (d) => ({
          labels: d.map((m) => m.marca + " " + m.modelo),
          datasets: [{ label: "Órdenes", data: d.map((m) => m.total_ordenes), backgroundColor: COLORS.slice(0, d.length), borderRadius: 6 }],
        }),
        servicios: (d) => ({
          labels: d.map((s) => s.descripcion),
          datasets: [{ label: "Veces", data: d.map((s) => s.total), backgroundColor: COLORS.slice(0, d.length), borderRadius: 6 }],
        }),
        dias: (d) => ({
          labels: d.map((dia) => dia.dia),
          datasets: [{ label: "Órdenes", data: d.map((dia) => dia.total), backgroundColor: COLORS.slice(0, d.length), borderRadius: 6 }],
        }),
        clientes: (d) => ({
          labels: d.map((c) => c.nombre),
          datasets: [{ label: "Órdenes", data: d.map((c) => c.total_ordenes), backgroundColor: COLORS.slice(0, d.length), borderRadius: 6 }],
        }),
        estados_ordenes: (d) => ({
          labels: d.map((x) => x.tipo),
          datasets: [{
            label: "Órdenes",
            data: d.map((x) => x.cantidad),
            backgroundColor: ["#22c55e", "#ef4444"],
            borderColor: "#fff",
            borderWidth: 2,
          }],
        }),
        rendimiento: (d) => ({
          labels: d.map((m) => m.nombre),
          datasets: [{ label: "Tiempo promedio (min)", data: d.map((m) => Number(m.minutos_promedio).toFixed(1)), backgroundColor: "#ffaa00", borderRadius: 6 }],
        }),
      };
      const baseOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: { backgroundColor: "#1a1a1a", titleFont: { size: 12 }, bodyFont: { size: 12 } },
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11 } } },
          y: { grid: { display: false }, ticks: { font: { size: 11 } } },
        },
      };

      return this.printSections
        .map((s) => {
          const raw = dataMap[s.key];
          const isHoriz = s.key !== "dias" && s.key !== "ganancias" && s.key !== "estados_ordenes";
            let opts;
            if (s.key === "estados_ordenes") {
              opts = {
                ...baseOptions,
                plugins: {
                  ...baseOptions.plugins,
                  legend: { display: true, position: "bottom", labels: { font: { size: 12 }, boxWidth: 14, padding: 14 } },
                },
              };
            } else if (s.key === "ganancias") {
              opts = {
                ...baseOptions,
                plugins: {
                  ...baseOptions.plugins,
                  tooltip: {
                    ...baseOptions.plugins.tooltip,
                    callbacks: { label: (ctx) => ` $ ${Number(ctx.parsed.y).toFixed(2)}` },
                  },
                },
                scales: {
                  ...baseOptions.scales,
                  y: {
                    ...baseOptions.scales.y,
                    min: 15,
                    max: 300,
                    ticks: {
                      ...baseOptions.scales.y.ticks,
                      callback: (v) => "$" + v,
                    },
                  },
                },
              };
            } else {
              opts = isHoriz ? { ...baseOptions, indexAxis: "y" } : baseOptions;
            }
            return {
              key: s.key,
              label: s.label,
              checked: s.checked,
              icon: icons[s.key],
            data: raw,
            columns: columns[s.key],
            chartData: chartBuilders[s.key](raw),
            chartOptions: opts,
          };
        });
    },
  },
  mounted() {
    this.fetchAll();
    this.preloadLogo();
  },
  methods: {
    preloadLogo() {
      const img = new Image();
      img.src = "https://res.cloudinary.com/dorj3mvvr/image/upload/v1783609693/logos/logotaller01.png";
    },
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
        const [avgRes, mecRes, motoRes, servRes, diasRes, cliRes, estadosRes, rendRes, ganRes, tasaRes] = await Promise.all([
          api.get("/reports/tiempo-promedio-reparacion", { params: dp }),
          api.get("/reports/mecanicos/mas-servicios", { params: dp }),
          api.get("/reports/motos/mas-atendidas", { params: dp }),
          api.get("/reports/servicios/top-descripciones", { params: dp }),
          api.get("/reports/ordenes/por-dia-semana"),
          api.get("/reports/clientes/recurrentes", { params: dp }),
          api.get("/reports/ordenes/completadas-canceladas", { params: dp }),
          api.get("/reports/mecanicos/rendimiento", { params: dp }),
          api.get("/reports/ganancias"),
          api.get("/bcv/tasa"),
        ]);
        this.avgMinutes = avgRes.data.minutos_promedio;
        this.topMecanicos = mecRes.data;
        this.topMotos = motoRes.data;
        this.topServicios = servRes.data;
        this.diasSemana = diasRes.data;
        this.topClientes = cliRes.data;
        this.estadosOrdenes = estadosRes.data;
        this.rendimientoMecanicos = rendRes.data;
        this.ganancias = ganRes.data;
        this.tasaBcv = tasaRes.data.tasa;
        this.tasaInput = tasaRes.data.tasa ? String(tasaRes.data.tasa) : "";
      } catch (err) {
        console.error("Error al cargar reportes", err);
      } finally {
        this.loading = false;
      }
    },
    async saveTasa() {
      const val = parseFloat(this.tasaInput);
      if (isNaN(val) || val <= 0) return;
      try {
        await api.put("/bcv/tasa-manual", { tasa: val });
        this.tasaBcv = val;
        this.editTasa = false;
      } catch (err) {
        console.error("Error al guardar tasa", err);
      }
    },
    clearFilters() {
      this.fechaInicio = "";
      this.fechaFin = "";
      this.fetchAll();
    },
    async printReport() {
      this.showPdfMenu = false;
      const num = this.pdfNumber;
      const next = this.pdfCounter + 1;
      localStorage.setItem("pdfCounter", String(next));
      this.pdfCounter = next;

      // Preload logo before print
      await new Promise((resolve) => {
        const img = new Image();
        img.onload = resolve;
        img.onerror = resolve;
        img.src = "https://res.cloudinary.com/dorj3mvvr/image/upload/v1783609693/logos/logotaller01.png";
      });

      // Set page title so "Save as PDF" uses filename "Reporte 0000005.pdf"
      const orig = document.title;
      document.title = "Reporte " + num;
      const restore = () => {
        document.title = orig;
        window.removeEventListener("afterprint", restore);
      };
      window.addEventListener("afterprint", restore);

      setTimeout(() => window.print(), 200);
    },
    capitalize(s) {
      if (!s) return "";
      return s.replace(/\b\w/g, (c) => c.toUpperCase());
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
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 12px;
}
.reports-header h1 { font-size: 1.8rem; color: #1a1a1a; font-weight: 800; }
.print-header { display: none; }
.reports-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
  justify-content: flex-end;
  flex-wrap: wrap;
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
/* Tasa BCV chip */
.tasa-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fff7e6;
  border: 1.5px solid #ffaa00;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 700;
  color: #1a1a1a;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.12s;
}
.tasa-chip:hover { background: #ffedcc; }
.tasa-chip-label { color: #b45309; font-weight: 700; }
.tasa-chip-value { color: #1a1a1a; }
.tasa-editor {
  display: flex;
  align-items: center;
  gap: 6px;
}
html.dark .tasa-chip { background: #334155; border-color: var(--color-primary); }
html.dark .tasa-chip:hover { background: #3b4a63; }
html.dark .tasa-chip-label { color: #fbbf24; }
html.dark .tasa-chip-value { color: var(--text-default); }
.loading-state { text-align: center; padding: 60px; color: #64748b; font-size: 1rem; }

/* PDF dropdown */
.pdf-dropdown {
  position: relative;
}
.btn-pdf {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #1a1a1a;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
.btn-pdf:hover { background: #333; }
.pdf-dropdown-content {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 6px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  padding: 12px;
  width: 260px;
  z-index: 100;
}
.pdf-dropdown-header {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: #94a3b8;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f1f5f9;
  text-align: center;
}
.pdf-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #1a1a1a;
  cursor: pointer;
  padding: 5px 0;
  border-radius: 5px;
  transition: background 0.1s;
}
.pdf-check input {
  width: 16px;
  flex-shrink: 0;
}
.pdf-check span {
  flex: 1;
  text-align: center;
}
.pdf-check:hover { background: #f8fafc; }
.pdf-check input { accent-color: #ffaa00; }
.pdf-dropdown-actions {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
}
.btn-pdf-generate {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: #ffaa00;
  color: #1a1a1a;
  border: none;
  border-radius: 8px;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}
.btn-pdf-generate:hover { background: #e69900; }

/* Highlight card */
.highlight-card {
  text-align: center;
  padding: 32px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #fff7e6, #fff3d6);
  border: 1.5px solid #ffaa00;
}
.highlight-value { font-size: 3rem; font-weight: 800; color: #1a1a1a; }
.highlight-label { font-size: 1rem; color: #64748b; margin-top: 4px; font-weight: 600; }

/* Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
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
  margin-bottom: 12px;
  color: #ffaa00;
}
.report-card-header h3 { font-size: 1rem; font-weight: 700; color: #1a1a1a; }
.chart-wrapper { position: relative; height: 200px; }
.chart-card .report-card-header { margin-bottom: 8px; }
.report-empty { text-align: center; padding: 40px; color: #94a3b8; font-size: 0.85rem; }

/* Print table (hidden on screen) */
.print-table-wrapper { display: none; }
</style>

<style>
@page {
  margin: 8mm;
}

@media print {
  .app-header,
  .app-nav,
  .logo,
  .nav-icon-btn,
  .user-info,
  .btn-logout,
  .notif-wrapper,
  .notif-bell,
  .notif-badge,
  .notif-dropdown,
  .admin-panel .welcome-section,
  .admin-panel .dashboard-grid,
  .chat-overlay {
    display: none !important;
  }

  .no-print,
  .screen-only,
  .highlight-card,
  .loading-state {
    display: none !important;
  }

  .reports-page {
    padding: 0 !important;
    max-width: 100% !important;
  }

  .reports-header {
    display: block !important;
    margin-bottom: 12px !important;
  }

  .reports-header h1,
  .reports-header .page-subtitle {
    display: none !important;
  }

  .print-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
  }

  .print-header-spacer {
    width: 55px;
    height: 1px;
  }

  .print-title-text {
    text-align: center !important;
  }

  .print-title {
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    color: #1a1a1a !important;
  }

  .print-company {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    margin-top: 2px !important;
  }

  .print-logo {
    width: 55px !important;
    height: auto !important;
  }

  .reports-grid {
    display: block !important;
  }

  .report-card {
    break-inside: avoid !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 0 !important;
    margin-bottom: 6px !important;
    border-radius: 0 !important;
  }

  .report-card-header {
    margin-bottom: 4px !important;
  }

  .report-card-header svg {
    display: none !important;
  }

  .report-card-header h3 {
    font-size: 0.8rem !important;
  }

  .print-table-wrapper {
    display: block !important;
  }

  .print-hidden {
    display: none !important;
  }

  .print-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10px;
  }

  .print-table th {
    text-align: left;
    padding: 3px 6px;
    background: #f1f5f9;
    font-weight: 700;
    color: #1a1a1a;
    border-bottom: 2px solid #d1d5db;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  .print-table td {
    padding: 2px 6px;
    border-bottom: 1px solid #e2e8f0;
    color: #1a1a1a;
  }

  .app-main {
    padding: 0 !important;
  }
}
</style>