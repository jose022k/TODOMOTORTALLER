<template>
  <div class="admin-panel">
    <h1>Panel de Administración</h1>
    <p class="subtitle">Bienvenido, {{ authStore.user?.nombre }}</p>

    <div class="dashboard-grid">
      <router-link to="/admin/users" class="dash-card">
        <div class="dash-icon">🔧</div>
        <h2>Gestionar Mecánicos</h2>
        <p>Crear, editar, desactivar mecánicos</p>
      </router-link>

      <router-link to="/admin/users" class="dash-card">
        <div class="dash-icon">👥</div>
        <h2>Gestionar Clientes</h2>
        <p>Ver, editar, desactivar clientes</p>
      </router-link>

      <router-link to="/admin/catalog" class="dash-card">
        <div class="dash-icon">🏍️</div>
        <h2>Catálogo de Motos</h2>
        <p>Administrar modelos y marcas</p>
      </router-link>

      <router-link to="/admin/service-orders" class="dash-card">
        <div class="dash-icon">📋</div>
        <h2>Órdenes de Servicio</h2>
        <p>Crear, gestionar y dar seguimiento</p>
      </router-link>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";

export default {
  name: "AdminPanel",
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
};
</script>

<style scoped>
.admin-panel {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}
.admin-panel h1 {
  font-size: 2rem;
  color: #1a1a1a;
  margin-bottom: 6px;
}
.subtitle {
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 40px;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
.dash-card {
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  padding: 28px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  display: block;
}
.dash-card:hover {
  border-color: #ffaa00;
  box-shadow: 0 8px 20px rgba(255,170,0,0.12);
  transform: translateY(-3px);
}
.dash-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}
.dash-card h2 {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 6px;
}
.dash-card p {
  font-size: 0.85rem;
  color: #64748b;
}
</style>
