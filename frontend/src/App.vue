<template>
  <div id="app" :class="{ 'pwa-mode': showMobileNav }">
    <!-- HEADER MOBILE -->
    <header v-if="showMobileNav" class="pwa-header">
      <div class="pwa-header-title">
        <span>Todomotortaller</span>
      </div>
    </header>

    <!-- HEADER NORMAL: navegador web desktop -->
    <header v-else class="app-header">
      <router-link :to="homeRoute" class="logo">Todomotortaller</router-link>
      <nav class="app-nav">
        <transition name="nav-fade" mode="out-in">
          <div v-if="authStore.isAuthenticated" key="auth" class="nav-group">
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
            <SettingsDropdown @theme-change="onThemeChange" />
            <button class="btn-logout" @click="handleLogout" :disabled="loggingOut">{{ loggingOut ? "Cerrando sesión..." : "Cerrar Sesión" }}</button>
          </div>
          <div v-else key="guest" class="nav-group">
            <router-link v-if="!authStore.isMecanico && !authStore.isCliente" to="/workshop" class="nav-text-link">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/></svg>
              Taller
            </router-link>
            <router-link v-if="!authStore.isMecanico && !authStore.isCliente" to="/location" class="nav-text-link">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              Ubicación
            </router-link>
            <router-link v-if="$route.path !== '/login'" to="/login" class="nav-text-link">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
              Iniciar Sesión
            </router-link>
            <button class="theme-toggle" @click="toggleTheme" :title="isDark ? 'Modo claro' : 'Modo oscuro'" v-html="isDark ? sunIcon : moonIcon"></button>
          </div>
        </transition>
      </nav>
    </header>

    <main class="app-main" :class="{ 'pwa-main': showMobileNav }" ref="mainContent" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
      <router-view v-slot="{ Component }">
        <transition :name="showMobileNav && isSwiping ? 'slide-' + swipeDirection : 'page-fade'" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </transition>
      </router-view>
    </main>

    <!-- BOTTOM NAV MOBILE: paginas publicas -->
    <nav v-if="showMobileNav && !authStore.isAuthenticated && isPublicPage" class="pwa-bottom-nav pwa-bottom-nav--centered">
      <router-link to="/workshop" class="pwa-nav-item" :class="{ active: $route.path === '/workshop' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/></svg>
        <span>Taller</span>
      </router-link>
      <router-link to="/location" class="pwa-nav-item" :class="{ active: $route.path === '/location' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        <span>Ubicación</span>
      </router-link>
      <router-link v-if="$route.path !== '/login'" to="/login" class="pwa-nav-item" :class="{ active: $route.path === '/login' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
        <span>Iniciar</span>
      </router-link>
      <router-link v-if="$route.path === '/login'" to="/register/cliente" class="pwa-nav-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
        <span>Registrar</span>
      </router-link>
      <button class="pwa-nav-item" @click="toggleTheme">
        <span v-html="isDark ? sunIcon : moonIcon"></span>
        <span>{{ isDark ? 'Claro' : 'Oscuro' }}</span>
      </button>
    </nav>

    <!-- BOTTOM NAV MOBILE: ADMIN -->
    <nav v-if="showMobileNav && authStore.isAuthenticated && authStore.isAdmin" class="pwa-bottom-nav">
      <router-link to="/admin" class="pwa-nav-item" :class="{ active: $route.path === '/admin' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        <span>Panel</span>
      </router-link>
      <router-link to="/admin/service-orders" class="pwa-nav-item" :class="{ active: $route.path === '/admin/service-orders' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M9 14l2 2 4-4"/></svg>
        <span>Órdenes</span>
      </router-link>
      <router-link to="/admin/reports" class="pwa-nav-item" :class="{ active: $route.path === '/admin/reports' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16"/><path d="M4 20V4"/><path d="M8 14V8"/><path d="M12 14v-4"/><path d="M16 14v-6"/><path d="M20 14V6"/></svg>
        <span>Reportes</span>
      </router-link>
      <router-link to="/admin/catalog" class="pwa-nav-item" :class="{ active: $route.path === '/admin/catalog' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4h8v16H3z"/><path d="M13 4h8v16H13z"/><path d="M11 4v16"/></svg>
        <span>Catálogo</span>
      </router-link>
      <router-link to="/admin/users" class="pwa-nav-item" :class="{ active: $route.path === '/admin/users' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        <span>Usuarios</span>
      </router-link>
      <router-link to="/notifications" class="pwa-nav-item" :class="{ active: $route.path === '/notifications' }">
        <span class="notif-badge-wrap">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </span>
        <span>Alertas</span>
      </router-link>
      <div class="pwa-nav-item pwa-nav-settings">
        <SettingsDropdown :above="true" @theme-change="onThemeChange" />
        <span>Ajustes</span>
      </div>
      <button class="pwa-nav-item pwa-nav-logout" @click="handleLogout">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        <span>Salir</span>
      </button>
    </nav>

    <!-- BOTTOM NAV MOBILE: MECANICO -->
    <nav v-if="showMobileNav && authStore.isAuthenticated && authStore.isMecanico" class="pwa-bottom-nav">
      <router-link to="/mecanico/orders" class="pwa-nav-item" :class="{ active: $route.path === '/mecanico/orders' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 14l2 2 4-4"/></svg>
        <span>Mis Órdenes</span>
      </router-link>
      <router-link to="/notifications" class="pwa-nav-item" :class="{ active: $route.path === '/notifications' }">
        <span class="notif-badge-wrap">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </span>
        <span>Alertas</span>
      </router-link>
      <div class="pwa-nav-item pwa-nav-settings">
        <SettingsDropdown :above="true" @theme-change="onThemeChange" />
        <span>Ajustes</span>
      </div>
      <button class="pwa-nav-item pwa-nav-logout" @click="handleLogout">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        <span>Salir</span>
      </button>
    </nav>

    <!-- BOTTOM NAV MOBILE: CLIENTE -->
    <nav v-if="showMobileNav && authStore.isAuthenticated && authStore.isCliente" class="pwa-bottom-nav">
      <router-link to="/cliente/orders" class="pwa-nav-item" :class="{ active: $route.path === '/cliente/orders' }">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        <span>Mi Panel</span>
      </router-link>
      <router-link to="/notifications" class="pwa-nav-item" :class="{ active: $route.path === '/notifications' }">
        <span class="notif-badge-wrap">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </span>
        <span>Alertas</span>
      </router-link>
      <div class="pwa-nav-item pwa-nav-settings">
        <SettingsDropdown :above="true" @theme-change="onThemeChange" />
        <span>Ajustes</span>
      </div>
      <button class="pwa-nav-item pwa-nav-logout" @click="handleLogout">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        <span>Salir</span>
      </button>
    </nav>

    <ConfirmModal
      :visible="showLogoutModal"
      title="Cerrar Sesión"
      message="¿Deseas cerrar sesión?"
      confirmText="Cerrar Sesión"
      cancelText="Cancelar"
      @confirm="confirmLogout"
      @cancel="showLogoutModal = false"
    />
    <LoadingOverlay :visible="loggingOut" text="Cerrando sesión..." />
    <NotificationNative />
    <SplashScreen />
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import NotificationsDropdown from "@/components/NotificationsDropdown.vue";
import SettingsDropdown from "@/components/SettingsDropdown.vue";
import ConfirmModal from "@/components/ConfirmModal.vue";
import LoadingOverlay from "@/components/LoadingOverlay.vue";
import NotificationNative from "@/components/NotificationNative.vue";
import SplashScreen from "@/components/SplashScreen.vue";
import { setupPush } from "@/services/push";
import orderSocket from "@/services/orderSocket";
import api from "@/services/api";

