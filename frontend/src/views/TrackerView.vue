<template>
  <div class="tracker-container">
    <div v-if="loading" class="loading-state">Consultando orden...</div>
    <div v-else-if="error" class="error-state">
      <h2>Orden no encontrada</h2>
      <p>El código QR no es válido o la orden ha sido eliminada.</p>
    </div>
    <div v-else class="tracker-card">
      <h1 class="tracker-title">Todomotortaller</h1>
      <p class="tracker-subtitle">Seguimiento de Servicio</p>

      <div class="order-info">
        <div class="info-row"><strong>Orden #{{ order.id }}</strong></div>
        <div class="info-row"><span>Moto:</span> {{ order.moto_marca }} {{ order.moto_modelo }} ({{ order.moto_placa }})</div>
        <div class="info-row"><span>Cliente:</span> {{ order.cliente_nombre }}</div>
        <div class="info-row"><span>Mecánico:</span> {{ order.mecanico_nombre }}</div>
        <div class="info-row"><span>Descripción:</span> {{ order.descripcion }}</div>
      </div>

      <div class="progress-tracker">
        <div class="progress-step" :class="{ completed: pasoCompletado('pendiente'), active: order.estado === 'pendiente', cancelled: order.estado === 'cancelada' }">
          <div class="step-icon">1</div>
          <div class="step-label">Recibida</div>
        </div>
        <div class="progress-line" :class="{ completed: pasoCompletado('en_proceso'), cancelled: order.estado === 'cancelada' }"></div>
        <div class="progress-step" :class="{ completed: pasoCompletado('en_proceso'), active: order.estado === 'en_proceso', cancelled: order.estado === 'cancelada' }">
          <div class="step-icon">2</div>
          <div class="step-label">En Proceso</div>
        </div>
        <div class="progress-line" :class="{ completed: order.estado === 'completada', cancelled: order.estado === 'cancelada' }"></div>
        <div class="progress-step" :class="{ completed: order.estado === 'completada', cancelled: order.estado === 'cancelada' }">
          <div class="step-icon" v-if="order.estado !== 'cancelada'">3</div>
          <div class="step-icon cancelled-icon" v-else>✕</div>
          <div class="step-label">{{ order.estado === 'cancelada' ? 'Cancelada' : 'Completada' }}</div>
        </div>
      </div>

      <div class="order-dates">
        <div class="date-item">
          <span class="date-label">Creada:</span>
          <span>{{ formatDate(order.fecha_creacion) }}</span>
        </div>
        <div class="date-item" v-if="order.fecha_cierre">
          <span class="date-label">Finalizada:</span>
          <span>{{ formatDate(order.fecha_cierre) }}</span>
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
      order: null,
      loading: true,
      error: false,
    };
  },
  mounted() {
    this.fetchTracker();
  },
  methods: {
    async fetchTracker() {
      const id = this.$route.params.id;
      try {
        const { data } = await api.get(`/service-orders/${id}/tracker`);
        this.order = data;
      } catch {
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
    pasoCompletado(estado) {
      const orden = ["pendiente", "en_proceso", "completada"];
      return orden.indexOf(this.order.estado) > orden.indexOf(estado);
    },
    formatDate(dt) {
      if (!dt) return "-";
      return new Date(dt).toLocaleString("es-VE");
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
.progress-tracker {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 28px 0;
}
.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1rem;
  transition: all 0.3s;
}
.progress-step.active .step-icon {
  background: #ffaa00;
  color: #1a1a1a;
  box-shadow: 0 0 0 4px rgba(255,170,0,0.2);
}
.progress-step.completed .step-icon {
  background: #16a34a;
  color: #fff;
}
.progress-step.cancelled .step-icon {
  background: #ef4444;
  color: #fff;
}
.cancelled-icon {
  font-size: 1.1rem;
}
.step-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}
.progress-step.active .step-label {
  color: #ffaa00;
}
.progress-step.completed .step-label {
  color: #16a34a;
}
.progress-step.cancelled .step-label {
  color: #ef4444;
}
.progress-line {
  width: 60px;
  height: 3px;
  background: #e2e8f0;
  margin: 0 8px;
  margin-bottom: 24px;
  border-radius: 2px;
  transition: background 0.3s;
}
.progress-line.completed {
  background: #16a34a;
}
.progress-line.cancelled {
  background: #ef4444;
}
.order-dates {
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  font-size: 0.85rem;
  color: #64748b;
}
.date-label {
  font-weight: 600;
  margin-right: 4px;
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
