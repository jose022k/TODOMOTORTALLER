<template>
  <div id="app">
    <header class="app-header">
      <router-link :to="homeRoute" class="logo">Todomotortaller</router-link>
      <nav class="app-nav">
        <template v-if="!authStore.isAuthenticated || !authStore.isAdmin">
          <router-link v-if="!authStore.isMecanico && !authStore.isCliente" to="/">Home</router-link>
          <router-link v-if="!authStore.isMecanico && !authStore.isCliente" to="/about">About</router-link>
        </template>
        <template v-if="authStore.isAuthenticated">
          <router-link v-if="authStore.isAdmin" to="/admin" class="nav-icon-btn" data-tooltip="Panel Admin">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </router-link>
          <router-link v-if="authStore.isAdmin" to="/admin/users" class="nav-icon-btn" data-tooltip="Gestionar Usuarios">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </router-link>
          <router-link v-if="authStore.isAdmin" to="/admin/catalog" class="nav-icon-btn" data-tooltip="Catálogo de Motos">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4h8v16H3z"/><path d="M13 4h8v16H13z"/><path d="M11 4v16"/><line x1="4" y1="8" x2="10" y2="8"/><line x1="4" y1="11" x2="10" y2="11"/><line x1="4" y1="14" x2="10" y2="14"/><line x1="14" y1="8" x2="20" y2="8"/><line x1="14" y1="11" x2="20" y2="11"/><line x1="14" y1="14" x2="20" y2="14"/></svg>
          </router-link>
          <router-link v-if="authStore.isAdmin" to="/admin/service-orders" class="nav-icon-btn" data-tooltip="Órdenes de Servicio">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M9 14l2 2 4-4"/></svg>
          </router-link>
          <router-link v-if="authStore.isAdmin" to="/admin/reports" class="nav-icon-btn" data-tooltip="Reportes">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16"/><path d="M4 20V4"/><path d="M8 14V8"/><path d="M12 14v-4"/><path d="M16 14v-6"/><path d="M20 14V6"/></svg>
          </router-link>
          <router-link v-if="authStore.isMecanico" to="/mecanico/orders" class="nav-icon-btn" data-tooltip="Mis Órdenes">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 14l2 2 4-4"/></svg>
          </router-link>
          <router-link v-if="authStore.isCliente" to="/cliente/orders" class="nav-icon-btn" data-tooltip="Mi Panel">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </router-link>
          <NotificationsDropdown />
          <span class="user-info">{{ authStore.user?.nombre }}</span>
          <button class="btn-logout" @click="handleLogout">Cerrar Sesión</button>
        </template>
        <template v-else>
          <router-link v-if="$route.path !== '/login'" to="/login">
            Iniciar Sesión
          </router-link>
        </template>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import NotificationsDropdown from "@/components/NotificationsDropdown.vue";
import { setupPush } from "@/services/push";

export default {
  name: "App",
  components: { NotificationsDropdown },
  setup() {
    const authStore = useAuthStore();
    if (authStore.isAuthenticated && !authStore.user) {
      authStore.fetchUser();
    }
    return { authStore };
  },
  watch: {
    "authStore.isAuthenticated": {
      immediate: true,
      handler(val) {
        if (val) {
          setTimeout(() => setupPush(), 1000);
        }
      },
    },
  },
  computed: {
    homeRoute() {
      if (!this.authStore.isAuthenticated) return "/";
      if (this.authStore.isAdmin) return "/admin";
      if (this.authStore.isMecanico) return "/mecanico/orders";
      if (this.authStore.isCliente) return "/cliente/orders";
      return "/";
    },
  },
  methods: {
    handleLogout() {
      this.authStore.logout();
      this.$router.push("/login");
    },
  },
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #1a1a1a;
  min-height: 100vh;
}
.app-header {
  background-color: #1a1a1a;
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  color: #ffaa00;
  font-size: 20px;
  font-weight: bold;
  text-decoration: none;
}
.app-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}
.app-nav a {
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}
.app-nav a:hover {
  color: #ffaa00;
}
.app-nav a.router-link-exact-active {
  color: #ffaa00;
}
.nav-icon-btn {
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s;
  position: relative;
}
.nav-icon-btn:hover {
  background: rgba(255, 170, 0, 0.15);
}
.nav-icon-btn:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  background: #1a1a1a;
  color: #fff;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.nav-icon-btn.router-link-exact-active svg {
  color: #ffaa00;
}
.user-info {
  color: #b0b5b9;
  font-size: 14px;
}
.btn-logout {
  background: transparent;
  border: 1px solid #b0b5b9;
  color: #b0b5b9;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.btn-logout:hover {
  border-color: #ffaa00;
  color: #ffaa00;
}
.app-main {
  padding: 12px 20px;
}
</style>
