<template>
  <div class="tracker-container">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Consultando historial...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <h2>Información no disponible</h2>
      <p>El código QR no es válido o la moto no tiene servicios registrados.</p>
    </div>
    <div v-else class="tracker-card">
      <h1 class="tracker-title">Todomotortaller</h1>
      <p class="tracker-subtitle">Historial de Servicios</p>

      <div class="order-info">
        <div class="info-row"><span>Moto:</span> {{ motoInfo.marca }} {{ motoInfo.modelo }} ({{ motoInfo.placa }})</div>
        <div class="info-row"><span>Cliente:</span> {{ motoInfo.cliente }}</div>
      </div>

      <div v-if="services.length === 0" class="empty-state">No hay servicios completados registrados.</div>

      <div v-else class="service-timeline">
        <div v-for="(s, i) in services" :key="i" class="service-item">
          <div class="service-dot"></div>
          <div class="service-content">
            <div class="service-date">{{ formatDate(s.fecha_cierre || s.fecha_creacion) }}</div>
            <div class="service-desc">{{ s.descripcion }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "TrackerView",
  data() {
    return {
      motoInfo: { marca: "", modelo: "", placa: "", cliente: "" },
      services: [],
      loading: true,
      error: false,
    };
  },
  mounted() {
    this.fetchData();
    this._onNotif = () => this.fetchData();
    window.addEventListener("notification-new", this._onNotif);
  },
  beforeUnmount() {
    if (this._onNotif) {
      window.removeEventListener("notification-new", this._onNotif);
    }
  },
  methods: {
    async fetchData() {
      const motoClienteId = this.$route.params.motoClienteId || this.$route.params.id;
      if (!motoClienteId) { this.error = true; this.loading = false; return; }
      try {
        if (this.$route.params.id && !this.$route.params.motoClienteId) {
          const { data: order } = await api.get(`/service-orders/${motoClienteId}/tracker`);
          this.motoInfo = {
            marca: order.moto_marca,
            modelo: order.moto_modelo,
            placa: order.moto_placa,
            cliente: order.cliente_nombre,
          };
          await this.loadHistory(order.moto_cliente_id);
        } else {
          await this.loadHistory(motoClienteId);
        }
      } catch {
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
    async loadHistory(motoClienteId) {
      const { data } = await api.get(`/service-orders/moto/${motoClienteId}/history`);
      const completadas = data.filter(s => s.estado === "completada").reverse();
      this.services = completadas;
      if (!this.motoInfo.marca && completadas.length > 0) {
        this.motoInfo = {
          marca: completadas[0].moto_marca,
          modelo: completadas[0].moto_modelo,
          placa: completadas[0].moto_placa,
          cliente: completadas[0].cliente_nombre,
        };
      }
    },
    formatDate(dt) {
      if (!dt) return "-";
      let str = String(dt);
      if (!str.endsWith("Z") && !str.includes("+") && !str.includes("-", 10)) {
        str += "Z";
      }
      const d = new Date(str);
      if (isNaN(d.getTime())) return String(dt);
      return d.toLocaleDateString("es-VE", { year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: true });
    },
  },
};
</script>

<style scoped>
.tracker-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 20px;
}
.tracker-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.tracker-title {
  text-align: center;
  color: #ffaa00;
  font-size: 1.8rem;
  margin-bottom: 4px;
}
.tracker-subtitle {
  text-align: center;
  color: #64748b;
  font-size: 0.95rem;
  margin-bottom: 24px;
}
.order-info {
  margin-bottom: 24px;
}
.info-row {
  padding: 6px 0;
  font-size: 0.9rem;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
}
.info-row span {
  color: #64748b;
  margin-right: 6px;
}
.service-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  padding-left: 20px;
}
.service-timeline::before {
  content: "";
  position: absolute;
  left: 7px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: #e2e8f0;
}
.service-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 12px 0;
  position: relative;
}
.service-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #ffaa00;
  flex-shrink: 0;
  margin-top: 2px;
  z-index: 1;
}
.service-content {
  flex: 1;
}
.service-date {
  font-size: 0.78rem;
  font-weight: 700;
  color: #ffaa00;
  text-transform: uppercase;
  margin-bottom: 2px;
}
.service-desc {
  font-size: 0.9rem;
  color: #334155;
  line-height: 1.4;
}
.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #94a3b8;
  font-size: 0.9rem;
}
.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}
.error-state h2 {
  color: #dc2626;
  margin-bottom: 8px;
}
</style>
