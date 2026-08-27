<template>
  <div class="admin-panel">
    <div class="welcome-section">
      <div class="header-content">
        <h1>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px; vertical-align: middle;"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          Panel de Administración
        </h1>
      </div>
    </div>

    <div class="dashboard-grid">
      <router-link to="/admin/users" class="dash-card">
        <div class="dash-icon-wrap">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="dash-info">
          <h2>Usuarios</h2>
          <span class="dash-badge">Admin</span>
        </div>
        <p>Gestionar mecánicos y clientes del taller</p>
        <div class="dash-footer">
          <span>Ir a Usuarios</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </div>
      </router-link>

      <router-link to="/admin/catalog" class="dash-card">
        <div class="dash-icon-wrap">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 4h8v16H3z"/>
            <path d="M13 4h8v16H13z"/>
            <path d="M11 4v16"/>
            <line x1="4" y1="8" x2="10" y2="8"/>
            <line x1="4" y1="11" x2="10" y2="11"/>
            <line x1="4" y1="14" x2="10" y2="14"/>
            <line x1="14" y1="8" x2="20" y2="8"/>
            <line x1="14" y1="11" x2="20" y2="11"/>
            <line x1="14" y1="14" x2="20" y2="14"/>
          </svg>
        </div>
        <div class="dash-info">
          <h2>Catálogo</h2>
          <span class="dash-badge">Admin</span>
        </div>
        <p>Administrar modelos y marcas de motos</p>
        <div class="dash-footer">
          <span>Ir al Catálogo</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </div>
      </router-link>

      <router-link to="/admin/service-orders" class="dash-card">
        <div class="dash-icon-wrap">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
            <path d="M9 14l2 2 4-4"/>
          </svg>
        </div>
        <div class="dash-info">
          <h2>Órdenes</h2>
          <span class="dash-badge">Admin</span>
        </div>
        <p>Crear, gestionar y dar seguimiento</p>
        <div class="dash-footer">
          <span>Ir a Órdenes</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </div>
      </router-link>

      <router-link to="/admin/reports" class="dash-card">
        <div class="dash-icon-wrap">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 20h16"/>
            <path d="M4 20V4"/>
            <path d="M8 14V8"/>
            <path d="M12 14v-4"/>
            <path d="M16 14v-6"/>
            <path d="M20 14V6"/>
          </svg>
        </div>
        <div class="dash-info">
          <h2>Reportes</h2>
          <span class="dash-badge">Admin</span>
        </div>
        <p>Estadísticas, rendimiento y métricas del taller</p>
        <div class="dash-footer">
          <span>Ir a Reportes</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </div>
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
  height: calc(100vh - 92px);
  display: flex;
  flex-direction: column;
  max-width: 1400px;
  margin: 0 auto;
  padding: 8px 40px 12px;
  animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.welcome-section h1 {
  font-size: 1.6rem;
  color: #1a1a1a;
  margin-bottom: 8px;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.page-subtitle {
  color: #666;
  margin-top: 5px;
  margin-left: 48px;
  font-size: 1.05rem;
}
.dashboard-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 16px;
}
.dash-card {
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px 28px;
  text-decoration: none;
  color: inherit;
  transition: all 0.25s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  overflow: hidden;
}
.dash-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #ffaa00;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}
.dash-card:hover::before {
  transform: scaleX(1);
}
.dash-card:hover {
  border-color: #ffaa00;
  box-shadow: 0 8px 24px rgba(255, 170, 0, 0.12);
  transform: translateY(-4px);
}
.dash-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #fff7e6;
  color: #ffaa00;
  display: flex;
  align-items: center;
  justify-content: center;
}
.dash-icon-wrap svg { width: 28px; height: 28px; }
.dash-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dash-info h2 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #1a1a1a;
}
.dash-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #ffaa00;
  color: #1a1a1a;
  padding: 2px 8px;
  border-radius: 20px;
}
.dash-card p {
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.4;
  margin: 0;
}
.dash-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #ffaa00;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
}
.dash-footer svg {
  transition: transform 0.2s ease;
}
.dash-card:hover .dash-footer svg {
  transform: translateX(4px);
}
/* ===== MOBILE / PWA native feel ===== */
@media (max-width: 768px) {
  .admin-panel {
    padding: 10px 12px 80px;
    height: auto;
    min-height: auto;
  }
  .welcome-section h1 {
    font-size: 1.3rem;
  }
  .page-subtitle {
    margin-left: 0;
    font-size: 0.9rem;
    display: none;
  }
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 8px;
    flex: none;
    height: auto;
  }
  .dash-card {
    padding: 16px 14px 12px;
    border-radius: 14px;
    gap: 8px;
    justify-content: flex-start;
  }
  .dash-icon-wrap {
    width: 40px;
    height: 40px;
    border-radius: 10px;
  }
  .dash-icon-wrap svg {
    width: 24px;
    height: 24px;
  }
  .dash-info {
    gap: 6px;
  }
  .dash-info h2 {
    font-size: 1.2rem;
    font-weight: 800;
  }
  .dash-badge {
    font-size: 0.6rem;
    padding: 1px 6px;
  }
  .dash-card p {
    font-size: 0.88rem;
    line-height: 1.3;
    margin: 0;
  }
  .dash-footer {
    font-size: 0.8rem;
    padding-top: 6px;
    margin-top: 0;
    border-top: none;
  }
}
html.dark .admin-panel .dash-card {
  background: #1a1f2e;
  border-color: #1e293b;
}
html.dark .admin-panel .dash-info h2 {
  color: #e2e8f0;
}
html.dark .admin-panel .dash-card p {
  color: #94a3b8;
}
html.dark .admin-panel .dash-footer {
  border-top-color: #1e293b;
}
</style>