export default {
  name: "App",
  components: { NotificationsDropdown, SettingsDropdown, ConfirmModal, LoadingOverlay, NotificationNative, SplashScreen },
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
  watch: {
    $route() {
      if (this.isSwiping) {
        setTimeout(() => { this.isSwiping = false; }, 350);
      }
    },
    "authStore.isAuthenticated": {
      immediate: true,
      handler(val) {
        if (val) {
          orderSocket.enable();
          setTimeout(() => setupPush(), 1000);
          this.fetchUnreadCount();
          clearInterval(this.unreadPollInterval);
          this.unreadPollInterval = setInterval(() => this.fetchUnreadCount(), 30000);
        } else {
          clearInterval(this.unreadPollInterval);
          this.unreadCount = 0;
        }
      },
    },
  },
  async created() {
    if (this.authStore.isAuthenticated && !this.authStore.user) {
      this.authStore.fetchUser();
    }
  },
  beforeUnmount() {
    clearInterval(this.unreadPollInterval);
  },
  computed: {
    homeRoute() {
      if (!this.authStore.isAuthenticated) return "/";
      if (this.authStore.isAdmin) return "/admin";
      if (this.authStore.isMecanico) return "/mecanico/orders";
      if (this.authStore.isCliente) return "/cliente/orders";
      return "/";
    },
    isPwa() {
      try {
        if (typeof window === "undefined") return false;
        const mq = window.matchMedia && window.matchMedia("(display-mode: standalone)").matches;
        const ios = window.navigator && window.navigator.standalone === true;
        return mq || ios;
      } catch (e) {
        return false;
      }
    },
    isMobile() {
      if (typeof window === "undefined") return false;
      return window.innerWidth <= 768;
    },
    showMobileNav() {
      return this.isPwa || this.isMobile;
    },
    isPublicPage() {
      try {
        const publicPaths = ["/login", "/register/cliente", "/workshop", "/location"];
        return publicPaths.includes(this.$route.path);
      } catch (e) {
        return false;
      }
    },
    swipePages() {
      if (this.authStore.isAdmin) {
        return ["/admin", "/admin/service-orders", "/admin/reports", "/admin/catalog", "/admin/users", "/notifications"];
      }
      if (this.authStore.isMecanico) {
        return ["/mecanico/orders", "/notifications"];
      }
      if (this.authStore.isCliente) {
        return ["/cliente/orders", "/notifications"];
      }
      return [];
    },
    currentSwipeIndex() {
      return this.swipePages.indexOf(this.$route.path);
    },
  },
  data() {
    return {
      showLogoutModal: false,
      loggingOut: false,
      unreadCount: 0,
      unreadPollInterval: null,
      isDark: document.documentElement.classList.contains("dark"),
      sunIcon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
      moonIcon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
      touchStartX: 0,
      touchStartY: 0,
      touchStartTime: 0,
      isSwiping: false,
      swipeDirection: "left",
    };
  },
  methods: {
    onThemeChange(dark) {
      this.isDark = dark;
      document.documentElement.classList.toggle("dark", dark);
    },
    toggleTheme() {
      this.isDark = !this.isDark;
      document.documentElement.classList.toggle("dark", this.isDark);
    },
    handleLogout() {
      this.showLogoutModal = true;
    },
    confirmLogout() {
      this.showLogoutModal = false;
      this.loggingOut = true;
      setTimeout(() => {
        this.authStore.logout();
        this.loggingOut = false;
        this.unreadCount = 0;
        this.$router.push("/login");
      }, 3000);
    },
    async fetchUnreadCount() {
      try {
        const { data } = await api.get("/notifications/unread-count");
        this.unreadCount = data.count;
      } catch { /* silent */ }
    },
    onTouchStart(e) {
      if (!this.showMobileNav || this.swipePages.length < 2) return;
      this.touchStartX = e.touches[0].clientX;
      this.touchStartY = e.touches[0].clientY;
      this.touchStartTime = Date.now();
      this.isSwiping = false;
    },
    onTouchMove(e) {
      if (!this.showMobileNav || this.swipePages.length < 2) return;
      const dx = e.touches[0].clientX - this.touchStartX;
      const dy = e.touches[0].clientY - this.touchStartY;
      if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 15) {
        this.isSwiping = true;
        e.preventDefault();
      }
    },
    onTouchEnd(e) {
      if (!this.showMobileNav || !this.isSwiping) return;
      this.isSwiping = false;
      const dx = e.changedTouches[0].clientX - this.touchStartX;
      const dt = Date.now() - this.touchStartTime;
      if (Math.abs(dx) < 60 || dt > 500) return;
      const idx = this.currentSwipeIndex;
      if (idx === -1) return;
      if (dx < 0 && idx < this.swipePages.length - 1) {
        this.swipeDirection = "left";
        this.isSwiping = true;
        this.$router.push(this.swipePages[idx + 1]);
      } else if (dx > 0 && idx > 0) {
        this.swipeDirection = "right";
        this.isSwiping = true;
        this.$router.push(this.swipePages[idx - 1]);
      }
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
  min-height: 100dvh;
}
.app-header {
  background-color: #1a1a1a;
  padding: 16px 32px;
  padding-top: calc(16px + env(safe-area-inset-top));
  padding-left: max(32px, env(safe-area-inset-left));
  padding-right: max(32px, env(safe-area-inset-right));
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  color: #ffaa00;
  font-size: 20px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-decoration: none;
}
.app-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}
.nav-group {
  display: flex;
  align-items: center;
  gap: 16px;
}
.nav-fade-enter-active,
.nav-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.nav-fade-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}
.nav-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.28s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.28s ease;
  will-change: transform, opacity;
}
.slide-left-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-40px);
}
.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-40px);
}
.slide-right-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
.app-nav a {
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}
.nav-text-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
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
.btn-logout:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.theme-toggle {
  background: none;
  border: none;
  color: #b0b5b9;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: all 0.15s;
  line-height: 1;
}
.theme-toggle:hover {
  color: #ffaa00;
  background: rgba(255,170,0,0.1);
}
html.dark .theme-toggle { color: #94a3b8; }
html.dark .theme-toggle:hover { color: #ffaa00; }
.app-main {
  padding: 12px 20px;
  padding-left: max(20px, env(safe-area-inset-left));
  padding-right: max(20px, env(safe-area-inset-right));
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}

/* ===== PWA HEADER ===== */
.pwa-header {
  background-color: #1a1a1a;
  padding: 12px 16px;
  padding-top: calc(12px + env(safe-area-inset-top));
  display: flex;
  justify-content: center;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 50;
}
.pwa-header-title {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffaa00;
  font-weight: 900;
  font-size: 18px;
  text-transform: uppercase;
  letter-spacing: 1px;
  width: 100%;
}

/* ===== PWA MAIN & BOTTOM NAV ===== */
.pwa-main {
  padding: 12px 16px;
  padding-bottom: calc(90px + env(safe-area-inset-bottom));
}
.pwa-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #1a1a1a;
  display: flex;
  justify-content: flex-start;
  align-items: stretch;
  padding: 8px 8px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  z-index: 100;
  border-top: 1px solid rgba(255, 170, 0, 0.2);
  gap: 4px;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
  scrollbar-width: none;
}
.pwa-bottom-nav::-webkit-scrollbar {
  display: none;
}
.pwa-bottom-nav--centered {
  justify-content: space-evenly;
  overflow-x: visible;
}
.pwa-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: #8b9299;
  text-decoration: none;
  font-size: 9px;
  font-weight: 600;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 14px;
  border-radius: 8px;
  transition: color 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 52px;
}
.pwa-nav-item.active,
.pwa-nav-item:hover {
  color: #ffaa00;
}
.pwa-nav-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}
.pwa-nav-settings {
  cursor: default;
  position: relative;
  z-index: 110;
}
.pwa-nav-settings span {
  color: #8b9299;
}
.notif-badge-wrap {
  position: relative;
  display: inline-flex;
}
.notif-badge {
  position: absolute;
  top: -4px;
  right: -6px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 8px;
  background: #ffaa00;
  color: #1a1a1a;
  font-size: 9px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow: 0 0 0 2px #1a1a1a;
}
html.dark .pwa-bottom-nav {
  background: #0d1117;
}
html.dark .settings-panel {
  background: #1a1f2e;
}
html.dark .settings-section h4 {
  color: #64748b;
}
html.dark .settings-row {
  color: #e2e8f0;
}
html.dark .settings-section + .settings-section {
  border-top-color: #1e293b;
}
</style>
